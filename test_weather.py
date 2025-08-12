# test_weather.py
from functions.weather import WeatherPredictor, DayWeather
from utils.rng_wrappers import get_hash_from_string

game_id = 123456
use_legacy = True
start_day = 1
end_day = 28

# 打印两个哈希常量，确认是否与 JS 一致（应为 -1513201250 与 -309161378）
print("hash('location_weather') =", get_hash_from_string("location_weather"))
print("hash('summer_rain_chance') =", get_hash_from_string("summer_rain_chance"))

wp = WeatherPredictor(game_id=game_id, use_legacy=use_legacy)
days: list[DayWeather] = wp.predict_range(start_day, end_day)

print(f"\nSeed/GameID={game_id} 春 {start_day}-{end_day} 天气：")
for d in days:
    print(f"春{d.dom:02d}  {d.weather_zh}")

rainy = [d.dom for d in days if d.weather_en in {"Rain", "Storm", "Green Rain"}]
print("\n雨天：", rainy)
