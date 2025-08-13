# test_night_event.py
from functions.night_events import predict_night_event_for_day

seeds = range(0, 1000)  # 自己改
check_day = 1               # 春1
greenhouse = False

for seed in seeds:
    res = predict_night_event_for_day(seed, check_day, greenhouse_unlocked=greenhouse)
    if res.is_fairy:
        print(f"种子 {seed}：春{check_day} 夜 = Fairy")
