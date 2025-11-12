# main.py
# Choisit le mode réseau selon confg.json et lance le programme principal

import boot
import wifi_utils
import time
import machine
from network_setup import start_server

def safe_restart():
    boot.log("Redémarrage de l'ESP32 dans 5 secondes...")
    time.sleep(5)
    machine.reset()

cfg = boot.load_config()
mode = cfg.get("mode","AP").upper()

boot.log(f"Démarrage en mode : {mode}")

if mode == "AP":
    ap = wifi_utils.start_ap(cfg["ap"])
    if ap:
        start_server(ap, mode)
    else:
        boot.log("Impossible de démarrer le Wifi AP. Redémarrage...")
        safe_restart()

elif mode == "STA":
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
else:
    boot.log(f"Mode inconnu : {mode}")
    safe_restart()

boot.log("Configuration réseau terminée.")
boot.log("Programme principal en cours...")

# === Exemple de boucle principale ===
while True:
    time.sleep(5)
    boot.log("ESP32 actif...")
