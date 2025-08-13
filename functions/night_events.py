# functions/night_events.py
# ------------------------------------------------------------
# Stardew Valley 1.6 夜间事件预测（按 mouseypounds JS）
# 需求：给定“白天 D”（春1=1），判断当晚是否为 Fairy。
# 说明：事件在次日早上 6:00 进行 roll，因此 RNG 用 (D + 1)。
# ------------------------------------------------------------
from dataclasses import dataclass
from typing import Dict, Any
from utils.dotnet_random import DotNetRandom
from utils.rng_wrappers import get_random_seed

@dataclass
class NightEventResult:
    day: int                 # 白天 D（春1=1）
    event: str               # "Fairy" / "Witch" / "Meteor" / "Stone Owl" / "Strange Capsule" / "None"
    is_fairy: bool
    debug: Dict[str, Any]

def predict_night_event_for_day(
    game_id: int,
    day_number: int,
    *,
    day_adjust: int = 0,
    greenhouse_unlocked: bool = False,
) -> NightEventResult:
    """
    1.6 逻辑（对齐 mouseypounds）：
      rng = CSRandom(getRandomSeed(day + 1 + dayAdjust, gameID / 2))
      预热：NextDouble() 执行 10 次
      之后：
        if greenhouse_unlocked: couldBeWindstorm = rng.NextDouble() < 0.1
        nextRoll = rng.NextDouble()
        if not greenhouse_unlocked: couldBeWindstorm = (nextRoll < 0.1)
        if nextRoll < 0.01 and (month%4) < 3: Fairy
        elif rng.NextDouble() < 0.01 and (day+1+dayAdjust) > 20: Witch
        elif rng.NextDouble() < 0.01 and (day+1+dayAdjust) > 5:  Meteor
        elif rng.NextDouble() < 0.005:                           Stone Owl
        elif rng.NextDouble() < 0.008 and year > 1:              Strange Capsule
        else: None
    """
    if day_number < 1:
        raise ValueError("day_number 必须 >= 1（春1=1）")

    # RNG 初始化（注意 gameID / 2 为浮点，get_random_seed 支持）
    day_for_rng = day_number + 1 + day_adjust
    seed = get_random_seed(day_for_rng, game_id / 2)
    rng = DotNetRandom(seed)

    # 预热 10 次
    for _ in range(10):
        rng.NextDouble()

    dbg: Dict[str, Any] = {"seed": seed, "day_for_rng": day_for_rng}

    # 风暴树（只影响风暴可能性提示，不影响 Fairy 判定）
    if greenhouse_unlocked:
        could_be_windstorm = rng.NextDouble() < 0.1
    else:
        could_be_windstorm = None  # 暂存，等 nextRoll 出来再赋值

    # 关键 roll 序列
    next_roll = rng.NextDouble()
    if greenhouse_unlocked is False:
        could_be_windstorm = next_roll < 0.1

    # 计算月/年（仅用于 Fairy 的季节判断与后续事件条件）
    # 春1..28 -> 月索引 0；夏29..56 -> 1；秋57..84 -> 2；冬85..112 -> 3 ...
    month_index = (day_number - 1) // 28
    year = 1 + (day_number - 1) // 112

    event = "None"
    # Fairy 只在春夏秋触发（month%4 < 3）
    if next_roll < 0.01 and (month_index % 4) < 3:
        event = "Fairy"
    elif rng.NextDouble() < 0.01 and day_for_rng > 20:
        event = "Witch"
    elif rng.NextDouble() < 0.01 and day_for_rng > 5:
        event = "Meteor"
    elif rng.NextDouble() < 0.005:
        event = "Stone Owl"
    elif rng.NextDouble() < 0.008 and year > 1:
        event = "Strange Capsule"

    dbg.update({
        "next_roll": next_roll,
        "month_index": month_index,
        "year": year,
        "could_be_windstorm": could_be_windstorm,
    })

    return NightEventResult(
        day=day_number,
        event=event,
        is_fairy=(event == "Fairy"),
        debug=dbg,
    )
