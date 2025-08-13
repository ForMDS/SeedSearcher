设计思路：
第一，我想预测天气（weather），我希望知道在春季（spring）和夏季（summer）每一天的天气
第二，我想预测沙漠节（desert festival）的商人（vendor），有一些村民（villager）会随机来沙漠节出售物品，每天会有两个人，我想知道是哪两个人会来出售
第三，我想知道矿井混合宝箱（remixed rewards in mine chests）的内容
第四，我想预测春5（spring 5），也就是游戏第五天里，矿井（mines）的怪物层（Monster and slime infestations），也就是有一些层数有可能会变成怪物层，我想知道是哪几层
第五，我想预测春1（spring 1）和春2（spring 2），也就是游戏的第一天和第二天，星之果实餐吧（stardrop saloon）的垃圾桶（garbag can）里是否产生物品

---

正式：

运行方式：python app.py
所有参数在app.py中修改

使用ENABLE_FILTER可以开启/关闭筛选功能

种子筛选范围：
SEED_START / SEED_END

功能一：天气预测（已完成）
提供起始、结束日期（含）：START_DAY / END_DAY
需要预测的天气类型：TARGET_TYPES
最少天数：MIN_COUNT
例如：春1-春28，至少10个雨天

功能二：矿井怪物层预测（已完成）
提供起始、结束日期（含）：MINES_START_DAY / MINES_END_DAY
起始、结束层数（含）：FLOOR_START / FLOOR_END
可以筛掉有怪物层的种子
例：春5，要求1-90层没有怪物层

功能三：矿井混合宝箱（已完成）
提供筛选条件：CHEST_RULES
例：要求20层是磁铁戒指，且80是长柄锤或110是巨锤

功能四：沙漠节摆摊
判断莉亚（出售100硬木）且/或贾斯（出售魔法糖冰棍）是否来摆摊
提供筛选参数：REQUIRE_LEAH / REQUIRE_JAS 
研究发现，前面天数晚上睡觉的时间会导致存档时npc位置不同，影响后续npc列表和沙漠节商人选择。目前默认以凌晨2点睡觉的序列预测贾斯。
这是修bug之前（莉亚预测准确，贾斯和玛妮谢恩序列会改变所以不准确）：
https://chatgpt.com/share/689b3861-f358-800b-9b32-b29165e96267

功能五：垃圾桶
