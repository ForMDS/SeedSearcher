# functions/chests.py
# 矿井混合宝箱（Remixed Mine Chest Rewards）— 1.6 逻辑 + 双语别名
from dataclasses import dataclass
from typing import Dict, Optional, List
from utils.rng_wrappers import get_random_seed
from utils.dotnet_random import DotNetRandom

@dataclass
class ChestReward:
    level: int
    item: Optional[str]  # 标准名（英文），如 "Leather Boots" / "Stardrop"

class ChestsPredictor:
    """
    - CHOICES 使用“英文标准名”作为内部唯一标识
    - ALIASES 提供“中文 ↔ 英文（标准名）”双向映射，以及一些英文变体（引号差异等）
    - normalize_item() 会把任意别名（中文/英文）归一到英文标准名
    - get_reward_name_for_level() 返回“易读名”（优先中文；没有中文就回退英文）
    """

    # ===== 候选表（按楼层；条目使用“英文标准名”）=====
    CHOICES: Dict[int, List[str]] = {
        10: [
            "Leather Boots",
            "Work Boots",
            "Wooden Blade",
            "Iron Dirk",
            "Wind Spire",
            "Femur",
        ],
        20: [
            "Steel Smallsword",
            "Wood Club",
            "Elf Blade",
            "Glow Ring",
            "Magnet Ring",
        ],
        30: ["(No chest)"],
        50: [
            "Tundra Boots",
            "Thermal Boots",
            "Combat Boots",
            "Silver Saber",
            "Pirate's Sword",
        ],
        60: [
            "Crystal Dagger",
            "Cutlass",
            "Iron Edge",
            "Burglar's Shank",
            "Wood Mallet",
        ],
        80: [
            "Firewalker Boots",
            "Dark Boots",
            "Claymore",
            "Templar's Blade",
            "Kudgel",
            "Shadow Dagger",
        ],
        90: [
            "Obsidian Edge",
            "Tempered Broadsword",
            "Wicked Kris",
            "Bone Sword",
            "Ossified Blade",
        ],
        100: ["Stardrop"],
        110: [
            "Space Boots",
            "Crystal Shoes",
            "Steel Falchion",
            "The Slammer",
        ],
        120: ["Skull Key"],
    }

    # ===== 双向别名（中文 ↔ 英文标准名），以及常见英文变体 =====
    ALIASES: Dict[str, str] = {
        # Floor 10
        "Leather Boots": "皮靴", "皮靴": "Leather Boots",
        "Work Boots": "工作靴", "工作靴": "Work Boots",
        "Wooden Blade": "木剑", "木剑": "Wooden Blade",
        "Iron Dirk": "铁制短剑", "铁制短剑": "Iron Dirk",
        "Wind Spire": "疾风利剑", "疾风利剑": "Wind Spire",
        "Femur": "股骨", "股骨": "Femur",

        # Floor 20
        "Steel Smallsword": "钢制轻剑", "钢制轻剑": "Steel Smallsword",
        "Wood Club": "木棒", "木棒": "Wood Club",
        "Elf Blade": "精灵之刃", "精灵之刃": "Elf Blade",
        "Glow Ring": "光辉戒指", "光辉戒指": "Glow Ring",
        "Magnet Ring": "磁铁戒指", "磁铁戒指": "Magnet Ring",

        # Floor 50
        "Tundra Boots": "冻土靴", "冻土靴": "Tundra Boots",
        "Thermal Boots": "热能靴", "热能靴": "Thermal Boots",
        "Combat Boots": "战靴", "战靴": "Combat Boots",
        "Silver Saber": "镀银军刀", "镀银军刀": "Silver Saber",
        "Pirate's Sword": "海盗剑", "海盗剑": "Pirate's Sword",
        "Pirate’s Sword": "海盗剑",  # 兼容弯引号
        "海盗剑": "Pirate's Sword",

        # Floor 60
        "Crystal Dagger": "水晶匕首", "水晶匕首": "Crystal Dagger",
        "Cutlass": "弯刀", "弯刀": "Cutlass",
        "Iron Edge": "铁刃", "铁刃": "Iron Edge",
        "Burglar's Shank": "飞贼之胫", "Burglar’s Shank": "飞贼之胫",
        "飞贼之胫": "Burglar's Shank",
        "Wood Mallet": "木锤", "木锤": "Wood Mallet",

        # Floor 80
        "Firewalker Boots": "蹈火者靴", "蹈火者靴": "Firewalker Boots",
        "Dark Boots": "黑暗之靴", "黑暗之靴": "Dark Boots",
        "Claymore": "双刃大剑", "双刃大剑": "Claymore",
        "Templar's Blade": "圣堂之刃", "Templar’s Blade": "圣堂之刃",
        "圣堂之刃": "Templar's Blade",
        "Kudgel": "长柄锤", "长柄锤": "Kudgel",
        "Shadow Dagger": "暗影匕首", "暗影匕首": "Shadow Dagger",

        # Floor 90
        "Obsidian Edge": "黑曜石之刃", "黑曜石之刃": "Obsidian Edge",
        "Tempered Broadsword": "淬火阔剑", "淬火阔剑": "Tempered Broadsword",
        "Wicked Kris": "蛇形邪剑", "蛇形邪剑": "Wicked Kris",
        "Bone Sword": "骨剑", "骨剑": "Bone Sword",
        "Ossified Blade": "骨化剑", "骨化剑": "Ossified Blade",

        # Floor 110
        "Space Boots": "太空之靴", "太空之靴": "Space Boots",
        "Crystal Shoes": "水晶鞋", "水晶鞋": "Crystal Shoes",
        "Steel Falchion": "钢刀", "钢刀": "Steel Falchion",
        "The Slammer": "巨锤", "巨锤": "The Slammer",

        # Specials
        "Stardrop": "星之果实", "星之果实": "Stardrop",
        "Skull Key": "骷髅钥匙", "骷髅钥匙": "Skull Key",
        "(No chest)": "（无宝箱）", "（无宝箱）": "(No chest)",
    }

    def __init__(self, game_id: int, use_legacy: bool = True):
        self.game_id = int(game_id)
        self.use_legacy = bool(use_legacy)

    def _rng_for_level(self, floor: int) -> DotNetRandom:
        # 1.6+: seed = get_random_seed(game_id * 512, floor)
        seed = get_random_seed(self.game_id * 512, floor, use_legacy=self.use_legacy)
        return DotNetRandom(seed)

    def normalize_item(self, item: str) -> str:
        """把任意中文/英文别名统一成英文标准名；若不在表中则原样返回"""
        return self.ALIASES.get(item, item)

    def display_name(self, canonical: str) -> str:
        """把英文标准名转为优先中文的显示名；若无中文映射则原样英文"""
        return self.ALIASES.get(canonical, canonical)

    def get_reward_for_level(self, floor: int) -> Optional[str]:
        """返回英文标准名；非宝箱层（不在 CHOICES）则返回 None"""
        if floor not in self.CHOICES:
            return None
        rng = self._rng_for_level(floor)
        choices = self.CHOICES[floor]
        idx = rng.Next(len(choices))
        return choices[idx]

    def get_reward_name_for_level(self, floor: int) -> Optional[str]:
        """返回友好显示名（中文优先）"""
        tag = self.get_reward_for_level(floor)
        if tag is None:
            return None
        return self.display_name(tag)

    def predict_levels(self, levels: List[int]) -> Dict[int, Optional[str]]:
        """批量预测：返回 {楼层: 英文标准名或 None}"""
        return {lv: self.get_reward_for_level(lv) for lv in levels}
