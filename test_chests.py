# test_chests.py
from functions.chests import ChestsPredictor

# ===== 参数 =====
SEED = 2           # 你要测试的种子
USE_LEGACY = True  # 是否开启 legacy random

# ===== 主程序 =====
cp = ChestsPredictor(game_id=SEED, use_legacy=USE_LEGACY)

# 矿井混合宝箱层数
CHEST_FLOORS = [10, 20, 50, 60, 80, 90, 110]

predicted = cp.predict_levels(CHEST_FLOORS)

print(f"种子 {SEED} 的宝箱预测：")
for floor in sorted(predicted.keys()):
    item_en = predicted[floor]
    if item_en is None:
        zh = "（非宝箱层）"
    else:
        zh = cp.display_name(item_en)  # 中文别名
    print(f"  第 {floor} 层: {item_en} / {zh}")
