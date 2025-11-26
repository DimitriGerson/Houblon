import sys
import types
import pytest

# === On MOCK le module umqtt.simple ===
#   Cela évite l'erreur "ModuleNotFoundError: umqtt.simple"
mock_umqtt = types.SimpleNamespace(
    MQTTClient=lambda client_id, broker, port: MockMQTTClient(client_id, broker, port)
)

sys.modules["umqtt.simple"] = mock_umqtt

# === Mock de MQTTClient pour nos tests ===
class MockMQTTClient:
    def __init__(self, client_id, broker, port):
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.connected = False
        self.published_messages = []

    def connect(self):
        self.connected = True

    def publish(self, topic, message):
        self.published_messages.append((topic, message))


# === Import après avoir mocké le module ===
from mqtt_utils import mqtt_connect, mqtt_publish


# === TESTS ===

def test_mqtt_connect():
    client = mqtt_connect("test_id", "192.168.1.100", 1883)

    assert client.connected is True
    assert client.client_id == "test_id"
    assert client.broker == "192.168.1.100"
    assert client.port == 1883


def test_mqtt_publish():
    client = mqtt_connect("test_id", "192.168.1.100", 1883)

    mqtt_publish(client, "test/topic", "hello")
    assert client.published_messages == [("test/topic", "hello")]


def test_publish_error_handled(capfd):
    """On vérifie que l'erreur est bien gérée et affichée"""
    class ErrorClient(MockMQTTClient):
        def publish(self, topic, message):
            raise Exception("Erreur de test")

    client = ErrorClient("id", "broker", 1883)

    mqtt_publish(client, "topic", "message")
    captured = capfd.readouterr()

    assert "Erreur MQTT" in captured.out
