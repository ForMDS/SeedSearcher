# functions/trashcans.py
# ------------------------------------------------------------
# Stardew 1.6 垃圾桶预测（Saloon）：
# - 支持任意游戏日 day>=1
# - 提供区间预测接口：predict_saloon_trash_in_range(start_day, end_day)
# - 种子推导与预热严格对齐 mouseypounds 1.6 逻辑
# ------------------------------------------------------------
from dataclasses import dataclass
from typing import Optional, Dict, Any

from utils.dotnet_random import DotNetRandom
from utils.rng_wrappers import get_random_seed, get_hash_from_string

_CAN_ID_SALOON = "Saloon"               # canID[5] = "Saloon"
_KEY_SALOON_DISH = "garbage_saloon_dish"

@dataclass
class TrashResult:
    day: int                # 游戏日（>=1）
    has_item: bool          # 是否有掉落（任意物品）
    source: str             # 命中来源：DishOfTheDay / Fallback / QiBean / None
    debug: Dict[str, Any]   # 调试信息

def _init_main_rng(game_id: int, day_number: int, day_adjust: int) -> DotNetRandom:
    """
    JS 1.6：
    seed = getRandomSeed(day + save.dayAdjust, save.gameID / 2, 777 + getHashFromString(canID[whichCan]))
    这里仅针对 Saloon（whichCan=5）。
    """
    a = day_number + day_adjust
    b = game_id / 2          # JS 是除以 2（得到浮点），你的 get_random_seed 支持浮点参与
    c = 777 + get_hash_from_string(_CAN_ID_SALOON)
    seed = get_random_seed(a, b, c)
    return DotNetRandom(seed)

def _prewarm_rng(rng: DotNetRandom) -> Dict[str, Any]:
    """
    按 JS：预热两次
      prewarm = rng.Next(0,100); burn NextDouble() prewarm 次
      再重复一遍
    """
    dbg = {}
    pre1 = rng.Next(0, 100)
    for _ in range(pre1):
        rng.NextDouble()
    pre2 = rng.Next(0, 100)
    for _ in range(pre2):
        rng.NextDouble()
    dbg["prewarm_counts"] = (pre1, pre2)
    return dbg

def _init_synced_rng_for_saloon_dish(game_id: int, day_number: int, day_adjust: int) -> DotNetRandom:
    """
    JS：
    new CSRandom(getRandomSeed(getHashFromString("garbage_saloon_dish"), save.gameID, day + save.dayAdjust))
    """
    a = get_hash_from_string(_KEY_SALOON_DISH)
    b = game_id
    c = day_number + day_adjust
    seed = get_random_seed(a, b, c)
    return DotNetRandom(seed)

def _predict_saloon_drop_day_1_6(
    game_id: int,
    day_number: int,
    *,
    daily_luck: float = -0.1,
    has_garbage_book: bool = False,
    day_adjust: int = 0,
    trash_cans_checked_total: int = 0,
    qi_crops_active: bool = False,
    theater_unlocked: bool = False,   # 暂未用到，但保留以便后续扩展“Joja 影院”等逻辑
    cc_complete: bool = False,        # 同上
) -> TrashResult:
    """
    复刻 mouseypounds 在 1.6 分支的流程，但只关心：
      - 是否“有掉落”（任意物品 True）
      - 仅 Saloon 垃圾桶（whichCan=5）
    """
    if day_number < 1:
        raise ValueError("day_number 必须为 >= 1 的正整数游戏日。")

    # base 概率 = 0.2 + dailyLuck；读过垃圾书再 +0.2
    luck_check = 0.2 + daily_luck
    if has_garbage_book:
        luck_check += 0.2

    # 主 RNG & 预热
    main_rng = _init_main_rng(game_id, day_number, day_adjust)
    dbg = _prewarm_rng(main_rng)

    source = "None"
    has_item = False

    # 齐豆优先（第一年默认 False）
    if qi_crops_active and main_rng.NextDouble() < 0.25:
        has_item = True
        source = "QiBean"
    else:
        # 基础通过判定
        base_chance_passed = (main_rng.NextDouble() < luck_check)

        if base_chance_passed:
            # Saloon 专属：Dish of the Day（独立同步 RNG）
            dish_rng = _init_synced_rng_for_saloon_dish(game_id, day_number, day_adjust)
            if dish_rng.NextDouble() < (0.2 + daily_luck):
                has_item = True
                source = "DishOfTheDay"
            else:
                # 专属未命中 → 进入 AfterAll fallback（仍算出物品）
                has_item = True
                source = "Fallback"
        else:
            # base 未通过；春初默认不会触发 mega/doubleMega，所以视为无掉落
            has_item = False
            source = "None"

    dbg.update({
        "luck_check": luck_check,
        "daily_luck": daily_luck,
        "has_garbage_book": has_garbage_book,
        "day_adjust": day_adjust,
        "trash_cans_checked_total": trash_cans_checked_total,
        "qi_crops_active": qi_crops_active,
        "base_roll": "passed" if (source != "None") else "failed",
        "source": source,
    })

    return TrashResult(
        day=day_number,
        has_item=has_item,
        source=source,
        debug=dbg,
    )

# === 对外 API ===============================================

def predict_saloon_trash_spring_day(
    game_seed_or_game_id: int,
    day_number: int,
    *,
    daily_luck: float = -0.1,
    has_garbage_book: bool = False,
) -> TrashResult:
    """
    预测指定游戏日的“酒吧垃圾桶是否有掉落”（任意物品）。
    - day_number: >=1（春1=1，春2=2，……）
    - daily_luck: 当日运势（典型 -0.1..0.1），默认 -0.1
    - has_garbage_book: 是否已读垃圾书（默认 False）
    """
    return _predict_saloon_drop_day_1_6(
        game_id=game_seed_or_game_id,
        day_number=day_number,
        daily_luck=daily_luck,
        has_garbage_book=has_garbage_book,
    )

def predict_saloon_trash_spring_1_and_2(
    game_seed_or_game_id: int,
    *,
    daily_luck_day1: float = -0.1,
    daily_luck_day2: float = -0.1,
    has_garbage_book: bool = False,
) -> Dict[int, TrashResult]:
    """
    便捷：返回春 1 与 春 2 的预测。
    """
    return {
        1: predict_saloon_trash_spring_day(
            game_seed_or_game_id, 1, daily_luck=daily_luck_day1, has_garbage_book=has_garbage_book
        ),
        2: predict_saloon_trash_spring_day(
            game_seed_or_game_id, 2, daily_luck=daily_luck_day2, has_garbage_book=has_garbage_book
        ),
    }

def predict_saloon_trash_in_range(
    game_seed_or_game_id: int,
    start_day: int,
    end_day: int,
    *,
    has_garbage_book: bool = False,
    daily_luck: float = -0.1,
    daily_luck_by_day: Optional[Dict[int, float]] = None,
) -> Dict[str, Any]:
    """
    在 [start_day, end_day]（含端点）的日期范围内，预测“酒吧垃圾桶是否出物品”。

    参数：
      - game_seed_or_game_id: 世界种子 / gameID
      - start_day, end_day: 正整数游戏日（春1=1）
      - has_garbage_book: 是否已读垃圾书（默认 False）
      - daily_luck: 统一运势（默认 -0.1）
      - daily_luck_by_day: 可选按天运势覆盖，如 {1:-0.05, 2:0.0}

    返回：
      {
        "results": {day: TrashResult, ...},
        "summary": {
           "days_total": int,
           "days_hit": int,
           "hit_days": List[int]
        }
      }
    """
    if start_day < 1 or end_day < 1:
        raise ValueError("start_day 和 end_day 必须为 >= 1 的正整数。")
    if end_day < start_day:
        start_day, end_day = end_day, start_day

    results: Dict[int, TrashResult] = {}
    hit_days = []
    luck_map = daily_luck_by_day or {}

    for day in range(start_day, end_day + 1):
        luck = luck_map.get(day, daily_luck)
        res = _predict_saloon_drop_day_1_6(
            game_id=game_seed_or_game_id,
            day_number=day,
            daily_luck=luck,
            has_garbage_book=has_garbage_book,
        )
        results[day] = res
        if res.has_item:
            hit_days.append(day)

    return {
        "results": results,
        "summary": {
            "days_total": end_day - start_day + 1,
            "days_hit": len(hit_days),
            "hit_days": hit_days,
        }
    }
