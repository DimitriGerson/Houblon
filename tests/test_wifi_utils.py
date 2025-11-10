import wifi_utils

cfg_ap = {
    "ssid": "TestAP",
    "password": "12345678",
    "channel": 6,
    "hidden": False
}

cfg_sta = {
    "ssid": "HomeWifi",
    "password": "mypassword"
}

def test_disable_all_wifi():
    wifi_utils.disable_all_wifi()
    " Pas d'erreur = succès
    assert True

def test_start_ap_returns_wlan():
    ap = wifi_utils.start_ap(cfg_ap)
    assert ap is not None
    assert ap.active() is True
    assert ap.ifconfig()[0].startswith("192.")

def test_start_sta_returns_wlan():
    sta = wifi_utils.start_sta(cfg_sta)
    assert sta is not None
    assert sta.isconnected() is True
    assert sta.ifconfig()[0].startswith("192.")

def test_start_sta_fails_if_empty_ssid():
    sta = wifi_utils.start_sta({"ssid": "", "password": ""})
    assert sta is None
