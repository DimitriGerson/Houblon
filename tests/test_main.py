import pytest
from unittest.mock import MagicMock, patch
import main

# empêche les vrais reset()
main.machine.reset = MagicMock()

@pytest.fixture
def fake_boot(monkeypatch):
    boot = MagicMock()
    monkeypatch.setattr(main, "boot", boot)
    return boot

@pytest.fixture
def fake_wifi(monkeypatch):
    wifi = MagicMock()
    monkeypatch.setattr(main, "wifi_utils", wifi)
    return wifi

@pytest.fixture
def fake_server(monkeypatch):
    srv = MagicMock()
    monkeypatch.setattr(main, "start_server", srv)
    return srv

def test_main_mode_ap_ok(fake_boot, fake_wifi, fake_server, monkeypatch):
    fake_boot.load_config.return_value = {
        "mode": "AP",
        "ap": {"ssid": "test", "password": "1234"}
    }

    fake_wifi.start_ap.return_value = MagicMock()

    # Patch sleep pour que le test soit rapide
    monkeypatch.setattr(main.time, "sleep", lambda x: None)

    main.main()

    fake_wifi.start_ap.assert_called_once()
    fake_server.assert_called_once()
    fake_boot.log.assert_any_call("Point d'accès actif, lancement du server web...")

def test_main_mode_ap_fail(fake_boot, fake_wifi, fake_server, monkeypatch):
    fake_boot.load_config.return_value = {
        "mode": "AP",
        "ap": {}
    }

    fake_wifi.start_ap.return_value = None

    with patch.object(main, "safe_restart") as restart:
        main.main()
        restart.assert_called_once()

def test_main_sta_ok(fake_boot, fake_wifi, fake_server):
    fake_boot.load_config.return_value = {
        "mode": "STA",
        "sta": {},
        "ap": {}
    }

    fake_wifi.start_sta.return_value = MagicMock()

    main.main()

    fake_wifi.start_sta.assert_called_once()
    fake_server.assert_called_once()
    fake_boot.log.assert_any_call("Connexion STA réussie.")

def test_main_sta_fail_fallback(fake_boot, fake_wifi, fake_server):
    fake_boot.load_config.return_value = {
        "mode": "STA",
        "sta": {},
        "ap": {}
    }

    fake_wifi.start_sta.return_value = None
    fake_wifi.start_ap.return_value = MagicMock()

    main.main()

    fake_wifi.start_ap.assert_called_once()
    fake_server.assert_called_once()
    fake_boot.log.assert_any_call("Connexion STA échouée - bascule en AP")

def test_main_sta_fail_and_ap_fail(fake_boot, fake_wifi):
    fake_boot.load_config.return_value = {
        "mode": "STA",
        "sta": {},
        "ap": {}
    }

    fake_wifi.start_sta.return_value = None
    fake_wifi.start_ap.return_value = None

    with patch.object(main, "safe_restart") as restart:
        main.main()
        restart.assert_called_once()

def test_safe_restart(monkeypatch):
    mock_log = MagicMock()
    mock_reset = MagicMock()
    monkeypatch.setattr(main.boot, "log", mock_log)
    monkeypatch.setattr(main.machine, "reset", mock_reset)
    
    # on mock time.sleep pour éviter d'attendre 5sec
    monkeypatch.setattr(main.time, "sleep", lambda x: None)

    main.safe_restart()

    mock_log.assert_called_with("Redémarrage de l'ESP32 dans 5 secondes...")
    mock_reset.assert_called_once()

def test_main_unknown_mode(fake_boot, fake_wifi, fake_server, monkeypatch):
    # Configuration avec mode inexistant
    fake_boot.load_config.return_value = {
        "mode": "UNKNOWN_MODE",
        "ap": {},
        "sta": {}
    }

    # On mock safe_restart pour ne pas reset la machine
    with patch.object(main, "safe_restart") as restart:
        main.main()

    # Vérifie que le bon log est appelé
    fake_boot.log.assert_any_call("Mode inconnu : UNKNOWN_MODE")
    
    # Vérifie que safe_restart() est bien appelé
    restart.assert_called_once()
    
    # Vérifie qu'aucun serveur n'est démarré
    fake_server.assert_not_called()
