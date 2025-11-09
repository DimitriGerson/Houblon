# main.py
# Choisit le mode réseau selon confg.json et lance le programme principal

import boot
import Wifi_utils
import time

cfg = boot.load_config()
mode = cfg.get("mode","AP").upper()

boot.log(f"Démarrage en mode : {mode}")

if mode == "AP"
    wifi_utils.start_ap(cfg["ap"])
elif mode == "STA"
    sta = wifi_utils.start_sta(cfg["sta"])
    if not sta:
        boot.log("Connexion STA échouée - bascule en AP")
        wifi_utils.start_ap(cfg["ap"])
    else:
        boot.log("Mode inconnu : {mode}")

    boot.log("Configuration réseau terminée.")
    boot.log("Programme principal en cours...")

    # === Exemple de boucle principale ===
    While True:
        time.sleep(5)
        boot.log("ESP32 actif...")
