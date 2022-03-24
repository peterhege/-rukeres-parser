import re

for_rating = {
    'cpu_cores': {'w': 1, 't': True},
    'cpu_speed': {'w': 1, 't': True},
    'memory_size': {'w': 1, 't': True},
    'storage_size': {'w': 1, 't': True},
    'storage_extend': {'w': 1, 't': True},
    'screen_resolution_for_rating': {'w': 1, 't': True},
    'screen_technology_for_rating': {'w': 1, 't': True},
    'camera_front_resolution': {'w': 1, 't': True},
    'camera_back_1_resolution': {'w': 1, 't': True},
    'camera_back_2_resolution': {'w': 1, 't': True},
    'camera_back_3_resolution': {'w': 1, 't': True},
    'camera_back_4_resolution': {'w': 1, 't': True},
    'camera_back_count': {'w': 1, 't': True},
    'battery_capacity': {'w': 1, 't': True},
    'battery_wire_performance': {'w': 1, 't': True},
}
units = {'t': True / 1000, 'g': 1, 'm': 1000, 'k': 1000 ** 2}


def parse(data: dict) -> dict:
    for key in ['cpu_cores', 'cpu_speed', 'memory_size', 'storage_size']:
        if key in data:
            found = re.search(r'([0-9]+(\.[0-9]+)?)\s+(\w+)', data[key])
            if found:
                data[key] = float(found.group(1)) if found.group(2) else int(found.group(1))
                if re.match(r'[gmkt](b|hz)', found.group(3).lower()):
                    unit = re.sub(r'b|hz', '', found.group(3).lower())
                    data[key] /= units[unit]
    if 'screen_resolution' in data:
        found = re.search(r'[0-9]+\s?x\s?([0-9]+)', data['screen_resolution'])
        if found:
            data['screen_resolution_for_rating'] = int(found.group(1))
    if 'screen_technology' in data:
        data['screen_technology_for_rating'] = 1 if data['screen_technology'].lower() == 'oled' else 0
    if 'camera_back_count' in data:
        data['camera_back_count'] = int(data['camera_back_count'])
    for key in ['camera_front_resolution', 'camera_back_1_resolution', 'camera_back_2_resolution',
                'camera_back_3_resolution', 'camera_back_4_resolution']:
        if key in data:
            found = re.search(r'^([0-9]+(\.[0-9]+)?)', data[key])
            if found:
                data[key] = float(found.group(1))
    for key in ['battery_capacity', 'battery_wire_performance']:
        if key in data:
            found = re.search(r'^([0-9]+)', data[key])
            if found:
                data[key] = int(found.group(1))

    return data
