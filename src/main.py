import boot
import wifi_utils
import time
try:
    import machine
except ImportError:
    import types
    machine = types.SimpleNamespace(reset=lambda: None)
from network_setup import start_server
from technique_sensors import Techniques
from mqtt_client import MQTTHandler

def safe_restart():
    boot.log("Redémarrage de l'ESP32 dans 5 secondes...")
    time.sleep(5)
    machine.reset()

def read_and_publish_sensors(mqtt, iterations=2):
    tech = Techniques("config.json")
    for _ in range(iterations):
        data = tech.read_all()
        print(data)
        tech.save_measure(data)

        for item in data:
            capteur = item["name"]
            type_capteur = item["type"]
            valeur = item["value"]
            try:
                mqtt.connect()
                time.sleep(2)
                for cle, val in valeur.items():
                    topic = mqtt.topic + cle
                    mqtt.client.publish(topic, str(val))
                mqtt.disconnect()
            except Exception as e:
                print("MQTT : publish impossible :", e)
                boot.log("MQTT non connecté")
        time.sleep(10)

def mode_ap(cfg, mqtt):
    ap = wifi_utils.start_ap(cfg["ap"])
    if ap:
        boot.log("Point d'accès actif, lancement du server web...")
        start_server(ap, "AP")
        read_and_publish_sensors(mqtt)
    else:
        boot.log("Impossible de démarrer le Wifi AP. Redémarrage...")
        safe_restart()

def mode_sta(cfg, mqtt):
    sta = wifi_utils.start_sta(cfg["sta"])
    if not sta:
        boot.log("Connexion STA échouée - bascule en AP")
        ap = wifi_utils.start_ap(cfg["ap"])
        if ap:
            start_server(ap, "AP")
        else:
            safe_restart()
    else:
        boot.log("Connexion STA réussie.")
        #start_server(sta, "STA")  # décommenter si serveur STA souhaité
        read_and_publish_sensors(mqtt)

def mode_unknown(cfg, mqtt):
    boot.log("Mode inconnu : " + cfg.get("mode","UNKNOWN"))
    safe_restart()

MODE_FUNCTIONS = {
    "AP": mode_ap,
    "STA": mode_sta
}

def main():
    cfg = boot.load_config()
    mode = cfg.get("mode","AP").upper()

    mqtt = MQTTHandler(cfg["mqtt"])
    mqtt.connect()
    boot.log("Démarrage en mode : " + mode)

    # Choix du mode via dictionnaire, fallback vers inconnu
    mode_fn = MODE_FUNCTIONS.get(mode, mode_unknown)
    mode_fn(cfg, mqtt)

    mqtt.disconnect()

if __name__ == "__main__":
    main()
