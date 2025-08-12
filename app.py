# app.py
import time
from functools import partial
from typing import Iterable, Tuple, List, Dict, Optional, Union, Set
from utils.scan_engine import run_scan
from functions.weather import WeatherPredictor, DayWeather
from functions.mines import MinesPredictor, DayInfested
from functions.chests import ChestsPredictor
from functions.desert_festival import DesertFestivalPredictor

# ========== 功能总开关 ==========
ENABLE_WEATHER_FILTER = True  # 天气
ENABLE_MINES_FILTER   = True  # 矿井怪物层
ENABLE_CHESTS_FILTER  = True  # 混合宝箱筛选
ENABLE_DESERT_FILTER  = True  # 沙漠节
# =================================

# ========= 天气筛选参数 =========
SEED_START   = 0
SEED_END     = 10000
START_DAY    = 6
END_DAY      = 7
TARGET_TYPES = ("Rain", "Storm", "Green Rain")
MIN_COUNT    = 1
# =====================================================================

# ========= 矿井筛选参数 =========
MINES_START_DAY = 5     # 绝对天数
MINES_END_DAY   = 5
FLOOR_START     = 1
FLOOR_END       = 90
REQUIRE_NO_INFESTED = True  # True=要求“完全没有怪物/史莱姆层”
# =====================================================================

# ========= 混合宝箱筛选参数（支持嵌套 OR）=========
# 顶层 CHEST_RULES_MODE:
#   "ALL": 所有顶层条件需满足；顶层元素如果是列表 -> 该列表内“任一项”满足即可
#   "ANY": 顶层任意一个条件满足即可；顶层元素如果是列表 -> 该列表内“任一项”满足即可
# 规则举例：
#   1) 20层=光辉戒指
#      CHEST_RULES = [(20, "光辉戒指")]
#   2) 20层=光辉戒指 且 (80层=长柄锤 或 110层=巨锤)
#      CHEST_RULES_MODE = "ALL"
#      CHEST_RULES = [ (20,"光辉戒指"), [ (80,"长柄锤"), (110,"巨锤") ] ]
ChestAtom = Tuple[int, str]
ChestGroup = List[ChestAtom]             # OR 组
ChestRule = Union[ChestAtom, ChestGroup] # 顶层元素：单条 或 OR 组

CHEST_RULES_MODE = "ALL"  # "ALL" 或 "ANY"
CHEST_RULES: List[ChestRule] = [
    # 示例：20层=磁铁戒指 且 (80层=长柄锤 或 110层=巨锤)
    (20, "磁铁戒指"),
    [(80, "长柄锤"), (110, "巨锤")],
]
# =====================================================================

# ========= 沙漠节筛选参数 =========
REQUIRE_LEAH = True  # 至少一天出现 Leah
REQUIRE_JAS  = True  # 至少一天出现 Jas
# =====================================================================

USE_LEGACY   = True
SHOW_DATES   = True
PROCESSES    = 0
CHUNKSIZE    = 1000

# ---------- helpers ----------
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

# ====== 宝箱（支持嵌套 OR）的工具函数 ======
def _collect_levels_from_rules(rules: List[ChestRule]) -> List[int]:
    levels: Set[int] = set()
    for rule in rules:
        if isinstance(rule, list):
            for lv, _ in rule:
                levels.add(lv)
        else:
            lv, _ = rule
            levels.add(lv)
    return sorted(levels)

def _normalize_rules(cp: ChestsPredictor, rules: List[ChestRule]) -> List[ChestRule]:
    norm: List[ChestRule] = []
    for rule in rules:
        if isinstance(rule, list):
            norm.append([(lv, cp.normalize_item(item)) for lv, item in rule])
        else:
            lv, item = rule
            norm.append((lv, cp.normalize_item(item)))
    return norm

def check_chest_rules_nested(cp: ChestsPredictor, rules: List[ChestRule], mode: str) -> Tuple[bool, Dict[int, Optional[str]]]:
    if not rules:
        return True, {}

    rules_norm = _normalize_rules(cp, rules)
    levels = _collect_levels_from_rules(rules_norm)
    pred = cp.predict_levels(levels)  # {level: canonical_en or None}

    def atom_ok(atom: ChestAtom) -> bool:
        lv, want = atom
        return pred.get(lv) == want

    def group_ok(group: ChestGroup) -> bool:
        return any(atom_ok(a) for a in group)

    satisfied_flags: List[bool] = []
    for elem in rules_norm:
        if isinstance(elem, list):
            satisfied_flags.append(group_ok(elem))
        else:
            satisfied_flags.append(atom_ok(elem))

    mode_u = mode.upper()
    if mode_u == "ANY":
        ok = any(satisfied_flags)
    else:
        ok = all(satisfied_flags)

    return ok, pred

def fmt_chests_human(cp: ChestsPredictor, details: Dict[int, Optional[str]]) -> str:
    pairs = []
    for lv in sorted(details.keys()):
        can = details[lv]
        if can is None:
            name = "（非宝箱层）"
        else:
            name = cp.display_name(can)
        pairs.append(f"L{lv}={name}")
    return ", ".join(pairs) if pairs else "无规则"

# ---------- 顶层 worker ----------
def worker(
    seed: int,
    # weather
    enable_weather: bool, start_day: int, end_day: int, targets: Tuple[str, ...], min_count: int, use_legacy: bool,
    # mines
    enable_mines: bool, mines_start: int, mines_end: int, floor_start: int, floor_end: int, require_no_infested: bool,
    # chests
    enable_chests: bool, chest_rules_mode: str, chest_rules: List[ChestRule],
    # desert festival
    enable_desert: bool, require_leah: bool, require_jas: bool,
):
    # 天气
    if enable_weather:
        wp = WeatherPredictor(game_id=seed, use_legacy=use_legacy)
        matched = match_days_in_range(wp, start_day, end_day, targets)
        weather_ok = len(matched) >= min_count
    else:
        matched = []
        weather_ok = True

    # 矿井
    if enable_mines:
        mp = MinesPredictor(game_id=seed, use_legacy=use_legacy)
        if require_no_infested:
            mines_ok, mines_detail = no_infested_in_range(mp, mines_start, mines_end, floor_start, floor_end)
        else:
            mines_detail = mp.predict_infested_in_range(mines_start, mines_end)
            mines_ok = True
    else:
        mines_detail = []
        mines_ok = True

    # 混合宝箱
    if enable_chests:
        cp = ChestsPredictor(game_id=seed, use_legacy=use_legacy)
        chests_ok, chests_detail = check_chest_rules_nested(cp, chest_rules, chest_rules_mode)
    else:
        chests_detail = {}
        chests_ok = True

    # ========== 沙漠节（第一年 春15/16/17）==========
    desert_ok = True
    desert_detail: Dict[str, List[str]] = {}
    if enable_desert:
        df = DesertFestivalPredictor(
            game_id=seed,
            use_legacy=use_legacy,
            year=1,
            leo_moved=False,
            debug=False
        )
        # {0:[v1,v2], 1:[v1,v2], 2:[v1,v2]}
        res = df.vendors_for_three_days()
        v15, v16, v17 = res[0], res[1], res[2]
        desert_detail = {"春15": v15, "春16": v16, "春17": v17}

        has_leah = any("Leah" in vendors for vendors in (v15, v16, v17))
        has_jas  = any("Jas"  in vendors for vendors in (v15, v16, v17))

        if require_leah and not has_leah:
            desert_ok = False
        if require_jas and not has_jas:
            desert_ok = False

    ok = weather_ok and mines_ok and chests_ok and desert_ok
    return seed, matched, mines_detail, chests_detail, desert_detail, ok

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
        enable_chests=ENABLE_CHESTS_FILTER,
        chest_rules_mode=CHEST_RULES_MODE,
        chest_rules=CHEST_RULES,
        enable_desert=ENABLE_DESERT_FILTER,
        require_leah=REQUIRE_LEAH,
        require_jas=REQUIRE_JAS,
    )

    t0 = time.time()
    results = run_scan(seeds, mp_worker, processes=processes, chunksize=CHUNKSIZE)
    elapsed = time.time() - t0

    hits = []
    for seed, matched, mines_detail, chests_detail, desert_detail, ok in results:
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
            if ENABLE_CHESTS_FILTER:
                tags.append("宝箱规则满足")
            if ENABLE_DESERT_FILTER:
                tags.append("沙漠节命中")
            print("；".join(tags) if tags else "（未启用任何筛选）")
            if SHOW_DATES:
                if ENABLE_WEATHER_FILTER:
                    print("  天气日期：", fmt_weather(matched) or "无")
                if ENABLE_MINES_FILTER and REQUIRE_NO_INFESTED:
                    print("  矿井异常：", fmt_mines(mines_detail, FLOOR_START, FLOOR_END))
                if ENABLE_CHESTS_FILTER:
                    cp_tmp = ChestsPredictor(game_id=seed, use_legacy=USE_LEGACY)
                    print("  宝箱掉落：", fmt_chests_human(cp_tmp, chests_detail))
                if ENABLE_DESERT_FILTER and desert_detail:
                    # 例：春15: [Leah, ...] | 春16: [...]
                    ds = " | ".join([f"{k}: {v}" for k, v in desert_detail.items()])
                    print("  沙漠节商人：", ds)

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
    if ENABLE_CHESTS_FILTER:
        print(f"宝箱筛选：模式={CHEST_RULES_MODE}，规则={CHEST_RULES or '（未写规则）'}")
    else:
        print("宝箱筛选：已关闭")
    if ENABLE_DESERT_FILTER:
        print(f"沙漠节筛选：莉亚={REQUIRE_LEAH}，贾斯={REQUIRE_JAS}")
    else:
        print("沙漠节筛选：已关闭")
    print(f"命中数量：{len(hits)}")
    if hits:
        print("前几个命中：", hits[:20])
    print(f"总耗时：{elapsed:.2f} 秒，进程数：{processes or 'auto'}，chunksize={CHUNKSIZE}")

if __name__ == "__main__":
    main()