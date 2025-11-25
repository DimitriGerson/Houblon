import os
import json
import pytest
from unittest.mock import MagicMock, patch
from technique_sensors import Techniques


# ============================
#     TEST __init__() 
# ============================

def test_init_loads_config(tmp_path, monkeypatch):
    # Création d'un faux fichier JSON
    config_file = tmp_path / "config.json"
    config_file.write_text('{"sensors": [{"name": "S1", "type": "analog", "pin": 1}]}')

    tech = Techniques(config_file)

    assert tech.sensors == [{"name": "S1", "type": "analog", "pin": 1}]


def test_init_file_not_found(monkeypatch):
    tech = Techniques("fichier_qui_existe_pas.json")
    assert tech.sensors == []  # doit renvoyer liste vide


# ============================
#     TEST read_sensor()
# ============================

def test_read_sensor_unknown_type():
    tech = Techniques()
    with pytest.raises(ValueError):
        tech.read_sensor({"name": "X", "type": "???", "pin": 0})


# ============================
#     TEST read_all()
# ============================

def test_read_all(monkeypatch):
    tech = Techniques()
    tech.sensors = [
        {"name": "A1", "type": "analog", "pin": 1},
        {"name": "D1", "type": "digital", "pin": 2},
    ]

    # Mock des méthodes hardware
    monkeypatch.setattr(tech, "read_analog", lambda pin: 123)
    monkeypatch.setattr(tech, "read_digital", lambda pin: 0)

    results = tech.read_all()

    assert results == [
        {"name": "A1", "type": "analog", "value": 123},
        {"name": "D1", "type": "digital", "value": 0},
    ]


# ============================
#     TEST save_measure()
# ============================

def test_save_measure(tmp_path, monkeypatch):
    filename = tmp_path / "data.json"
    tech = Techniques()
    
    # Données simulées
    data = [{"name": "S1", "type": "analog", "value": 42}]

    # Simule time.time()
    monkeypatch.setattr("technique_sensors.time.time", lambda: 1111111.0)

    tech.save_measure(data, filename)

    # Vérification JSON écrit
    content = json.loads(filename.read_text())
    assert content[0]["name"] == "S1"
    assert content[0]["timestamp"] == 1111111.0

def test_read_dht22_no_machine():
    """Test fallback quand machine n'est pas disponible"""
    tech = Techniques()
    result = tech.read_dht22(1)
    assert result["status"] == "error"
    assert "machine non disponible" in result["message"]


def test_read_dht22_with_mock(monkeypatch):
    """Test la lecture DHT22 avec mocks pour machine et dht"""
    tech = Techniques()

    # Mock module machine
    class MockPin:
        def __init__(self, pin):
            self.pin = pin

    class MockDHT:
        def __init__(self, pin):
            self.pin = pin
        def measure(self):
            pass
        def temperature(self):
            return 25
        def humidity(self):
            return 55

    mock_machine = MagicMock()
    mock_machine.Pin = MockPin

    # Patch get_machine pour renvoyer notre module simulé
    monkeypatch.setattr(tech, "get_machine", lambda: mock_machine)
    # Patch dht.DHT22
    import technique_sensors
    import types
    mock_dht_module = types.SimpleNamespace(DHT22=MockDHT)
    monkeypatch.setattr(technique_sensors, "dht", mock_dht_module)

    result = tech.read_dht22(4)

    assert result["status"] == "ok"
    assert result["temperature"] == 25
    assert result["humidity"] == 55
