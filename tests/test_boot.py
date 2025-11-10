import os
import json
import boot

def setup_function():
    # Nettoyage avant chaque test
    for f in ["boot.log", "config.json"]:
        if f in os.listdir():
            os.remove(f)

def test_load_config_default():
    cfg = boot.load_config()
    assert cfg["mode"] == "AP"
    assert "ap" in cfg
    assert "sta" in cfg

def test_load_config_custom():
    sample = {"mode": "STA", "sta": {"ssid": "TestWifi", "password": "secret"}}
    with open("config.json", "w") as f:
        json.dump(sample, f)
    cfg = boot.load_config()
    assert cfg["mode"] == "STA"
    assert cfg["sta"]["ssid"] == "TestWifi"

def test_log_creates_file():
    boot.log("Hello test")
    assert "boot.log" in os.listdir()
    with open("boot.log") as f:
        assert "Hello test" in f.read()

def test_clear_old_log_removes_large_file():
    with open("boot.log", "wb") as f:
        f.write(b"x" * 101_000)
    boot.clear_old_log()
    assert not os.path.exists("boot.log")
