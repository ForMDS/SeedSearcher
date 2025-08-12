# app.py
import time
from functools import partial
from typing import Iterable, Tuple, List
from utils.scan_engine import run_scan
from functions.weather import WeatherPredictor, DayWeather

# ========= 在这里改参数 =========
SEED_START   = 0
SEED_END     = 10
START_DAY    = 1
END_DAY      = 28
TARGET_TYPES = ("Rain", "Storm", "Green Rain")
MIN_COUNT    = 6
USE_LEGACY   = True
SHOW_DATES   = True
PROCESSES    = 0          # 0=auto
CHUNKSIZE    = 1000
# =================================

def match_days_in_range(wp: WeatherPredictor, start_day: int, end_day: int, targets: Tuple[str, ...]) -> List[DayWeather]:
    days = wp.predict_range(start_day, end_day)
    tset = set(targets)
    return [d for d in days if d.weather_en in tset]

# 顶层 worker，保证可被 pickle
def worker(seed: int, start_day: int, end_day: int, targets: Tuple[str, ...], use_legacy: bool):
    wp = WeatherPredictor(game_id=seed, use_legacy=use_legacy)
    matched = match_days_in_range(wp, start_day, end_day, targets)
    return seed, matched

def fmt_list(days: List[DayWeather]) -> str:
    return "、".join([f"{d.season_en}{d.dom}({d.weather_zh})" for d in days])

def main():
    seeds: Iterable[int] = range(SEED_START, SEED_END + 1)
    processes = None if PROCESSES == 0 else PROCESSES

    # 用 partial 绑定参数；注意 worker 是顶层函数 -> 可 pickle
    mp_worker = partial(
        worker,
        start_day=START_DAY,
        end_day=END_DAY,
        targets=TARGET_TYPES,
        use_legacy=USE_LEGACY,
    )

    t0 = time.time()
    results = run_scan(seeds, mp_worker, processes=processes, chunksize=CHUNKSIZE)
    elapsed = time.time() - t0

    hits = []
    for seed, matched in results:
        if len(matched) >= MIN_COUNT:
            hits.append(seed)
            print(f"命中种子 {seed}: 区间内命中 {len(matched)} 天")
            if SHOW_DATES:
                print("  日期：", fmt_list(matched) or "无")

    print("\n=== 总结 ===")
    print(f"扫描范围：{SEED_START}..{SEED_END}（共 {SEED_END - SEED_START + 1} 个种子）")
    print(f"区间：第 {START_DAY} 天 到 第 {END_DAY} 天")
    print(f"目标天气：{', '.join(TARGET_TYPES)}，最少 {MIN_COUNT} 天")
    print(f"命中数量：{len(hits)}")
    if hits:
        print("前几个命中：", hits[:20])
    print(f"总耗时：{elapsed:.2f} 秒，进程数：{processes or 'auto'}，chunksize={CHUNKSIZE}")

if __name__ == "__main__":
    main()
