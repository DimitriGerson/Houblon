# mqtt_client.py
# Classe dédiée à l'envoi des données vers un serveur MQTT

import time
from umqtt.simple import MQTTClient  # Library MicroPython

class MQTTHandler:
    
    """
    Classe pour gérer la connexion et la publication de données vers un serveur MQTT.

    Cette classe encapsule les opérations courantes pour :
    - Se connecter à un broker MQTT
    - Publier des messages sur un topic
    - Se déconnecter proprement

    Attributes:
        server (str): Adresse IP ou nom du serveur MQTT.
        port (int): Port du serveur MQTT (par défaut 1883).
        client_id (str): Identifiant unique du client MQTT.
        topic (str): Topic sur lequel publier les messages.
        client (MQTTClient): Instance du client MQTT.
    """

    def __init__(self, config):
        """
        Initialise le client MQTT avec les paramètres fournis.

        Args:
            config (dict): Dictionnaire contenant les clés suivantes :
                - "server" (str): Adresse du serveur MQTT.
                - "port" (int, optionnel): Port du serveur (par défaut 1883).
                - "client_id" (str, optionnel): Identifiant du client (par défaut "esp8266").
                - "topic" (str, optionnel): Topic pour la publication (par défaut "esp/data").

        Raises:
            KeyError: Si la clé "server" est absente du dictionnaire.

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
        """
        Établit la connexion avec le serveur MQTT.

        Returns:
            bool: True si la connexion réussit, False sinon.

        Affiche un message en cas de succès ou d'erreur.
        """
        try:
            self.client.connect()
            print("MQTT connecté à :", self.server)
            return True
        except Exception as e:
            print("Erreur connexion MQTT :", e)
            return False

    def publish(self, data):
        """
        Publie des données sur le topic MQTT configuré.

        Args:
            data (dict | str): Données à envoyer. Si un dictionnaire est fourni,
                               il sera converti en JSON.

        Affiche un message en cas de succès ou d'erreur.
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
