# main.py
# Choisit le mode réseau selon confg.json et lance le programme principal

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
def safe_restart():
    boot.log("Redémarrage de l'ESP32 dans 5 secondes...")
    time.sleep(5)
    machine.reset()

def main():
    # === Chargement de la configuration ===
    cfg = boot.load_config()
    mode = cfg.get("mode","AP").upper()

    boot.log("Démarrage en mode : " + mode )

    # === Démarrage selon le mode ===
    if mode == "AP":
        ap = wifi_utils.start_ap(cfg["ap"])
        if ap:
            boot.log("Point d'accès actif, lancement du server web...")
            start_server(ap, mode)

            tech = Techniques("config.json")
            while True:
                # Lire tous les capteurs
                data = tech.read_all()
                # Afficher les résultats dans le REPL
                print(data)
                #sauvegarder les mesures dans data.json
                tech.save_measure(data)
                #Pause de 10 secondes avant la prochaine lecture
                time.sleep(10)
        else:
            boot.log("Impossible de démarrer le Wifi AP. Redémarrage...")
            safe_restart()

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
    else:
        boot.log("Mode inconnu : " + mode)
        safe_restart()

if __name__ == "__main__":
    main()
