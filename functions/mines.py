# functions/mines.py
# 矿井“怪物层 / 史莱姆层（Infested）”预测 —— 1.6+ 实现
from dataclasses import dataclass
from typing import List, Set
from utils.dotnet_random import DotNetRandom
from utils.rng_wrappers import get_random_seed

@dataclass
class DayInfested:
    abs_day: int        # 绝对天数（Year1 春1 = 1）
    floors: Set[int]    # 当天所有“怪物/史莱姆层”的楼层号（常规矿井 1..120）

class MinesPredictor:
    def __init__(self, game_id: int, use_legacy: bool = True):
        self.game_id = int(game_id)
        self.use_legacy = bool(use_legacy)

        # 与 mouseypounds 页面一致的假设（只按种子搜索时）：
        self.day_adjust = 0          # save.dayAdjust（页面里用到），新档情境用 0
        self.quarry_unlocked = False # save.quarryUnlocked，新档默认未解锁
        # 备注：1.5 移除了“被感染的采石场层”，但这不影响我们“无怪物层”的筛选

    def _cs_random(self, seed: int) -> DotNetRandom:
        return DotNetRandom(seed)  # legacy RNG（System.Random）

    def _seed_rng(self, *seed_args) -> DotNetRandom:
        seed = get_random_seed(*seed_args, use_legacy=self.use_legacy)
        return self._cs_random(seed)

    @staticmethod
    def _is_theme_window(level: int) -> bool:
        """mineLevel % 40 > 5 && < 30 && !== 19 才会判定为 Infested 候选"""
        mod = level % 40
        return (mod > 5) and (mod < 30) and (mod != 19)

    def _infested_floors_for_day(self, abs_day: int) -> Set[int]:
        """
        对应 mouseypounds 1.6 分支：
        rng = new CSRandom(getRandomSeed(day + save.dayAdjust, save.gameID/2, mineLevel*100))
        if (rng.NextDouble() < 0.044 && in theme window) -> Infested (Monster/Slime)
        """
        day = abs_day
        floors: Set[int] = set()

        for level in range(1, 120):  # 1..119
            if level % 5 == 0:
                continue  # 跳过电梯层
            # 1.6+ 的播种方式（注意 game_id / 2 是“浮点除法”，不能用 //）
            rng = self._seed_rng(day + self.day_adjust, self.game_id / 2, level * 100)

            if self._is_theme_window(level) and rng.NextDouble() < 0.044:
                # 第二次 NextDouble() 仅用于 Monster/Slime 分类，这里我们二者都算“怪物层”
                # rng.NextDouble() < 0.5 -> Monster，否则 Slime（不影响我们集合里是否收录）
                _ = rng.NextDouble()
                floors.add(level)
                continue

            # 1.6 分支还会判断“quarryLevel”，但与你的“无怪物层”筛选无关，这里可以忽略
            # if rng.NextDouble() < 0.044 and self.quarry_unlocked and (level % 40 > 1):
            #     pass  # 我们不将其计入怪物层集合

            # 之后还有蘑菇层/光照等检查，与“是否怪物层”无关，省略

        return floors

    # 对外：在给定绝对天数范围内，按天返回结果
    def predict_infested_in_range(self, start_abs_day: int, end_abs_day: int) -> List[DayInfested]:
        if start_abs_day < 1 or end_abs_day < start_abs_day:
            raise ValueError("Invalid day range")
        out: List[DayInfested] = []
        for d in range(start_abs_day, end_abs_day + 1):
            floors = self._infested_floors_for_day(d)
            out.append(DayInfested(abs_day=d, floors=floors))
        return out
