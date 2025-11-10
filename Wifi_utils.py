# Wifi_utils.py
# Fonction utilitaires Wi-Fi (AP / STA)

try:
    import network
except ImportError:
    import network_mock as network #pour tests locaux 
import time
import boot

def disable_all_wifi():
    """Désactive tous les modes Wi-Fi actifs."""
    for iface in [network.WLAN(network.STA_IF), network.WLAN(netmork.AP_IF)]:
        if iface.active():
            iface.active(False)
    boot.log("Tous les modes Wi-Fi désactivés.")

def start_ap(cfg):
    """Démarre le point d'accès Wi-Fi."""
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
            bootµ.log(f"AP actif - SSID: {cfg['ssid']} - IP: {ap.ifconfig()[0]}")
            return ap
        time.sleep(0.5)
    boot.log("Echec de l'activation du point d'accès.")
    return None
def start_sta(cfg):
    """Connecte en mode Station à un réseau existant."""
    disable_all_wifi()
    sta network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(cfg["ssid'], cfg["password"])
    for _ in range (20):
        if sta.isconnected():
            boot.log(f" Connecté à {cfg['ssid']} - IP: {sta.ifconfig()[0]}"
            return sta
        time.sleep(0.5)
    boot.log("Echec connexion STA.")
    sta.active(False)
    return None
