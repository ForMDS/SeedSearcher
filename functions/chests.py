# functions/chests.py
from dataclasses import dataclass
from typing import Dict, Optional, List
from utils.rng_wrappers import get_random_seed
from utils.dotnet_random import DotNetRandom
from data.chests_data import CHOICES as CHEST_CHOICES, ALIASES as CHEST_ALIASES

@dataclass
class ChestReward:
    level: int
    item: Optional[str]  # 英文标准名

class ChestsPredictor:
    def __init__(self, game_id: int, use_legacy: bool = True):
        self.game_id = int(game_id)
        self.use_legacy = bool(use_legacy)

    # —— 数据访问（解耦代码与数据）——
    @property
    def choices(self) -> Dict[int, List[str]]:
        return CHEST_CHOICES

    @property
    def aliases(self) -> Dict[str, str]:
        return CHEST_ALIASES

    # —— RNG —— 
    def _rng_for_level(self, floor: int) -> DotNetRandom:
        seed = get_random_seed(self.game_id * 512, floor, use_legacy=self.use_legacy)
        return DotNetRandom(seed)

    # —— 名称归一/显示 —— 
    def _normalize_quotes(self, s: str) -> str:
        # 统一直/弯引号，去掉首尾空白
        return s.replace("’", "'").strip()

    def normalize_item(self, name: str) -> str:
        """别名→英文标准名；不在表中则返回清洗后的原值"""
        key = self._normalize_quotes(name)
        return self.aliases.get(key, key)

    def display_name(self, canonical: str) -> str:
        """英文标准名→中文友好名（若有），否则返回英文"""
        key = self._normalize_quotes(canonical)
        return self.aliases.get(key, key)

    # —— 预测 —— 
    def get_reward_for_level(self, floor: int) -> Optional[str]:
        """返回英文标准名；非宝箱层返回 None"""
        if floor not in self.choices:
            return None
        rng = self._rng_for_level(floor)
        pool = self.choices[floor]
        idx = rng.Next(len(pool))
        return pool[idx]

    def get_reward_name_for_level(self, floor: int) -> Optional[str]:
        can = self.get_reward_for_level(floor)
        if can is None:
            return None
        return self.display_name(can)

    def predict_levels(self, levels: List[int]) -> Dict[int, Optional[str]]:
        return {lv: self.get_reward_for_level(lv) for lv in levels}
