from functions.desert_festival import DesertFestivalPredictor

SEED = 4211

dp = DesertFestivalPredictor(SEED, use_legacy=True, year=1, leo_moved=False, debug=False)
res = dp.leah_in_festival()
for d, (has_leah, lst) in res.items():
    print(f"春{15+d} -> {lst} | 是否有Leah: {has_leah}")
