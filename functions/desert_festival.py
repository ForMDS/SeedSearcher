from typing import Dict, List, Tuple
from utils.dotnet_random import DotNetRandom
from utils.rng_wrappers import get_random_seed
from data.characters_order import CHARACTERS_IN_ORDER

class DesertFestivalPredictor:
    # 来自 mouseypounds / 游戏：有资格成为沙漠节商人的角色集合
    POSSIBLE_VENDORS = {
        'Abigail','Caroline','Clint','Demetrius','Elliott','Emily','Evelyn','George',
        'Gus','Haley','Harvey','Jas','Jodi','Alex','Kent','Leah','Marnie','Maru',
        'Pam','Penny','Pierre','Robin','Sam','Sebastian','Shane','Vincent','Leo'
    }

    # 每日排除（春15/16/17 -> d=0/1/2）
    SCHEDULE_EXCLUSION: Dict[int, set] = {
        0: {'Abigail','Caroline','Elliott','Gus','Alex','Leah','Pierre','Sam','Sebastian','Haley'},
        1: {'Haley','Clint','Demetrius','Maru','Pam','Penny','Robin','Leo'},
        2: {'Evelyn','George','Jas','Jodi','Kent','Marnie','Shane','Vincent'},
    }

    def __init__(self, game_id: int, use_legacy: bool = True, year: int = 1, leo_moved: bool = False, debug: bool = False):
        self.game_id   = int(game_id)
        self.use_legacy = bool(use_legacy)
        self.year      = int(year)
        self.leo_moved = bool(leo_moved)
        self.debug     = bool(debug)
        # 固定顺序（来自 save.characters），不要排序
        self.characters_in_order: List[str] = list(CHARACTERS_IN_ORDER)

    def _rng(self, day_abs: int) -> DotNetRandom:
        # 传统随机 + 整数除法 gameID//2
        seed = get_random_seed(day_abs, self.game_id / 2, use_legacy=self.use_legacy)
        return DotNetRandom(seed)

    def _build_pool_for_day(self, d: int) -> List[str]:
        pool: List[str] = []
        exc = self.SCHEDULE_EXCLUSION[d]
        for name in self.characters_in_order:
            if name not in self.POSSIBLE_VENDORS:
                continue
            if name in exc:
                continue
            if name == 'Kent' and self.year < 2:
                continue
            if name == 'Leo' and not self.leo_moved:
                continue
            pool.append(name)
        if self.debug:
            print(f"[DEBUG] 春{15+d} vendorPool: {pool}")
        return pool

    def vendors_for_three_days(self) -> Dict[int, List[str]]:
        vendors: Dict[int, List[str]] = {0: [], 1: [], 2: []}
        for d in range(3):  # 0→春15, 1→春16, 2→春17
            day_abs = 15 + d
            pool = self._build_pool_for_day(d)
            rng = self._rng(day_abs)

            # 先移除 2*d 个（跨日不重复）
            for _ in range(d):
                for __ in range(2):
                    idx = rng.Next(len(pool))
                    if self.debug:
                        print(f"[DEBUG] 春{15+d} 预移除 idx={idx}, {pool[idx]}")
                    pool.pop(idx)

            # 当天抽 2 人
            for __ in range(2):
                idx = rng.Next(len(pool))
                pick = pool.pop(idx)
                if self.debug:
                    print(f"[DEBUG] 春{15+d} 选择 idx={idx}, {pick}")
                vendors[d].append(pick)
        return vendors

    def leah_in_festival(self) -> Dict[int, Tuple[bool, List[str]]]:
        vmap = self.vendors_for_three_days()
        return {d: ('Leah' in vmap[d], vmap[d]) for d in range(3)}

    def jas_in_festival(self) -> Dict[int, Tuple[bool, List[str]]]:
        vmap = self.vendors_for_three_days()
        return {d: ('Jas' in vmap[d], vmap[d]) for d in range(3)}
