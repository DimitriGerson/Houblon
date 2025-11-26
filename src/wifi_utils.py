# Wifi_utils.py
# Fonction utilitaires Wi-Fi (AP / STA) 
"""
wifi_utils.py
Fonctions utilitaires pour la gestion du Wi-Fi sur ESP (MicroPython).

Rôle :
- Activer ou désactiver les modes Wi-Fi (AP ou STA).
- Démarrer un point d'accès (AP).
- Connecter l'ESP à un réseau existant (STA).
- Fournir un mode simulation pour tests sur PC.

Utilisation :
Importé par main.py pour configurer le réseau selon config.json.
"""
import time
import boot

# --- Détection automatique : ESP32 ou simulation PC ---
try:
    import network  # vrai module sur ESP32
    _ESP_MODE = True
except ImportError:
    import network_mock as network # version simulée pour PC
    _ESP_MODE = False

def disable_all_wifi():
    """
    Désactive tous les modes Wi-Fi actifs (AP et STA).

    Cette fonction est appelée avant de changer de mode
    pour éviter les conflits entre interfaces.
    """
    for iface in [network.WLAN(network.STA_IF), network.WLAN(network.AP_IF)]:
        if iface.active():
            iface.active(False)
    boot.log("Tous les modes Wi-Fi désactivés.")

def start_ap(cfg):
    """
    Démarre le point d'accès Wi-Fi (mode AP).

    Args:
        cfg (dict): Configuration du point d'accès avec clés :
            - ssid (str): Nom du réseau AP.
            - password (str): Mot de passe.
            - channel (int): Canal Wi-Fi (par défaut 6).
            - hidden (bool): Réseau caché ou non.

    Returns:
        network.WLAN: Objet AP actif si succès, sinon None.
    """
    disable_all_wifi()
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(
        essid=cfg["ssid"],
        password=cfg["password"],
        channel=cfg.get("channel", 6),
        hidden=cfg.get("hidden", False),
        authmode=network.AUTH_WPA_WPA2_PSK
    )
    for _ in range(10):
        if ap.active():
            boot.log("AP actif - SSID: " + cfg['ssid'] +" - IP: " + ap.ifconfig()[0])
            return ap
        time.sleep(0.5)
    boot.log("Echec de l'activation du point d'accès.")
    return None
    
def start_sta(cfg): 
    """
    Connecte l'ESP en mode Station (STA) à un réseau existant.

    Args:
        cfg (dict): Configuration STA avec clés :
            - ssid (str): Nom du réseau Wi-Fi.
            - password (str): Mot de passe.

    Returns:
        network.WLAN: Objet STA connecté si succès, sinon None.
    """
    disable_all_wifi()
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(cfg["ssid"], cfg["password"])
    for _ in range (20):
        if sta.isconnected():
            boot.log(" Connecté à " + cfg['ssid'] + " - IP: " + sta.ifconfig()[0])
            return sta
        time.sleep(0.5)
    boot.log("Echec connexion STA.")
    sta.active(False)
    return None
# --- Optionnel : petit log pour savoir sur quoi on tourne ---
if not _ESP_MODE:
    boot.log("Mode simulation réseau activé (network_mock).")
