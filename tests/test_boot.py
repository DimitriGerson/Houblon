import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
import json
import boot
from unittest.mock import patch

def setup_function():
    # Nettoyage avant chaque test
    for f in ["boot.log", "config.json"]:
        if f in os.listdir() and os.getcwd().endswith("tests"):
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

def test_clear_old_log_handles_exception():
    # s'assurer qu'un fichier existe
    with open("boot.log", "wb") as f:
        f.write(b"x" * 200_000) # gros fichier pour déclencher la condition

    # On force os.stat à lever une exception
    with patch("os.stat", side_effect=Exception("test error")):
        boot.clear_old_log() # doivent PAS lever d'erreur

    # Le fichier doit encore exister, car l'exception a empêché la suppression
    assert os.path.exists("boot.log")

def test_load_config_missing_file():
    # On s'assure que le fichier n'existe pas
    if os.path.exists("config.json"):
        os.remove("config.json")
    
    cfg = boot.load_config()
    assert cfg["mode"] == "AP"
    assert "ap" in cfg

def test_loa_config_invalid_json():
    with open("config.json", "w") as f:
        f.write("{invalid_json: true") # pas de guillements ni accolade fermante

    cfg = boot.load_config()
    assert cfg["mode"] == "AP"

from unittest.mock import patch

def test_load_config_raises_oserror():
    with patch("builtins.open", side_effect=OSError("Permission denied")):
        cfg = boot.load_config()
        assert cfg["mode"] == "AP"
