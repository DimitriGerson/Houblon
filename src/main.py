# main.py
# Choisit le mode réseau selon confg.json et lance le programme principal

"""
main.py
Programme principal pour l'ESP32 sous MicroPython.

Rôle :
- Charger la configuration depuis config.json.
- Choisir le mode réseau (AP ou STA) et initialiser le Wi-Fi.
- Lancer le serveur web.
- Lire les capteurs et sauvegarder les mesures.
- Gérer les bascules et redémarrages en cas d'erreur.

Fonctionnalités :
- Mode AP : création d'un point d'accès et démarrage du serveur.
- Mode STA : connexion au réseau Wi-Fi existant, sinon fallback en AP.
- Lecture des capteurs via la classe Techniques.
- Sauvegarde des mesures dans data.json.
- Redémarrage sécurisé en cas d'échec critique.

Utilisation :
Exécuter ce fichier après boot.py. Il s'appuie sur :
- boot.py pour la configuration et les logs.
- wifi_utils.py pour la gestion Wi-Fi.
- technique_sensors.py pour la lecture des capteurs.
- network_setup.py pour le serveur web.
"""

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
import time
from mqtt_client import MQTTHandler 

def safe_restart():
    """
    Redémarre l'ESP32 après un délai de 5 secondes.
    Utilisé en cas d'erreur critique.
    """
    boot.log("Redémarrage de l'ESP32 dans 5 secondes...")
    time.sleep(5)
    machine.reset()

def main():
    """
    Point d'entrée principal :
    - Charge la configuration
    - Sélectionne le mode réseau (AP ou STA)
    - Lance le serveur web
    - Gère la lecture des capteurs et la sauvegarde des données
    """
    # === Chargement de la configuration ===
    cfg = boot.load_config()
    mode = cfg.get("mode","AP").upper()

    # Initialisation MQTT
    mqtt = MQTTHandler(cfg["mqtt"])
    mqtt.connect()  # Connexion
    
    boot.log("Démarrage en mode : " + mode )

    # === Démarrage selon le mode ===
    if mode == "AP":
        ap = wifi_utils.start_ap(cfg["ap"])
        
        (lambda: (
            boot.log("Point d'accès actif, lancement du server web..."),
            start_server(ap, "AP")
        ))() if ap else (lambda: (
            boot.log("Impossible de démarrer le Wifi AP. Redémarrage..."),
            safe_restart()
        ))()

        tech = Techniques("config.json")
        for _ in range(2):
            # Lire tous les capteurs
            data = tech.read_all()
            # Afficher les résultats dans le REPL
            print(data)
            #sauvegarder les mesures dans data.json
            tech.save_measure(data)
            #Pause de 10 secondes avant la prochaine lecture
            time.sleep(10)


    elif mode == "STA":
        sta = wifi_utils.start_sta(cfg["sta"])
        if not sta:
            boot.log("Connexion STA échouée - bascule en AP")
            ap = wifi_utils.start_ap(cfg["ap"])
            if ap:
                start_server(ap, "AP") # fallback en AP
            else:
                safe_restart()
        else:
            boot.log("Connexion STA réussie.")
            boot.log("Lancement du serveur web...")
            start_server(sta, "STA") # ici aussi, lancement du serveur
            tech = Techniques("config.json")
            for _ in range(2):
                # Lire tous les capteurs
                data = tech.read_all()
                # Afficher les résultats dans le REPL
                print(data)
                #sauvegarder les mesures dans data.json
                tech.save_measure(data)
                
                for item in data:
                    if mqtt.client.is_connected():
                        mqtt.client.publish(mqtt.topic + "/" + item["name"], str(item["value"]))
                    else:
                        boot.log("MQTT non connecté")
                #Pause de 10 secondes avant la prochaine lecture
                time.sleep(10)
            
    else:
        boot.log("Mode inconnu : " + mode)
        safe_restart()
    mqtt.disconnect()

if __name__ == "__main__":
    main()
