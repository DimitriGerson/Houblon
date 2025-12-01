# mqtt_client.py
# Classe dédiée à l'envoi des données vers un serveur MQTT

import time
from umqtt.simple import MQTTClient  # Library MicroPython

class MQTTHandler:
    def __init__(self, config):
        """
        config doit contenir :
        {
            "server": "192.168.1.20",
            "port": 1883,
            "client_id": "ESP8266_01",
            "topic": "mesures/capteurs"
        }
        """
        self.server = config["server"]
        self.port = config.get("port", 1883)
        self.client_id = config.get("client_id", "esp8266")
        self.topic = config.get("topic", "esp/data")

        self.client = MQTTClient(
            client_id=self.client_id,
            server=self.server,
            port=self.port
        )

    def connect(self):
        try:
            self.client.connect()
            print("MQTT connecté à :", self.server)
            return True
        except Exception as e:
            print("Erreur connexion MQTT :", e)
            return False

    def publish(self, data):
        """
        data doit être un dictionnaire ou string
        """
        try:
            if isinstance(data, dict):
                import json
                data = json.dumps(data)
            self.client.publish(self.topic, data)
            print("MQTT publish :", data)
        except Exception as e:
            print("Erreur envoi MQTT :", e)

    def disconnect(self):
        try:
            self.client.disconnect()
        except:
            pass
