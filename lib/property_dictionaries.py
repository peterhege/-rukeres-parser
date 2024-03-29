missing_keys = {}

DEFAULT_DICT = {
    'brand': 'Márka',
    'name': 'Név',
    'category': 'Kategória',
    'url': 'URL',
    'rating': 'Értékelés',
    'rating_count': 'Értékelések száma',
    'shop_name': 'Bolt',
    'shop_rating': 'Bolt értékelés',
    'shop_rating_count': 'Bolt értékelések száma',
    'price': 'Ár',
    'shipping': 'Szállítási díj',
    'calculated_rating': 'Ajánlás'
}

PHONE_DICT = {
    'design': 'Kialakítás',
    'sim_card': 'SIM kártya típusa',
    'cpu_type': 'Processzor típusa',
    'cpu_cores': 'Processzormagok száma',
    'cpu_speed': 'Processzor sebessége',
    'memory_size': 'RAM',
    'storage_size': 'Belső memória mérete',
    'storage_extend': 'Memória bővíthető',
    'sd_card_type': 'Memóriakártya típusa',
    'os': 'Operációs rendszer',
    'screen_count': 'Kijelzők száma',
    'screen_size': 'Kijelző mérete',
    'screen_resolution': 'Kijelző felbontása',
    'screen_technology': 'Kijelző technológia',
    'screen_type': 'Kijelző típusa',
    'screen_frequency': 'Képfrissítési frekvencia',
    'screen_other': 'Egyéb kijelző tulajdonságok',
    'camera_exists': 'Fényképező',
    'camera_front_exists': 'Előlapi kamera',
    'camera_front_resolution': 'Előlapi kamera felbontása',
    'camera_back_count': 'Hátlapi kamerák száma',
    'camera_back_1_resolution': 'Első hátlapi kamera felbontása',
    'camera_back_2_resolution': 'Második hátlapi kamera felbontása',
    'camera_back_3_resolution': 'Harmadik hátlapi kamera felbontása',
    'camera_back_4_resolution': 'Negyedik hátlapi kamera felbontása',
    'camera_auto_focus': 'Autofókusz',
    'camera_has_flash': 'Beépített vaku',
    'camera_has_retina_scan': 'Retina szkenner',
    'camera_has_lidar_scan': 'LiDAR szkenner',
    'camera_has_tof_sensor': 'ToF szenzor',
    'camera_has_video': 'Videofelvétel',
    'camera_max_video_resolution': 'Maximális video felbontás',
    'mp3': 'MP3 lejátszó',
    'video_player': 'Video lejátszás',
    'web_browser': 'Internet böngésző',
    'game': 'Játék',
    'network': 'Adatátvitel',
    'plugs': 'Csatlakozók',
    'network_connections': 'Hálózati kapcsolatok',
    'navigation': 'Navigáció',
    'sensors': 'Szenzorok',
    'battery_type': 'Akkumulátor típusa',
    'battery_capacity': 'Akkumulátor kapacitás',
    'battery_wire_performance': 'Vezetékes töltési teljesítmény',
    'battery_wireless': 'Vezeték nélküli töltés',
    'mms': 'MMS',
    'email': 'E-mail',
    'height': 'Hosszúság',
    'width': 'Szélesség',
    'thickness': 'Vastagság',
    'weight': 'Tömeg',
    'sim_card_dual': 'Dual SIM',
    'sim_card_tri': 'Tripla SIM',
    'dripproof': 'Cseppálló',
    'waterproof': 'Vízálló',
    'dustproof': 'Porálló',
    'shockproof': 'Ütésálló',
    'dictaphone': 'Diktafon',
    'calendar': 'Naptár',
    'alarm': 'Ébresztő',
    'calculator': 'Számológép',
    'handsfree': 'Kihangosítás',
    'radio_fm': 'FM rádió'
}

ROUTER_DICT = {
    "has_wifi": "Vezeték nélküli", "has_usb": "USB csatlakozó", "lan_port_count": "LAN portok száma",
    "lan_speed": "LAN sebesség", "wan_port_count": "WAN portok száma", "wan_speed": "WAN sebesség",
    "wifi_speed": "Wi-Fi sebesség", "frequency": "Működési frekvencia", "antenna_count": "Antennák száma",
    "wifi_standards": "Vezeték nélküli szabványok", "wep_encryption": "WEP titkosítás",
    "security_options": "Biztonsági lehetőségek"
}

PRINTER_DICT = {
    "type": "Nyomtató típusa", "is_colorful": "Színes nyomtató", "double_side": "Kétoldalas nyomtatás",
    "disk_printer": "CD/DVD nyomtatás",
    "pict_bridge": "Közvetlen nyomtatás (PictBridge)", "wifi_direct": "Wi-Fi Direct",
    "max_page_size": "Maximális papírméret",
    "resolution": "Felbontás (fekete-fehér)", "resolution_colorful": "Felbontás (színes)",
    "speed": "Nyomtatási sebesség (fekete-fehér, A4 méretben)",
    "speed_colorful": "Nyomtatási sebesség (színes, A4 méretben)", "has_usb": "USB", "parallel_port": "Párhuzamos port",
    "serial_prot": "Soros port", "fire_wire": "FireWire", "ethernet": "Ethernet", "wifi": "Wi-Fi", "width": "Szélesség",
    "height": "Magasság", "depth": "Mélység", "weight": "Tömeg", "capacity": "Lapadagoló kapacitása",
    "card_reader": "Kártyaolvasó", "noise": "Nyomtatási zajszint"
}

dictionaries = {'phone': PHONE_DICT, 'router': ROUTER_DICT, 'printer': PRINTER_DICT}


def dict_flip(d: dict) -> dict:
    nd = {}
    for key, value in d.items():
        if type(value) != list:
            value = [value]
        for v in value:
            nd[v] = key
    return nd


def dict_values(d: dict) -> dict:
    nd = {}
    for key, value in d.items():
        if type(value) != list:
            value = [value]
        nd[key] = value[0]
    return nd


def translate(i: dict, o: dict, d: str) -> dict:
    prop_dict = dict_flip(dictionaries[d])
    for key, value in i.items():
        if key in prop_dict:
            o[prop_dict[key]] = value
        else:
            if d not in missing_keys:
                missing_keys[d] = []
            if key in missing_keys[d]:
                continue
            missing_keys[d].append(key)
    return o
