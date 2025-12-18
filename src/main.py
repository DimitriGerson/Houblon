"""
main.py
Point d’entrée principal de l'application ESP32 (MicroPython).

Rôle :
- Charger la configuration système (via boot.py)
- Initialiser le Wi-Fi en mode AP ou STA
- Lancer le serveur web (si nécessaire)
- Lire les capteurs et publier les données via MQTT
- Gérer les erreurs, bascules automatiques et redémarrages sécurisés

Structure :
    - safe_restart()
        Redémarrage de l'ESP32 après un délai
    - read_and_publish_sensors()
        Lecture des capteurs + enregistrement + publication MQTT
    - mode_ap()
        Démarrage en point d'accès + serveur web + mesures
    - mode_sta()
        Connexion au Wi-Fi station + mesures
    - mode_unknown()
        Gestion des modes invalides → redémarrage
    - MODE_FUNCTIONS
        Dispatch dynamique AP/STA
    - main()
        Orchestration générale, appelée automatiquement après boot.py

Fonctionnement général :
    1. boot.py exécute l'initialisation et charge la configuration
    2. main.py récupère la configuration (mode, Wi-Fi, MQTT)
    3. main.py configure MQTT, Wi-Fi, serveur web selon le mode
    4. Les capteurs sont lus périodiquement, enregistrés et publiés
    5. Redémarrage automatique en cas d'erreur critique

Modules externes :
    - boot : logs + chargement config
    - wifi_utils : gestion AP / STA
    - network_setup : serveur web embarqué
    - technique_sensors : abstraction capteurs
    - mqtt_client : wrapper MQTT fiable

Compatibilité MicroPython :
    - machine.reset est encapsulé pour permettre les tests PC
    - time.sleep est utilisé pour temporiser le publish MQTT

Ce fichier constitue la boucle opérationnelle centrale du projet.
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
from mqtt_client import MQTTHandler

def safe_restart():
    """
    Redémarrage sécurisé de l’ESP32.

    Rôle :
        - Informer via les logs qu’un redémarrage va avoir lieu
        - Attendre 5 secondes (permet de lire l’erreur éventuelle)
        - Effectuer un reset matériel de l’ESP32

    Utilisation :
        Appelé en cas d'erreur critique (ex : Wi-Fi impossible, mode inconnu).

    Notes :
        - Sur PC (tests), machine.reset est mocké pour éviter un vrai reboot.
    """
    boot.log("Redémarrage de l'ESP32 dans 5 secondes...")
    time.sleep(5)
    machine.reset()

def read_and_publish_sensors(mqtt, iterations=2):
    """
    Lit les capteurs, sauvegarde les données et publie les valeurs via MQTT.

    Args:
        mqtt (MQTTHandler): Instance configurée pour communiquer avec le broker.
        iterations (int): Nombre de cycles de mesures (défaut 2).

    Fonctionnement :
        - Initialise la classe Techniques pour lire tous les capteurs
        - Enregistre les mesures dans data.json
        - Publie chaque valeur sur un topic MQTT dédié
        - Ajoute une pause de 10 secondes entre chaque cycle

    Publication MQTT :
        Pour chaque mesure :
            topic = mqtt.topic + clé_de_mesure
            valeur = str(valeur_mesurée)

    Gestion des erreurs :
        - Si la connexion MQTT échoue : log "MQTT non connecté"
        - Le programme continue son exécution

    Notes :
        - Compatible MicroPython + mode test PC
        - Pensé pour fonctionner aussi bien en AP qu’en STA
    """
    tech = Techniques("config.json")
    for _ in range(iterations):
        data = tech.read_all()
        print(data)

        #tech.save_measure(data)

        try:
            boot.log("Avant la connection au mqtt")
            mqtt.connect()  #une connection par cycle
            boot.log("Premiere connection au mqtt ???")
            time.sleep(1)

            for item in data:
                capteur = item["name"]
                type_capteur = item["type"]
                valeur = item["value"]

                for cle, val in valeur.items():
                    topic = mqtt.topic + cle
                    mqtt.client.publish(topic, str(val))
        except Exception as e:
            print("MQTT : publish impossible :", e)
            boot.log("MQTT non connecté")
        finally:
            try:
                mqtt.disconnect()
            except:
                pass
        time.sleep(10)

def mode_ap(cfg, mqtt):
    """
    Démarre l'ESP32 en mode Point d'Accès (AP).

    Args:
        cfg (dict): Configuration complète chargée depuis config.json.
        mqtt (MQTTHandler): Gestionnaire MQTT déjà initialisé.

    Fonctionnement :
        - Active le point d’accès Wi-Fi avec ssid/password de cfg["ap"]
        - Démarre le serveur web embarqué
        - Lance la lecture des capteurs + publication MQTT

    Cas d'erreur :
        - Si l’AP ne peut pas démarrer → redémarrage sécurisé

    Utilisation :
        Mode utile si l’ESP doit servir de réseau indépendant
        (ex : configuration initiale, absence de Wi-Fi local).
    """
    ap = wifi_utils.start_ap(cfg["ap"])
    if ap:
        boot.log("Point d'accès actif, lancement du server web...")
        start_server(ap, "AP")
        read_and_publish_sensors(mqtt)
    else:
        boot.log("Impossible de démarrer le Wifi AP. Redémarrage...")
        safe_restart()

def mode_sta(cfg, mqtt):
    """
    Démarre l'ESP32 en mode Point d'Accès (AP).

    Args:
        cfg (dict): Configuration complète chargée depuis config.json.
        mqtt (MQTTHandler): Gestionnaire MQTT déjà initialisé.

    Fonctionnement :
        - Active le point d’accès Wi-Fi avec ssid/password de cfg["ap"]
        - Démarre le serveur web embarqué
        - Lance la lecture des capteurs + publication MQTT

    Cas d'erreur :
        - Si l’AP ne peut pas démarrer → redémarrage sécurisé

    Utilisation :
        Mode utile si l’ESP doit servir de réseau indépendant
        (ex : configuration initiale, absence de Wi-Fi local).
    """
    sta = wifi_utils.start_sta(cfg["sta"])
    if not sta:
        boot.log("Connexion STA échouée - bascule en AP")
        ap = wifi_utils.start_ap(cfg["ap"])
        if ap:
            machine.reset() # on ne se met plus en AP si on arrive pas à se connecter en sta
            start_server(ap, "AP")
        else:
            safe_restart()
    else:
        boot.log("Connexion STA réussie.")
        #start_server(sta, "STA")  # décommenter si serveur STA souhaité
        read_and_publish_sensors(mqtt)

def mode_unknown(cfg, mqtt):
    """
    Gestion des modes Wi-Fi invalides ou non reconnus.

    Args:
        cfg (dict): Configuration chargée depuis le fichier JSON.
        mqtt (MQTTHandler): Instance active du gestionnaire MQTT.

    Fonctionnement :
        - Enregistre un log indiquant que le mode est invalide
        - Déclenche un redémarrage sécurisé

    Utilité :
        - Garantir que l’ESP ne reste pas bloqué dans un état incohérent
    """
    boot.log("Mode inconnu : " + cfg.get("mode","UNKNOWN"))
    safe_restart()
# Dictionnaire permettant de sélectionner dynamiquement
# la fonction correspondant au mode réseau défini dans config.json
MODE_FUNCTIONS = {
    "AP": mode_ap,
    "STA": mode_sta
}

def main():
    """
    Fonction principale exécutée après boot.py.

    Rôle :
        - Charger la configuration complète (Wi-Fi, MQTT…)
        - Initialiser le gestionnaire MQTT
        - Sélectionner le mode réseau (AP/STA)
        - Démarrer la logique correspondante via MODE_FUNCTIONS
        - Nettoyer la connexion MQTT avant sortie

    Étapes :
        1. Lecture config → mode Wi-Fi (AP/STA)
        2. Initialisation MQTT
        3. Log du mode choisi
        4. Appel dynamique de la fonction correspondant au mode
        5. Déconnexion MQTT propre

    Notes :
        - Toute erreur critique dans un mode déclenche un restart.
        - La sélection dynamique permet d'ajouter d'autres modes facilement.
    """
    cfg = boot.load_config()
    mode = cfg.get("mode","AP").upper()
    boot.log("Chargement du mode " + str(mode))
    mqtt = MQTTHandler(cfg["mqtt"])
    mqtt.connect()
    boot.log("Démarrage en mode : " + mode)
    # Choix du mode via dictionnaire, fallback vers inconnu
    mode_fn = MODE_FUNCTIONS.get(mode, mode_unknown)
    try:
        mode_fn(cfg, mqtt)
    except Exception as e:
        boot.log("Erreur : " + str(e))
    finally:
        time.sleep_ms(200)
        boot.log(str(cfg["DEEP_SLEEP_MS"]))
        machine.deepsleep(cfg["DEEP_SLEEP_MS"])
    #mqtt.disconnect()

if __name__ == "__main__":
    main()
