# functions/weather.py
from dataclasses import dataclass
from typing import List, Literal, Tuple, Dict
from utils.dotnet_random import DotNetRandom
from utils.rng_wrappers import get_random_seed, get_hash_from_string

WeatherEN = Literal["Sun", "Rain", "Storm", "Wind", "Green Rain", "Festival"]
SEASON_EN = Literal["Spring", "Summer", "Fall", "Winter"]

WEATHER_ZH_MAP: Dict[str, str] = {
    "Sun": "晴", "Rain": "雨", "Storm": "雷暴", "Wind": "风", "Green Rain": "绿雨", "Festival": "节日",
}

FESTIVAL_MAP = {
    13:"Egg Festival", 24:"Flower Dance", 39:"Luau",
    48:"Trout Derby", 49:"Trout Derby", 56:"Moonlight Jellies",
    72:"Stardew Valley Fair", 83:"Spirit's Eve", 92:"Festival of Ice",
    96:"Squid Fest", 97:"Squid Fest",
    99:"Night Market", 100:"Night Market", 101:"Night Market",
    109:"Feast of the Winter Star",
}
FORCE_SUN_FESTIVALS = {13, 24, 72, 83, 92, 109}

@dataclass
class DayWeather:
    abs_day: int
    season_en: SEASON_EN
    dom: int
    year: int
    weather_en: WeatherEN
    weather_zh: str
    festival_name: str | None
    forced_sun: bool

class WeatherPredictor:
    def __init__(self, game_id: int, use_legacy: bool = True):
        self.game_id = int(game_id)
        self.use_legacy = bool(use_legacy)

    def _cs_random(self, seed: int) -> DotNetRandom:
        return DotNetRandom(seed)

    def _seed_rng(self, *seed_args: int) -> DotNetRandom:
        seed = get_random_seed(*seed_args, use_legacy=self.use_legacy)
        return self._cs_random(seed)

    @staticmethod
    def _season_of_month(m: int) -> SEASON_EN:
        return ("Spring", "Summer", "Fall", "Winter")[m % 4]

    def _green_rain_day_for_summer(self, year: int) -> int:
        rng = self._seed_rng(year * 777, self.game_id)
        return [5,6,7,14,15,16,18,23][rng.Next(8)]

    def _roll_one(self, day1: int) -> DayWeather:
        day = day1
        month = (day - 1) // 28
        season: SEASON_EN = self._season_of_month(month)
        dom = ((day - 1) % 28) + 1
        year = 1 + (day - 1) // 112
        d112 = day % 112

        if day in (1,2,4) or (day % 28) == 1:
            return DayWeather(day, season, dom, year, "Sun", WEATHER_ZH_MAP["Sun"], FESTIVAL_MAP.get(d112), d112 in FORCE_SUN_FESTIVALS)
        if day == 3:
            return DayWeather(day, season, dom, year, "Rain", WEATHER_ZH_MAP["Rain"], FESTIVAL_MAP.get(d112), False)

        festival_name = FESTIVAL_MAP.get(d112)
        if festival_name and d112 in FORCE_SUN_FESTIVALS:
            return DayWeather(day, season, dom, year, "Sun", WEATHER_ZH_MAP["Sun"], festival_name, True)

        if season in ("Spring", "Fall"):
            rng = self._seed_rng(get_hash_from_string("location_weather"), self.game_id, day - 1)
            w = "Rain" if rng.NextDouble() < 0.183 else "Sun"
            return DayWeather(day, season, dom, year, w, WEATHER_ZH_MAP[w], festival_name, False)

        if season == "Summer":
            gr = self._green_rain_day_for_summer(year)
            rng = self._seed_rng(day - 1, self.game_id // 2, get_hash_from_string("summer_rain_chance"))
            if dom == gr: w = "Green Rain"
            elif dom % 13 == 0: w = "Storm"
            else:
                rain_chance = 0.12 + 0.003*(dom - 1)
                w = "Rain" if rng.NextDouble() < rain_chance else "Sun"
            return DayWeather(day, season, dom, year, w, WEATHER_ZH_MAP[w], festival_name, False)

        # Winter 先占位（将来可扩展雪/风）
        return DayWeather(day, season, dom, year, "Sun", WEATHER_ZH_MAP["Sun"], festival_name, False)

    def predict_range(self, start_abs_day: int, end_abs_day: int) -> List[DayWeather]:
        if start_abs_day < 1 or end_abs_day < start_abs_day:
            raise ValueError("Invalid day range")
        return [self._roll_one(d) for d in range(start_abs_day, end_abs_day+1)]

    @staticmethod
    def count_weather(days: List[DayWeather], include_en: tuple[WeatherEN, ...]) -> int:
        s = set(include_en)
        return sum(1 for d in days if d.weather_en in s)

    @staticmethod
    def pretty_print(days: List[DayWeather]) -> None:
        for d in days:
            fest = f"（{d.festival_name}）" if d.festival_name else ""
            forced = "（强制晴）" if d.forced_sun else ""
            print(f"第{d.abs_day}天 / {d.season_en} {d.dom:02d}（第{d.year}年）: {d.weather_zh}{fest}{forced}")
