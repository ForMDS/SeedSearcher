from flask import Blueprint, request, jsonify
from functions.weather import WeatherPredictor
from functions.mines import MinesPredictor
from functions.chests import ChestsPredictor
from functions.desert_festival import DesertFestivalPredictor
from functions.night_events import predict_night_event_for_day
from services.predict import (
    evaluate_weather_clauses,
    no_infested_in_range,
    collect_levels_from_rules,
    check_chest_rules_nested,
    evaluate_saloon_trash_range,
)
from config import (
    TARGET_TYPES, WEATHER_CLAUSES,
    MINES_START_DAY, MINES_END_DAY, FLOOR_START, FLOOR_END, REQUIRE_NO_INFESTED,
    CHEST_RULES_MODE, CHEST_RULES,
    REQUIRE_LEAH, REQUIRE_JAS,
    saloon_start_day, saloon_end_day, saloon_daily_luck, saloon_has_book, saloon_require_min_hit,
    NIGHT_CHECK_DAY, NIGHT_GREENHOUSE_UNLOCKED,
    USE_LEGACY,
)

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.post('/weather')
def api_weather():
    data = request.get_json() or {}
    seed = int(data.get('seed', 0))
    clauses = data.get('clauses', WEATHER_CLAUSES)
    targets = tuple(data.get('targets', TARGET_TYPES))
    wp = WeatherPredictor(game_id=seed, use_legacy=USE_LEGACY)
    ok, matched = evaluate_weather_clauses(wp, clauses, targets)
    return jsonify({
        'ok': bool(ok),
        'matched_days': [
            {
                'abs_day': d.abs_day,
                'season': d.season_en,
                'day': d.dom,
                'weather': d.weather_en,
                'weather_zh': d.weather_zh
            } for d in matched
        ]
    })

@bp.post('/mines')
def api_mines():
    data = request.get_json() or {}
    seed = int(data.get('seed', 0))
    start_day = int(data.get('start_day', MINES_START_DAY))
    end_day = int(data.get('end_day', MINES_END_DAY))
    floor_start = int(data.get('floor_start', FLOOR_START))
    floor_end = int(data.get('floor_end', FLOOR_END))
    require_no_infested = bool(data.get('require_no_infested', REQUIRE_NO_INFESTED))
    mp = MinesPredictor(game_id=seed, use_legacy=USE_LEGACY)
    if require_no_infested:
        ok, details = no_infested_in_range(mp, start_day, end_day, floor_start, floor_end)
    else:
        ok = True
        details = mp.predict_infested_in_range(start_day, end_day)
    return jsonify({
        'ok': bool(ok),
        'start_day': start_day,
        'end_day': end_day,
        'floor_start': floor_start,
        'floor_end': floor_end,
        'days': [
            {'abs_day': d.abs_day, 'floors': sorted(list(d.floors))} for d in details
        ]
    })

@bp.post('/chests/check')
def api_chests_check():
    data = request.get_json() or {}
    seed = int(data.get('seed', 0))
    mode = str(data.get('mode', CHEST_RULES_MODE))
    rules = data.get('rules', CHEST_RULES)
    cp = ChestsPredictor(game_id=seed, use_legacy=USE_LEGACY)
    ok, pred = check_chest_rules_nested(cp, rules, mode)
    items = []
    for lv in sorted(pred.keys()):
        can = pred[lv]
        display = None if can is None else cp.display_name(can)
        items.append({'level': lv, 'item': can, 'display': display})
    return jsonify({'ok': bool(ok), 'items': items, 'mode': mode})

@bp.post('/chests/predict')
def api_chests_predict():
    data = request.get_json() or {}
    seed = int(data.get('seed', 0))
    levels = data.get('levels', [])
    levels = sorted({int(x) for x in levels})
    cp = ChestsPredictor(game_id=seed, use_legacy=USE_LEGACY)
    pred = cp.predict_levels(levels)
    resp = []
    for lv in levels:
        can = pred.get(lv)
        display = None if can is None else cp.display_name(can)
        resp.append({'level': lv, 'item': can, 'display': display})
    return jsonify({'items': resp})

@bp.post('/desert')
def api_desert():
    data = request.get_json() or {}
    seed = int(data.get('seed', 0))
    require_leah = bool(data.get('require_leah', REQUIRE_LEAH))
    require_jas = bool(data.get('require_jas', REQUIRE_JAS))
    df = DesertFestivalPredictor(game_id=seed, use_legacy=USE_LEGACY, year=1, leo_moved=False, debug=False)
    res = df.vendors_for_three_days()
    v15, v16, v17 = res[0], res[1], res[2]
    has_leah = any('Leah' in vendors for vendors in (v15, v16, v17))
    has_jas = any('Jas' in vendors for vendors in (v15, v16, v17))
    ok = (not require_leah or has_leah) and (not require_jas or has_jas)
    return jsonify({'ok': bool(ok), 'vendors': {'春15': v15, '春16': v16, '春17': v17}, 'has_leah': has_leah, 'has_jas': has_jas})

@bp.post('/saloon_trash')
def api_saloon_trash():
    data = request.get_json() or {}
    seed = int(data.get('seed', 0))
    start_day = int(data.get('start_day', saloon_start_day))
    end_day = int(data.get('end_day', saloon_end_day))
    daily_luck = float(data.get('daily_luck', saloon_daily_luck))
    has_book = bool(data.get('has_garbage_book', saloon_has_book))
    require_min_hit = int(data.get('require_min_hit_days', saloon_require_min_hit))
    ok, tag, out = evaluate_saloon_trash_range(
        seed,
        start_day=start_day,
        end_day=end_day,
        daily_luck=daily_luck,
        has_garbage_book=has_book,
        daily_luck_by_day=None,
        require_min_hit_days=require_min_hit,
    )
    summary = out['summary']
    return jsonify({'ok': bool(ok), 'tag': tag, 'summary': summary})

@bp.post('/night_event')
def api_night_event():
    data = request.get_json() or {}
    seed = int(data.get('seed', 0))
    check_day = int(data.get('check_day', NIGHT_CHECK_DAY))
    greenhouse_unlocked = bool(data.get('greenhouse_unlocked', NIGHT_GREENHOUSE_UNLOCKED))
    ne = predict_night_event_for_day(
        seed,
        check_day,
        day_adjust=0,
        greenhouse_unlocked=greenhouse_unlocked,
    )
    return jsonify({
        'day': check_day,
        'event': getattr(ne, 'event', None),
        'is_fairy': getattr(ne, 'is_fairy', False),
    })

@bp.post('/search')
def api_search():
    """
    批量种子筛选接口：给定种子范围和筛选条件，返回满足所有条件的种子列表
    完全复制原 app.py 中的 worker 函数逻辑，包括动态排序和短路优化
    """
    data = request.get_json() or {}
    
    # 种子范围参数
    seed_start = int(data.get('seed_start', 0))
    seed_range = int(data.get('seed_range', 100))  # 默认只搜索100个，避免前端请求超时
    
    # 各功能的开关和参数
    enable_weather = bool(data.get('enable_weather', False))
    weather_clauses = data.get('weather_clauses', [])
    weather_targets = data.get('weather_targets', ['Rain', 'Storm', 'Green Rain'])
    
    enable_mines = bool(data.get('enable_mines', False))
    mines_start_day = int(data.get('mines_start_day', 5))
    mines_end_day = int(data.get('mines_end_day', 5))
    floor_start = int(data.get('floor_start', 1))
    floor_end = int(data.get('floor_end', 85))
    require_no_infested = bool(data.get('require_no_infested', True))
    
    enable_chests = bool(data.get('enable_chests', False))
    chest_rules_mode = str(data.get('chest_rules_mode', 'ALL'))
    chest_rules = data.get('chest_rules', [])
    
    enable_desert = bool(data.get('enable_desert', False))
    require_leah = bool(data.get('require_leah', False))
    require_jas = bool(data.get('require_jas', False))
    
    enable_saloon = bool(data.get('enable_saloon', False))
    saloon_start_day = int(data.get('saloon_start_day', 1))
    saloon_end_day = int(data.get('saloon_end_day', 2))
    saloon_daily_luck = float(data.get('saloon_daily_luck', -0.1))
    saloon_has_book = bool(data.get('saloon_has_book', False))
    saloon_require_min_hit = int(data.get('saloon_require_min_hit', 1))
    
    enable_night_event = bool(data.get('enable_night_event', False))
    night_check_day = int(data.get('night_check_day', 1))
    night_greenhouse_unlocked = bool(data.get('night_greenhouse_unlocked', False))
    
    use_legacy = bool(data.get('use_legacy', USE_LEGACY))
    
    # 改用原版 worker 函数逻辑 - 带动态成本估算和短路优化
    def search_worker(seed: int) -> dict:
        """
        完全复制 app.py 的 worker 函数，包括动态排序 + 短路优化
        """
        # 默认返回容器（短路时也能返回）
        matched = []
        mines_detail = []
        chests_detail = {}
        desert_detail = {}
        saloon_out = None
        saloon_tag = None
        saloon_ok = True
        night_detail = None
        night_ok = True

        tasks = []  # (name, cost_estimate, fn)

        # 夜间事件
        if enable_night_event:
            cost_night = 1
            def _eval_night():
                nonlocal night_detail, night_ok
                ne = predict_night_event_for_day(
                    seed,
                    night_check_day,
                    day_adjust=0,
                    greenhouse_unlocked=night_greenhouse_unlocked,
                )
                night_detail = ne
                night_ok = getattr(ne, 'is_fairy', False)
                return night_ok
            tasks.append(("night", cost_night, _eval_night))

        # 沙漠节
        if enable_desert:
            cost_desert = 3  # 固定 3 天
            def _eval_desert():
                nonlocal desert_detail
                ok = True
                df = DesertFestivalPredictor(
                    game_id=seed,
                    use_legacy=use_legacy,
                    year=1,
                    leo_moved=False,
                    debug=False
                )
                res = df.vendors_for_three_days()
                v15, v16, v17 = res[0], res[1], res[2]
                desert_detail = {"春15": v15, "春16": v16, "春17": v17}
                has_leah = any("Leah" in vendors for vendors in (v15, v16, v17))
                has_jas  = any("Jas"  in vendors for vendors in (v15, v16, v17))
                if require_leah and not has_leah:
                    ok = False
                if require_jas and not has_jas:
                    ok = False
                return ok
            tasks.append(("desert", cost_desert, _eval_desert))

        # 宝箱
        if enable_chests and chest_rules:
            unique_levels = len(collect_levels_from_rules(chest_rules))
            cost_chests = max(1, unique_levels)
            def _eval_chests():
                nonlocal chests_detail
                cp = ChestsPredictor(game_id=seed, use_legacy=use_legacy)
                ok, detail = check_chest_rules_nested(cp, chest_rules, chest_rules_mode)
                chests_detail = detail
                return ok
            tasks.append(("chests", cost_chests, _eval_chests))

        # 天气（多区间 AND）
        if enable_weather and weather_clauses:
            # 估算成本：所有子区间长度之和（更贴近实际）
            cost_weather = max(1, sum(int(c["end"]) - int(c["start"]) + 1 for c in weather_clauses))
            def _eval_weather():
                nonlocal matched
                wp = WeatherPredictor(game_id=seed, use_legacy=use_legacy)
                ok, matched_days = evaluate_weather_clauses(wp, weather_clauses, tuple(weather_targets))
                matched = matched_days
                return ok
            tasks.append(("weather", cost_weather, _eval_weather))

        # 垃圾桶
        if enable_saloon:
            span_saloon = max(0, saloon_end_day - saloon_start_day + 1)
            cost_saloon = max(1, span_saloon * 220)  # 经验系数
            def _eval_saloon():
                nonlocal saloon_out, saloon_tag, saloon_ok
                saloon_ok, saloon_tag, saloon_out = evaluate_saloon_trash_range(
                    seed,
                    start_day=saloon_start_day,
                    end_day=saloon_end_day,
                    daily_luck=saloon_daily_luck,
                    has_garbage_book=saloon_has_book,
                    daily_luck_by_day=None,
                    require_min_hit_days=saloon_require_min_hit,
                )
                return saloon_ok
            tasks.append(("saloon", cost_saloon, _eval_saloon))

        # 矿井
        if enable_mines:
            span_mines = max(0, mines_end_day - mines_start_day + 1)
            cost_mines = max(1, span_mines * 1000)  # 经验系数（相对最贵）
            def _eval_mines():
                nonlocal mines_detail
                mp = MinesPredictor(game_id=seed, use_legacy=use_legacy)
                if require_no_infested:
                    ok, mines_detail_local = no_infested_in_range(mp, mines_start_day, mines_end_day, floor_start, floor_end)
                    mines_detail = mines_detail_local
                    return ok
                else:
                    mines_detail = mp.predict_infested_in_range(mines_start_day, mines_end_day)
                    return True
            tasks.append(("mines", cost_mines, _eval_mines))

        # 没开任何功能 → 直接通过
        if not tasks:
            return {
                'seed': seed,
                'ok': True,
                'conditions_enabled': 0,
                'details': {}
            }

        # 动态排序 + 短路
        tasks.sort(key=lambda x: x[1])
        for task_name, _cost, fn in tasks:
            try:
                if not fn():
                    # 短路：第一个失败就返回
                    return {
                        'seed': seed,
                        'ok': False,
                        'failed_on': task_name,
                        'conditions_enabled': len(tasks),
                        'details': {}
                    }
            except Exception as e:
                return {
                    'seed': seed,
                    'ok': False,
                    'failed_on': task_name,
                    'error': str(e),
                    'conditions_enabled': len(tasks),
                    'details': {}
                }

        # 全部通过
        return {
            'seed': seed,
            'ok': True,
            'conditions_enabled': len(tasks),
            'details': {
                'weather': {'matched_count': len(matched)} if enable_weather else None,
                'mines': {'infested_days': len([d for d in mines_detail if d.floors])} if enable_mines else None,
                'chests': {'rules_count': len(chest_rules)} if enable_chests else None,
                'desert': {'vendors_days': len(desert_detail)} if enable_desert else None,
                'saloon': {'hit_days': saloon_out['summary'].get('dish_days_hit', 0) if saloon_out else 0} if enable_saloon else None,
                'night_event': {'event': getattr(night_detail, 'event', None) if night_detail else None} if enable_night_event else None,
            }
        }
    
    # 生成种子列表并批量处理
    seeds = list(range(seed_start, seed_start + seed_range + 1))
    
    # 简单的单线程处理（避免复杂度，前端可以控制范围）
    all_results = []
    hit_seeds = []
    
    for seed in seeds:
        result = search_worker(seed)
        all_results.append(result)
        if result['ok']:
            hit_seeds.append(seed)
    
    return jsonify({
        'seed_start': seed_start,
        'seed_range': seed_range,
        'total_checked': len(seeds),
        'hit_count': len(hit_seeds),
        'hit_seeds': hit_seeds,
        'conditions': {
            'weather': enable_weather,
            'mines': enable_mines,
            'chests': enable_chests,
            'desert': enable_desert,
            'saloon': enable_saloon,
            'night_event': enable_night_event
        },
        # 可选：返回前几个详细结果作为示例
        'sample_results': all_results[:5] if len(all_results) <= 50 else []
    })
