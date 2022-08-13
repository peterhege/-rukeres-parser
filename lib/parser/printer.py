import re

for_rating = {
    'is_colorful': {'w': 1, 't': True},
    'double_side': {'w': 1, 't': True},
    'disk_printer': {'w': 1, 't': True},
    'pict_bridge': {'w': 1, 't': True},
    'wifi_direct': {'w': 1, 't': True},
    'max_page_size': {'w': 1, 't': False},
    'resolution': {'w': 1, 't': True},
    'resolution_colorful': {'w': 1, 't': True},
    'speed': {'w': 1, 't': True},
    'speed_colorful': {'w': 1, 't': True},
    'has_usb': {'w': 1, 't': True},
    'wifi': {'w': 2, 't': True},
    'weight': {'w': 1, 't': True},
    'capacity': {'w': 1, 't': True},
    'card_reader': {'w': 1, 't': True},
    'noise': {'w': 1, 't': True},
    'ethernet': {'w': 1, 't': True},
}


def parse(data: dict) -> dict:
    if 'double_side' in data:
        double_side_enum = ['nincs', 'manuális', 'automata']
        v = data['double_side'].lower()
        data['double_side'] = double_side_enum.index(v) if v in double_side_enum else 0
    if 'max_page_size' in data:
        found = re.search(r'[a-z]([0-9]+)', data['max_page_size'].lower())
        data['max_page_size'] = int(found.group(1)) if found else 0
    if 'resolution' in data:
        found = re.search(r'([0-9]+)\s*x\s*([0-9]+)', data['resolution'].lower())
        data['resolution'] = int(found.group(1)) * int(found.group(2)) if found else 0
    if 'resolution_colorful' in data:
        found = re.search(r'([0-9]+)\s*x\s*([0-9]+)', data['resolution_colorful'].lower())
        data['resolution_colorful'] = int(found.group(1)) * int(found.group(2)) if found else 0

    for key in ['noise', 'capacity', 'weight', 'speed_colorful', 'speed']:
        if key in data:
            found = re.search(r'(^[0-9]+(\.[0-9]+)?)', data[key])
            data[key] = float(found.group(1)) if found else 0

    return data
