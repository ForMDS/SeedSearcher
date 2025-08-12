# app.py
import time
from functools import partial
from typing import Iterable, Tuple, List
from utils.scan_engine import run_scan
from functions.weather import WeatherPredictor, DayWeather
from functions.mines import MinesPredictor, DayInfested

# ========== 功能总开关 ==========
ENABLE_WEATHER_FILTER = True   # 关掉则不按天气筛选
ENABLE_MINES_FILTER   = True   # 关掉则不按怪物层筛选
# =================================

# ========= 天气筛选参数（仅在 ENABLE_WEATHER_FILTER=True 时生效） =========
SEED_START   = 0
SEED_END     = 100
START_DAY    = 6
END_DAY      = 7
TARGET_TYPES = ("Rain", "Storm", "Green Rain")
MIN_COUNT    = 1
# =====================================================================

# ========= 矿井筛选参数（仅在 ENABLE_MINES_FILTER=True 时生效） =========
MINES_START_DAY = 5     # 绝对天数
MINES_END_DAY   = 5
FLOOR_START     = 1
FLOOR_END       = 90
REQUIRE_NO_INFESTED = True  # True=要求“完全没有怪物/史莱姆层”
# =====================================================================

USE_LEGACY   = True
SHOW_DATES   = True
PROCESSES    = 0          # 0=auto
CHUNKSIZE    = 1000

# ---------- helper ----------
def match_days_in_range(wp: WeatherPredictor, start_day: int, end_day: int, targets: Tuple[str, ...]) -> List[DayWeather]:
    days = wp.predict_range(start_day, end_day)
    tset = set(targets)
    return [d for d in days if d.weather_en in tset]

def no_infested_in_range(mp: MinesPredictor, start_day: int, end_day: int, floor_start: int, floor_end: int) -> Tuple[bool, List[DayInfested]]:
    all_days = mp.predict_infested_in_range(start_day, end_day)
    ok = True
    for d in all_days:
        if any(floor_start <= f <= floor_end for f in d.floors):
            ok = False
            break
    return ok, all_days

def fmt_weather(days: List[DayWeather]) -> str:
    return "、".join([f"{d.season_en}{d.dom}({d.weather_zh})" for d in days])

def fmt_mines(details: List[DayInfested], floor_start: int, floor_end: int) -> str:
    parts = []
    for d in details:
        bad = sorted([f for f in d.floors if floor_start <= f <= floor_end])
        if bad:
            parts.append(f"Day{d.abs_day}: {bad}")
    return " | ".join(parts) if parts else "无"

# ---------- 顶层 worker（可被 pickle） ----------
def worker(
    seed: int,
    # weather
    enable_weather: bool, start_day: int, end_day: int, targets: Tuple[str, ...], min_count: int, use_legacy: bool,
    # mines
    enable_mines: bool, mines_start: int, mines_end: int, floor_start: int, floor_end: int, require_no_infested: bool,
):
    # 天气
    if enable_weather:
        wp = WeatherPredictor(game_id=seed, use_legacy=use_legacy)
        matched = match_days_in_range(wp, start_day, end_day, targets)
        weather_ok = len(matched) >= min_count
    else:
        matched = []
        weather_ok = True  # 不启用 => 视为通过

    # 矿井
    if enable_mines:
        mp = MinesPredictor(game_id=seed, use_legacy=use_legacy)
        if require_no_infested:
            mines_ok, mines_detail = no_infested_in_range(mp, mines_start, mines_end, floor_start, floor_end)
        else:
            mines_detail = mp.predict_infested_in_range(mines_start, mines_end)
            mines_ok = True  # 只展示，不作为筛选条件
    else:
        mines_detail = []
        mines_ok = True

    ok = weather_ok and mines_ok
    return seed, matched, mines_detail, ok

# ---------- main ----------
def main():
    seeds: Iterable[int] = range(SEED_START, SEED_END + 1)
    processes = None if PROCESSES == 0 else PROCESSES

    mp_worker = partial(
        worker,
        enable_weather=ENABLE_WEATHER_FILTER,
        start_day=START_DAY,
        end_day=END_DAY,
        targets=TARGET_TYPES,
        min_count=MIN_COUNT,
        use_legacy=USE_LEGACY,
        enable_mines=ENABLE_MINES_FILTER,
        mines_start=MINES_START_DAY,
        mines_end=MINES_END_DAY,
        floor_start=FLOOR_START,
        floor_end=FLOOR_END,
        require_no_infested=REQUIRE_NO_INFESTED,
    )

    t0 = time.time()
    results = run_scan(seeds, mp_worker, processes=processes, chunksize=CHUNKSIZE)
    elapsed = time.time() - t0

    hits = []
    for seed, matched, mines_detail, ok in results:
        if ok:
            hits.append(seed)
            print(f"命中种子 {seed}：", end="")
            tags = []
            if ENABLE_WEATHER_FILTER:
                tags.append(f"天气命中 {len(matched)} 天")
            if ENABLE_MINES_FILTER:
                if REQUIRE_NO_INFESTED:
                    tags.append(f"矿井[{MINES_START_DAY}-{MINES_END_DAY}]楼层[{FLOOR_START}-{FLOOR_END}]无怪物层")
                else:
                    tags.append("矿井筛选未启用或仅展示")
            print("；".join(tags) if tags else "（未启用任何筛选）")
            if SHOW_DATES:
                if ENABLE_WEATHER_FILTER:
                    print("  天气日期：", fmt_weather(matched) or "无")
                if ENABLE_MINES_FILTER and REQUIRE_NO_INFESTED:
                    print("  矿井异常：", fmt_mines(mines_detail, FLOOR_START, FLOOR_END))

    print("\n=== 总结 ===")
    print(f"扫描范围：{SEED_START}..{SEED_END}（共 {SEED_END - SEED_START + 1} 个种子）")
    if ENABLE_WEATHER_FILTER:
        print(f"天气区间：第 {START_DAY} 天 到 第 {END_DAY} 天；目标={', '.join(TARGET_TYPES)}；最少 {MIN_COUNT} 天")
    else:
        print("天气筛选：已关闭")
    if ENABLE_MINES_FILTER:
        extra = "且无怪物层" if REQUIRE_NO_INFESTED else "（仅展示，不作筛选）"
        print(f"矿井区间：第 {MINES_START_DAY} 天 到 第 {MINES_END_DAY} 天；楼层 {FLOOR_START}-{FLOOR_END} {extra}")
    else:
        print("矿井筛选：已关闭")
    print(f"命中数量：{len(hits)}")
    if hits:
        print("前几个命中：", hits[:20])
    print(f"总耗时：{elapsed:.2f} 秒，进程数：{processes or 'auto'}，chunksize={CHUNKSIZE}")

if __name__ == "__main__":
    main()
