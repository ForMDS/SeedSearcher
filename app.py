from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import time
from functools import partial
from typing import Iterable, Tuple, List, Dict, Optional, Union, Set
from utils.scan_engine import run_scan
from functions.weather import WeatherPredictor, DayWeather
from functions.mines import MinesPredictor, DayInfested
from functions.chests import ChestsPredictor
from functions.desert_festival import DesertFestivalPredictor
from functions.trashcans import predict_saloon_trash_in_range
from functions.night_events import predict_night_event_for_day


dist_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
app = Flask(__name__, static_folder=dist_path, template_folder=dist_path)

# 启用 CORS（仅开放 /api/* 路径），允许本地开发端口访问
_allowed_origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
CORS(
    app,
    resources={r"/api/*": {"origins": _allowed_origins}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "access-token"],
)

# 首页和静态资源
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# 天气预测 API
@app.route('/api/weather', methods=['POST'])
def api_weather():
    data = request.get_json()
    seed = data.get('seed', 0)
    clauses = data.get('clauses', WEATHER_CLAUSES)
    targets = tuple(data.get('targets', TARGET_TYPES))

    wp = WeatherPredictor(game_id=seed)
    ok, matched = evaluate_weather_clauses(wp, clauses, targets)

    result = {
        'ok': ok,
        'matched_days': [
            {
                'abs_day': d.abs_day,
                'season': d.season_en,
                'day': d.dom,
                'weather': d.weather_en,
                'weather_zh': d.weather_zh
            } for d in matched
        ]
    }
    return jsonify(result)

# ========== 功能总开关 ==========
ENABLE_WEATHER_FILTER = False  # 天气
ENABLE_MINES_FILTER   = False  # 矿井怪物层
ENABLE_CHESTS_FILTER  = False  # 混合宝箱筛选
ENABLE_DESERT_FILTER  = False  # 沙漠节
ENABLE_SALOON_FILTER = False   # 酒吧垃圾桶
ENABLE_NIGHT_EVENT_FILTER = False   # 夜间事件（仙子）

# ENABLE_WEATHER_FILTER = True  # 天气
# ENABLE_MINES_FILTER   = True  # 矿井怪物层
ENABLE_CHESTS_FILTER  = True  # 混合宝箱筛选
# ENABLE_DESERT_FILTER  = True  # 沙漠节
# ENABLE_SALOON_FILTER = True   # 酒吧垃圾桶
# ENABLE_NIGHT_EVENT_FILTER = True   # 夜间事件（仙子）
# =================================

# ========= 种子范围 =========
SEED_START = 0      # 从这里开始
SEED_RANGE = 500    # 共筛这么多个

# ========= 天气筛选参数（多区间规则）=========
TARGET_TYPES = ("Rain", "Storm", "Green Rain")  # 默认雨天类型集合

# 每条规则：start, end, min_count, 可选 targets（不写则用上面的 TARGET_TYPES）
WEATHER_CLAUSES: List[Dict] = [
    {"start": 7,  "end": 7,  "min_count": 1},                               
    {"start": 14, "end": 26, "min_count": 4},                               
    {"start": 30, "end": 27, "min_count": 10},                               
    # 还可以继续加：{"start": X, "end": Y, "min_count": Z, "targets": ("Rain","Storm")} # 从日期X到Y，至少Z天targets类型的天气
]
# =====================================================================

# =====================================================================

# ========= 矿井筛选参数 =========
MINES_START_DAY = 5     # 绝对天数
MINES_END_DAY   = 5
FLOOR_START     = 1
FLOOR_END       = 85
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

CHEST_RULES_MODE = "ALL"
CHEST_RULES: List[ChestRule] = [
    (20, "磁铁戒指"),
    [   # 这是一个 OR 组
        [ (80, "长柄锤"),   (110, "太空之靴") ],  # AND 子组 A
        [ (80, "蹈火者靴"), (110, "巨锤") ],      # AND 子组 B
    ],
]
# =====================================================================

# ========= 沙漠节筛选参数 =========
REQUIRE_LEAH = True  # 至少一天出现 Leah
REQUIRE_JAS  = True  # 至少一天出现 Jas
# =====================================================================

# ===== Saloon 垃圾桶（日期区间）示例集成：开始 =====
# 你可以把这些参数接到你的 GUI/CLI；这里先用演示值
saloon_start_day = 1               # 开始日期（春1 = 1）
saloon_end_day = 2                 # 结束日期
saloon_daily_luck = -0.1           # 统一运势（或使用 daily_luck_by_day 覆盖）
saloon_has_book = False            # 是否读过垃圾之书
saloon_require_min_hit = 1         # 至少命中 N 天才算通过


# ===== Saloon 垃圾桶（日期区间）示例集成：开始 =====
NIGHT_CHECK_DAY = 1                # 检查“春1”的夜间事件
NIGHT_GREENHOUSE_UNLOCKED = False  # 温室已修复？只影响风暴提示，不影响仙子判定
# =====================================================================

USE_LEGACY   = True
SHOW_DATES   = True
PROCESSES    = 0
CHUNKSIZE    = 1000

# ---------- helpers ----------

def evaluate_weather_clauses(
    wp: WeatherPredictor,
    clauses: List[Dict],
    default_targets: Tuple[str, ...]
) -> Tuple[bool, List[DayWeather]]:
    """
    逐条规则评估天气：
      - 每条 {start, end, min_count, targets?} 都必须满足
      - 返回 (ok_all, matched_union_days)
        * matched_union_days：把所有规则中命中的天（满足 targets 的日子）去重合并后按天排序
    为了少算 RNG，我们先算整段包络再筛。
    """
    if not clauses:
        return True, []

    # 计算包络区间
    mn = min(int(c["start"]) for c in clauses)
    mx = max(int(c["end"]) for c in clauses)
    all_days = wp.predict_range(mn, mx)  # List[DayWeather]，包含 mn..mx

    # 辅助索引：abs_day -> DayWeather
    by_day: Dict[int, DayWeather] = {d.abs_day: d for d in all_days}

    ok_all = True
    matched_union: Dict[int, DayWeather] = {}

    for c in clauses:
        s = int(c["start"]); e = int(c["end"]); need = int(c["min_count"])
        t = tuple(c.get("targets", default_targets))
        tset = set(t)

        # 当前规则命中天
        hits = []
        for day in range(s, e + 1):
            dw = by_day.get(day)
            if dw and dw.weather_en in tset:
                hits.append(dw)
                matched_union[dw.abs_day] = dw  # 合并去重

        if len(hits) < need:
            ok_all = False  # 任何一条不满足则整体不通过

    # 合并后的天按绝对日排序
    merged = [by_day[d] for d in sorted(matched_union.keys())]
    return ok_all, merged

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

    def walk(node):
        if isinstance(node, list):
            for x in node:
                walk(x)
        else:
            lv, _ = node
            levels.add(lv)

    for r in rules:
        walk(r)
    return sorted(levels)


def _normalize_rules(cp: ChestsPredictor, rules: List[ChestRule]) -> List[ChestRule]:
    def norm_node(node):
        if isinstance(node, list):
            return [norm_node(x) for x in node]  # 递归：OR 组或 AND 子组
        else:
            lv, item = node
            return (lv, cp.normalize_item(item))  # 中文/别名 → 规范英文
    return [norm_node(r) for r in rules]


def check_chest_rules_nested(cp: ChestsPredictor, rules: List[ChestRule], mode: str) -> Tuple[bool, Dict[int, Optional[str]]]:
    if not rules:
        return True, {}

    rules_norm = _normalize_rules(cp, rules)
    levels = _collect_levels_from_rules(rules_norm)
    pred = cp.predict_levels(levels)  # {level: canonical_en or None}

    def atom_ok(atom: ChestAtom) -> bool:
        lv, want = atom
        return pred.get(lv) == want

    def or_group_ok(group: List[Union[ChestAtom, List[ChestAtom]]]) -> bool:
        """
        OR 组：任一元素满足即可
          - 元素若为 atom：等价于 AND(单个)
          - 元素若为 List[atom]：视作 AND 子组（全部命中）
        """
        for elem in group:
            if isinstance(elem, list):          # AND 子组
                if all(atom_ok(a) for a in elem):
                    return True
            else:                               # 单个 atom
                if atom_ok(elem):
                    return True
        return False

    def eval_top(node) -> bool:
        if isinstance(node, list):             # OR 组
            return or_group_ok(node)
        else:                                   # 原子
            return atom_ok(node)

    flags = [eval_top(n) for n in rules_norm]
    ok = any(flags) if mode.upper() == "ANY" else all(flags)
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

def evaluate_saloon_trash_range(
    seed: int,
    *,
    start_day: int,
    end_day: int,
    daily_luck: float = -0.1,
    has_garbage_book: bool = False,
    daily_luck_by_day: dict | None = None,
    require_min_hit_days: int = 1,   # 范围内至少出现多少次 Dish 才算合格（默认≥1）
):
    """
    评估 [start_day, end_day] 范围内的“酒吧垃圾桶 DishOfTheDay”命中情况。
    只统计 source == 'DishOfTheDay' 的天数；其他掉落既不计入也不淘汰。

    返回: (ok, summary_text, detail_dict)
      - ok: Dish 命中天数 >= require_min_hit_days
      - summary_text: 如 "酒吧垃圾桶（Dish）命中 2/7 天（1,3）"
      - detail_dict["summary"] 包含 dish_days, dish_days_hit 等字段
    """
    out = predict_saloon_trash_in_range(
        seed,
        start_day,
        end_day,
        has_garbage_book=has_garbage_book,
        daily_luck=daily_luck,
        daily_luck_by_day=daily_luck_by_day,
    )
    results = out["results"]
    days_total = out["summary"]["days_total"]

    dish_days = [d for d in range(start_day, end_day + 1) if results[d].source == "DishOfTheDay"]
    dish_days_hit = len(dish_days)
    ok = dish_days_hit >= max(1, int(require_min_hit_days))

    if dish_days:
        hit_str = ",".join(str(d) for d in dish_days)
        tag = f"酒吧垃圾桶（Dish）命中 {dish_days_hit}/{days_total} 天（{hit_str}）"
    else:
        tag = f"酒吧垃圾桶（Dish）命中 0/{days_total} 天"

    out_ext = {
        "results": results,
        "summary": {
            **out["summary"],
            "dish_days": dish_days,
            "dish_days_hit": dish_days_hit,
            "require_min_hit_days": int(require_min_hit_days),
        }
    }
    return ok, tag, out_ext


# ---------- 顶层 worker ----------
def worker(
    seed: int,
    # weather
    enable_weather: bool, weather_clauses: List[Dict], targets: Tuple[str, ...], use_legacy: bool,
    # mines
    enable_mines: bool, mines_start: int, mines_end: int, floor_start: int, floor_end: int, require_no_infested: bool,
    # chests
    enable_chests: bool, chest_rules_mode: str, chest_rules: List[ChestRule],
    # desert festival
    enable_desert: bool, require_leah: bool, require_jas: bool,
):
    """
    动态估价 + 短路：
      - 将启用的功能封装为任务，估算成本并排序
      - 按成本从小到大执行；任一项失败立即返回
    返回结构保持不变。
    """
    # 默认返回容器（短路时也能返回）
    matched: List[DayWeather] = []
    mines_detail: List[DayInfested] = []
    chests_detail: Dict[int, Optional[str]] = {}
    desert_detail: Dict[str, List[str]] = {}
    saloon_out = None
    saloon_tag = None
    saloon_ok = True
    night_detail = None
    night_ok = True

    tasks = []  # (name, cost_estimate, fn)

    # 夜间事件
    if ENABLE_NIGHT_EVENT_FILTER:
        cost_night = 1
        def _eval_night():
            nonlocal night_detail, night_ok
            ne = predict_night_event_for_day(
                seed,
                NIGHT_CHECK_DAY,
                day_adjust=0,
                greenhouse_unlocked=NIGHT_GREENHOUSE_UNLOCKED,
            )
            night_detail = ne
            night_ok = ne.is_fairy
            return night_ok
        tasks.append(("night", cost_night, _eval_night))

    # 沙漠节
    if enable_desert:
        cost_desert = 3  # 固定 3 天
        def _eval_desert():
            nonlocal desert_detail
            ok = True
            df = DesertFestivalPredictor(
                game_id=seed,
                use_legacy=use_legacy,
                year=1,
                leo_moved=False,
                debug=False
            )
            res = df.vendors_for_three_days()
            v15, v16, v17 = res[0], res[1], res[2]
            desert_detail = {"春15": v15, "春16": v16, "春17": v17}
            has_leah = any("Leah" in vendors for vendors in (v15, v16, v17))
            has_jas  = any("Jas"  in vendors for vendors in (v15, v16, v17))
            if require_leah and not has_leah:
                ok = False
            if require_jas and not has_jas:
                ok = False
            return ok
        tasks.append(("desert", cost_desert, _eval_desert))

    # 宝箱
    if enable_chests:
        unique_levels = len(_collect_levels_from_rules(chest_rules))
        cost_chests = max(1, unique_levels)
        def _eval_chests():
            nonlocal chests_detail
            cp = ChestsPredictor(game_id=seed, use_legacy=use_legacy)
            ok, detail = check_chest_rules_nested(cp, chest_rules, chest_rules_mode)
            chests_detail = detail
            return ok
        tasks.append(("chests", cost_chests, _eval_chests))

    # 天气（多区间 AND）
    if enable_weather:
        # 估算成本：所有子区间长度之和（更贴近实际）
        cost_weather = max(1, sum(int(c["end"]) - int(c["start"]) + 1 for c in weather_clauses))
        def _eval_weather():
            nonlocal matched
            wp = WeatherPredictor(game_id=seed, use_legacy=use_legacy)
            ok, matched_days = evaluate_weather_clauses(wp, weather_clauses, targets)
            matched = matched_days
            return ok
        tasks.append(("weather", cost_weather, _eval_weather))

    # 垃圾桶
    if ENABLE_SALOON_FILTER:
        span_saloon = max(0, saloon_end_day - saloon_start_day + 1)
        cost_saloon = max(1, span_saloon * 220)  # 经验系数
        def _eval_saloon():
            nonlocal saloon_out, saloon_tag, saloon_ok
            saloon_ok, saloon_tag, saloon_out = evaluate_saloon_trash_range(
                seed,
                start_day=saloon_start_day,
                end_day=saloon_end_day,
                daily_luck=saloon_daily_luck,
                has_garbage_book=saloon_has_book,
                daily_luck_by_day=None,
                require_min_hit_days=saloon_require_min_hit,
            )
            return saloon_ok
        tasks.append(("saloon", cost_saloon, _eval_saloon))

    # 矿井
    if enable_mines:
        span_mines = max(0, mines_end - mines_start + 1)
        cost_mines = max(1, span_mines * 1000)  # 经验系数（相对最贵）
        def _eval_mines():
            nonlocal mines_detail
            mp = MinesPredictor(game_id=seed, use_legacy=use_legacy)
            if require_no_infested:
                ok, mines_detail_local = no_infested_in_range(mp, mines_start, mines_end, floor_start, floor_end)
                mines_detail = mines_detail_local
                return ok
            else:
                mines_detail = mp.predict_infested_in_range(mines_start, mines_end)
                return True
        tasks.append(("mines", cost_mines, _eval_mines))

    # 没开任何功能 → 直接通过
    if not tasks:
        ok = True
        return seed, matched, mines_detail, chests_detail, desert_detail, ok, saloon_out, saloon_tag, saloon_ok, night_detail, night_ok

    # 动态排序 + 短路
    tasks.sort(key=lambda x: x[1])
    for _name, _cost, fn in tasks:
        if not fn():
            ok = False
            return seed, matched, mines_detail, chests_detail, desert_detail, ok, saloon_out, saloon_tag, saloon_ok, night_detail, night_ok

    # 全部通过
    ok = True
    return seed, matched, mines_detail, chests_detail, desert_detail, ok, saloon_out, saloon_tag, saloon_ok, night_detail, night_ok


# ---------- main ----------
def main():
    seeds: Iterable[int] = range(SEED_START, SEED_START + SEED_RANGE + 1)
    processes = None if PROCESSES == 0 else PROCESSES

    mp_worker = partial(
        worker,
        enable_weather=ENABLE_WEATHER_FILTER,
        weather_clauses=WEATHER_CLAUSES,
        targets=TARGET_TYPES,
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
    for seed, matched, mines_detail, chests_detail, desert_detail, ok, saloon_out, saloon_tag, saloon_ok, night_detail, night_ok in results:
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
            if ENABLE_SALOON_FILTER and saloon_tag:
                tags.append(saloon_tag)
            if ENABLE_NIGHT_EVENT_FILTER and night_ok:
                tags.append(f"春{NIGHT_CHECK_DAY}夜=Fairy")

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
                    ds = " | ".join([f"{k}: {v}" for k, v in desert_detail.items()])
                    print("  沙漠节商人：", ds)
                if ENABLE_SALOON_FILTER and saloon_out:
                    s = saloon_out["summary"]
                    hit_days = s.get("dish_days", [])
                    hit_str = ",".join(map(str, hit_days)) if hit_days else "无"
                    print(f"  酒吧垃圾桶（Dish）：命中 {s.get('dish_days_hit', 0)}/{s['days_total']} 天；日期：{hit_str}")
                if ENABLE_NIGHT_EVENT_FILTER and night_detail is not None:
                    print(f"  夜间事件：春{NIGHT_CHECK_DAY}夜 -> {night_detail.event}")

    print(f"命中数量：{len(hits)}")
    if hits:
        print("前几个命中：", hits[:20])
    print(f"总耗时：{elapsed:.2f} 秒，进程数：{processes or 'auto'}，chunksize={CHUNKSIZE}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--flask":
        app.run(debug=True)
    else:
        main()
