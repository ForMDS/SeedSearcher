# data/chests_data.py
# 统一维护：矿井混合宝箱（Remixed）掉落池 & 别名（中↔英）
# 注意：所有“标准名”使用英文；别名字典是双向映射（中文<->英文），含常见英文变体。

# 楼层掉落池（英文标准名）
CHOICES = {
    10: ["Leather Boots", "Work Boots", "Wooden Blade", "Iron Dirk", "Wind Spire", "Femur"],
    20: ["Steel Smallsword", "Wood Club", "Elf Blade", "Glow Ring", "Magnet Ring"],
    30: ["(No chest)"],
    40: ["Slingshot"],  # 早前示例的 Floor 40 实际是武器；保留 mouseypounds 列表结构
    50: ["Tundra Boots", "Thermal Boots", "Combat Boots", "Silver Saber", "Pirate's Sword"],
    60: ["Crystal Dagger", "Cutlass", "Iron Edge", "Burglar's Shank", "Wood Mallet"],
    70: ["Templar's Blade"],  # 与示例一致（单一掉落）
    80: ["Firewalker Boots", "Dark Boots", "Claymore", "Templar's Blade", "Kudgel", "Shadow Dagger"],
    90: ["Obsidian Edge", "Tempered Broadsword", "Wicked Kris", "Bone Sword", "Ossified Blade"],
    100: ["Stardrop"],
    110: ["Space Boots", "Crystal Shoes", "Steel Falchion", "The Slammer"],
    120: ["Skull Key"],
}

# 双向别名（中文<->英文标准名），以及常见英文变体（引号等）
ALIASES = {
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
    "Pirate’s Sword": "海盗剑",  # 弯引号变体

    # Floor 60
    "Crystal Dagger": "水晶匕首", "水晶匕首": "Crystal Dagger",
    "Cutlass": "弯刀", "弯刀": "Cutlass",
    "Iron Edge": "铁刃", "铁刃": "Iron Edge",
    "Burglar's Shank": "飞贼之胫", "Burglar’s Shank": "飞贼之胫", "飞贼之胫": "Burglar's Shank",
    "Wood Mallet": "木锤", "木锤": "Wood Mallet",

    # Floor 70
    "Templar's Blade": "圣堂之刃", "Templar’s Blade": "圣堂之刃", "圣堂之刃": "Templar's Blade",

    # Floor 80
    "Firewalker Boots": "蹈火者靴", "蹈火者靴": "Firewalker Boots",
    "Dark Boots": "黑暗之靴", "黑暗之靴": "Dark Boots",
    "Claymore": "双刃大剑", "双刃大剑": "Claymore",
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
