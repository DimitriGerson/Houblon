import sys, os, types, pytest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
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
    # Pas d'erreur = succès
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

def make_fake_iface(active_state=True, connected=False, ip="192.168.4.1"):
    """créer un faux objet WLAN simulant une interface AP/STA."""
    iface = MagicMock()
    iface._active = active_state
    iface.active.side_effect = lambda *args: (
        setattr(iface, "_active", args[0]) or None if len(args) == 1 else iface._active
    )
    iface.isconnected.return_value = connected
    iface.ifconfig.return_value = (ip, "255.255.255.0", "192.168.4.1", "8.8.8.8")
    return iface

def test_disable_all_wifi_deactivates_interfaces(monkeypatch):
    """Teste la désactivation des interfaces actives."""
    # création de deux fausses interfaces
    fake_sta = MagicMock()
    fake_ap = MagicMock()
    
    # Fonction side_effect qui renvoie True quand appelée sans argument,
    # et change l'état quand appelée avec un booléen
    def active_side_effect(*args):
        if len(args) == 0:
            return True
        else:
            return None

    fake_sta.active.side_effect = active_side_effect
    fake_ap.active.side_effect = active_side_effect
    
    # WLAN doit renvoyer successivement STA puis AP
    fake_WLAN = MagicMock(side_effect=[fake_sta, fake_ap])

    monkeypatch.setattr(wifi_utils, "network", types.SimpleNamespace(
        STA_IF=0, AP_IF=1, WLAN=fake_WLAN
    ))
    monkeypatch.setattr(wifi_utils, "boot", types.SimpleNamespace(log=MagicMock()))
    
    wifi_utils.disable_all_wifi()
    
    # Vérifie que chaque interface a été désactivée
    fake_sta.active.assert_any_call(False)
    fake_ap.active.assert_any_call(False)

def test_start_ap_eventually_becomes_active(monkeypatch):
    """Teste que start_ap retourne l'objet AP quand il devient actif après quelques boucles."""
    fake_ap = MagicMock()
    calls = {"reads": 0}
    
    def fake_active(*args):
        # Lecture de l'état (active())
        if len(args) == 0:
            calls["reads"] += 1
            # Devient actif après 3 lectures
            return calls["reads"] > 3
        # Ecriture (active(True) ou active(False))
        return None

    fake_ap.active.side_effect = fake_active
    fake_ap.ifconfig.return_value = ("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8")

    # Ici : WLAN renvoie toujours le même fake_ap
    fake_WLAN = MagicMock(return_value=fake_ap)
    monkeypatch.setattr(wifi_utils, "network", types.SimpleNamespace(
        AP_IF=1,
        STA_IF=0,
        WLAN=fake_WLAN,
        AUTH_WPA_WPA2_PSK=3
    ),)
    monkeypatch.setattr(wifi_utils, "boot", types.SimpleNamespace(log=MagicMock()),)
    
    result = wifi_utils.start_ap({"ssid": "TestAP", "password": "12345678"})
    assert result is fake_ap
    assert result.active() is True

def test_esp_mode_true(monkeypatch):
    """Force _ESP_MODE=True et vérifie qu'on utilise bien network (pas network_mock)."""
    real_network = types.SimpleNamespace(WLAN=MagicMock(), STA_IF=0, AP_IF=1, AUTH_WPA_WPA2_PSK=3)
    with patch.dict(sys.modules, {"network": real_network}):
        import importlib
        import wifi_utils as w
        importlib.reload(w) # recharge pour forcer le chemin try/except
        assert w._ESP_MODE is True
        assert hasattr(w.network, "WLAN")
def test_start_ap_fails_after_timeout(monkeypatch):
    """Teste que start_ap retourne None et loggue un échec si l'AP n'active jamais."""
    
    # --- 1) Créer un faux AP qui ne devient jamais actif ---
    fake_ap = MagicMock()
    fake_ap.active.return_value = False
    fake_ap.ifconfig.return_value = ("0.0.0.0", "", "", "")
    
    # WLAN() renvoie toujours ce fake_ap
    fake_WLAN = MagicMock(return_value=fake_ap)

    # --- 2) Mock network + boot.log ---
    fake_log = MagicMock()

    monkeypatch.setattr(
        wifi_utils, "network",
        types.SimpleNamespace(
            AP_IF=1,
            STA_IF=0,
            WLAN=fake_WLAN,
            AUTH_WPA_WPA2_PSK=3
        )
    )
    monkeypatch.setattr(wifi_utils, "boot", types.SimpleNamespace(log=fake_log))

    # --- 3) Mock time.sleep pour accélérer le test ---
    monkeypatch.setattr(wifi_utils, "time", types.SimpleNamespace(sleep=lambda x: None))

    # --- 4) Appeler start_ap ---
    result = wifi_utils.start_ap({"ssid": "TestAP", "password": "12345678"})

    # --- 5) Assertions ---
    assert result is None                        # La fonction doit échouer
    fake_log.assert_called_with("Echec de l'activation du point d'accès.")
