from functions.desert_festival import DesertFestivalPredictor

# seeds = [1, 42]
# seeds = [1602, 4211, 4479]
seeds = [7605]
for seed in seeds:


    dp = DesertFestivalPredictor(
        game_id=seed,
        use_legacy=True,
        year=1,
        leo_moved=False,
        debug=False
    )

    res = dp.leah_in_festival()

    print(f"种子：{seed}")

    for d, (has_leah, lst) in res.items():
        print(f"春{15+d} : {lst}")
