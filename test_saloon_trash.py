from functions.trashcans import predict_saloon_trash_in_range

# 待测种子
seeds = [7605]

# 日期范围
start_day = 1
end_day = 20

# 统一运势 & 是否读垃圾书
daily_luck = -0.1
has_garbage_book = False

for seed in seeds:
    out = predict_saloon_trash_in_range(
        seed,
        start_day,
        end_day,
        has_garbage_book=has_garbage_book,
        daily_luck=daily_luck,
    )

    results = out["results"]
    dish_days = []
    for day in range(start_day, end_day + 1):
        r = results[day]
        if r.source == "DishOfTheDay":
            dish_days.append(day)

    print(f"种子：{seed} ；日期范围：{start_day}-{end_day}；运势={daily_luck}；垃圾书={has_garbage_book}")


    # 判定（Dish-only）
    if not dish_days:
        print("没有符合的日期")
    else:
        print(f"符合日期：{dish_days}")
