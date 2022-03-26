import re

for_rating = {
    'has_wifi': {'w': 2, 't': True},
    'has_usb': {'w': 1, 't': True},
    'lan_port_count': {'w': 1, 't': True},
    'lan_speed': {'w': 2, 't': True},
    'wan_speed': {'w': 2, 't': True},
    'wifi_speed': {'w': 3, 't': True},
    'frequency': {'w': 1, 't': True},
    'antenna_count': {'w': 1, 't': True},
    'wifi_standards_for_rating': {'w': 2, 't': True},
}
units = {'t': 1 / 1000 ** 2, 'g': 1 / 1000, 'm': 1, 'k': 1000}
wifi_standards = ['802.11', '802.11a', '802.11b', '802.11g', '802.11y', '802.11n', '802.11ac', '802.11ax']


def parse(data: dict) -> dict:
    for key in ['lan_speed', 'wan_speed', 'wifi_speed']:
        if key in data:
            found = re.search(r'([0-9]+(\.[0-9]+)?)\s*([MGTk])bit/s$', data[key])
            if not found:
                print(key, 'parse error: {}'.format(data[key]))
                exit()
            data[key] = float(found.group(1))
            data[key] /= units[found.group(3).lower()]
    if 'wifi_standards' in data:
        if type(data['wifi_standards']) == str:
            data['wifi_standards'] = [data['wifi_standards']]
        data['wifi_standards_for_rating'] = 0
        for standard in data['wifi_standards']:
            data['wifi_standards_for_rating'] += data['wifi_standards'].index(standard)
    if 'frequency' in data:
        found = re.search(r'([0-9]+(\.[0-9]+)?)\s*GHz$', data['frequency'])
        if not found:
            print('frequency parse error: {}'.format(data[key]))
            exit()
        data['frequency'] = float(found.group(1))
    for key in ['lan_port_count', 'antenna_count']:
        if key in data:
            found = re.search(r'^([0-9]+(\.[0-9]+)?)', data[key])
            if found:
                data[key] = float(found.group(1))
    return data
