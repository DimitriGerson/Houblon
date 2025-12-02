
import pytest
from unittest.mock import MagicMock, patch
from mqtt_client import MQTTHandler

@pytest.fixture
def config():
    return {
        "server": "192.168.1.20",
        "port": 1883,
        "client_id": "ESP8266_01",
        "topic": "mesures/capteurs"
    }

@pytest.fixture
def mqtt_handler(config):
    return MQTTHandler(config)

def test_init_attributes(mqtt_handler):
    """Vérifie que les attributs sont correctement initialisés."""
    assert mqtt_handler.server == "192.168.1.20"
    assert mqtt_handler.port == 1883
    assert mqtt_handler.client_id == "ESP8266_01"
    assert mqtt_handler.topic == "mesures/capteurs"

@patch("mqtt_client.MQTTClient")
def test_connect_success(mock_client, mqtt_handler):
    """Test que connect() retourne True en cas de succès."""
    mqtt_handler.client = mock_client()
    mqtt_handler.client.connect.return_value = None  # Pas d'erreur
    assert mqtt_handler.connect() is True
    mqtt_handler.client.connect.assert_called_once()

@patch("mqtt_client.MQTTClient")
def test_connect_failure(mock_client, mqtt_handler):
    """Test que connect() retourne False en cas d'erreur."""
    mqtt_handler.client = mock_client()
    mqtt_handler.client.connect.side_effect = Exception("Erreur")
    assert mqtt_handler.connect() is False

@patch("mqtt_client.MQTTClient")
def test_publish_dict(mock_client, mqtt_handler):
    """Test que publish() convertit un dict en JSON et appelle MQTTClient.publish."""
    mqtt_handler.client = mock_client()
    data = {"temp": 25}
    mqtt_handler.publish(data)
    args, kwargs = mqtt_handler.client.publish.call_args
    assert args[0] == mqtt_handler.topic
    assert '{"temp": 25}' in args[1]

@patch("mqtt_client.MQTTClient")
def test_publish_string(mock_client, mqtt_handler):
    """Test que publish() envoie une chaîne telle quelle."""
    mqtt_handler.client = mock_client()
    data = "Hello MQTT"
    mqtt_handler.publish(data)
    mqtt_handler.client.publish.assert_called_with(mqtt_handler.topic, data)

@patch("mqtt_client.MQTTClient")
def test_disconnect(mock_client, mqtt_handler):
    """Test que disconnect() appelle MQTTClient.disconnect sans erreur."""
    mqtt_handler.client = mock_client()
    mqtt_handler.disconnect()
    mqtt_handler.client.disconnect.assert_called_once()
