#src/mqtt_utils.py
"""
mqtt_utils.py
Utilitaires pour la communication MQTT avec MicroPython.

Rôle :
- Établir une connexion MQTT avec un broker.
- Publier des messages sur un topic spécifique.

Utilisation :
Exemple :
    from mqtt_utils import mqtt_connect, mqtt_publish

    client = mqtt_connect("esp8266", "192.168.1.10", 1883)
    mqtt_publish(client, "maison/salon", "Température: 22°C")
"""
from umqtt.simple import MQTTClient

def mqtt_connect(client_id, broker, port):
    """
    Établit une connexion MQTT avec le broker.

    Args:
        client_id (str): Identifiant unique pour le client MQTT.
        broker (str): Adresse IP ou nom de domaine du broker MQTT.
        port (int): Port du broker (par défaut 1883).

    Returns:
        MQTTClient: Instance connectée au broker.
    """
    client = MQTTClient(client_id, broker, port)
    client.connect()
    return client

def mqtt_publish(client, topic, message): 
    """
    Publie un message sur un topic MQTT.

    Args:
        client (MQTTClient): Instance MQTT connectée.
        topic (str): Nom du topic (ex. "maison/salon").
        message (str): Message à envoyer.
    """
    try:
        client.publish(topic, message)
    except Exception as e:
        print("Erreur MQTT:", e)
