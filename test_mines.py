# test_mines.py
from functions.mines import MinesPredictor

# ===== 修改这里进行测试 =====
SEED = 23456789             # uniqueIDForThisGame
USE_LEGACY = True    # 是否勾选“传统随机”
ABS_DAY = 5          # 绝对天数（Year1 春1 = 1，春5 = 5）
# ===========================

mp = MinesPredictor(game_id=SEED, use_legacy=USE_LEGACY)
floors = mp._infested_floors_for_day(ABS_DAY)

print(f"种子 {SEED}, 绝对天数 {ABS_DAY} 的怪物层楼层数：")
if floors:
    print(sorted(floors))
else:
    print("无怪物层")
