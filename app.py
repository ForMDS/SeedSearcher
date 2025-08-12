import time
from typing import Iterable
from utils.scan_engine import run_scan
from functions.weather import WeatherPredictor, DayWeather

# ======= 运行参数 =======
USE_LEGACY = True
SHOW_RAIN_DAYS = True

# 扫描种子范围
START_SEED = 0
END_SEED   = 99999
PROCESSES  = None        # None = 自动用所有CPU
CHUNKSIZE  = 1000

# 预测的天数范围（绝对天数：第1天=Spring 1 Year 1）
WEATHER_START_DAY = 1
WEATHER_END_DAY   = 28

# 你想匹配的天气类型（可以改为任何组合，比如 ("Rain", "Storm")）
TARGET_WEATHER = ("Rain", "Storm", "Green Rain")

# ========================

def count_weather_and_list(wp: WeatherPredictor, start_day: int, end_day: int, target: tuple[str, ...]):
    days = wp.predict_range(start_day, end_day)
    matched = [d for d in days if d.weather_en in target]
    return len(matched), matched

def weather_worker(seed: int):
    wp = WeatherPredictor(game_id=seed, use_legacy=USE_LEGACY)
    count, matched_days = count_weather_and_list(wp, WEATHER_START_DAY, WEATHER_END_DAY, TARGET_WEATHER)
    return seed, count, matched_days

def fmt_list(days: list[DayWeather]) -> str:
    return "、".join([f"{d.season_en}{d.dom}({d.weather_zh})" for d in days])

def main():
    seeds: Iterable[int] = range(START_SEED, END_SEED + 1)
    t0 = time.time()
    results = run_scan(seeds, weather_worker, processes=PROCESSES, chunksize=CHUNKSIZE)
    elapsed = time.time() - t0

    for seed, count, matched in results:
        if count > 0:  # 你可以改成 count >= X 作为条件
            print(f"种子 {seed}: 共有 {count} 天符合条件")
            if SHOW_RAIN_DAYS:
                print(f"  天数: {fmt_list(matched)}")

    print("\n=== 总结 ===")
    print(f"扫描范围：{START_SEED}..{END_SEED}（共 {END_SEED-START_SEED+1} 个种子）")
    print(f"总耗时：{elapsed:.2f} 秒，进程数：{PROCESSES or 'auto'}，chunksize={CHUNKSIZE}")

if __name__ == "__main__":
    main()
