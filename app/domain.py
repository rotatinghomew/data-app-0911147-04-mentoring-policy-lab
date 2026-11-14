from collections import Counter
from statistics import mean


def mature_trial(data):
    output = []
    seen = set()
    for row in data['trial']:
        identity = (row['student_id'], row['period'])
        if identity in seen:
            raise ValueError('重复试点记录')
        seen.add(identity)
        probabilities = row['propensities']
        if abs(sum(probabilities.values()) - 1) > 1e-9 or any(value < 0 for value in probabilities.values()):
            raise ValueError('邀请概率不合法')
        if probabilities.get(row['invited_arm'], 0) <= 0:
            raise ValueError('实际邀请没有随机化支持')
        if row['outcome_available_at'] <= data['cutoff'] and row['outcome'] is not None:
            output.append(row)
    return output


def baseline(data):
    rows = mature_trial(data)
    arms = sorted(data['capacity']['slot_cost'])
    return {'mature': len(rows), 'pending': len(data['trial']) - len(rows),
            'invited_counts': dict(Counter(row['invited_arm'] for row in rows)),
            'raw_means': {arm: mean(row['outcome'] for row in rows if row['invited_arm'] == arm)
                          if any(row['invited_arm'] == arm for row in rows) else None for arm in arms}}


def act(data, request):
    if request.get('operation') != 'draft':
        raise ValueError('未知分配操作')
    slots = request.get('slots')
    arm = request.get('arm')
    if not isinstance(slots, int) or slots < 0 or arm not in data['capacity']['slot_cost']:
        raise ValueError('名额或邀请方式不合法')
    candidates = [row for row in data['eligibility'] if arm in row['eligible_arms']]
    candidates.sort(key=lambda row: (row['baseline_score'], row['student_id']))
    cost = data['capacity']['slot_cost'][arm]
    affordable = int(data['capacity']['budget'] // cost) if cost else len(candidates)
    selected = candidates[:min(slots, affordable)]
    return {'arm': arm, 'students': [row['student_id'] for row in selected],
            'cost': len(selected) * cost, 'rule': 'baseline_score_ascending',
            'notice': '现行分配规则，不声明增量效果'}
