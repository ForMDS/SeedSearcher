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
