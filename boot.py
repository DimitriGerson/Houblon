#boot.py
#initialisation minimal + gestion des logs + chargement config

import time, os, json

LOG_FILE = "boot.log"

def log(msg):
    """Affiche et écrit un message dans boot.log."""
    t = time.ticks_ms() / 1000
    line = f"[{t:07.2f}] {msg} \n"
    print(line, end="")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line)

    except:
        pass

def clear_old_log():
    """Efface le log s'il dépasse 100 Ko."""
    try:
        if LOG_FILE in os.lisdir() and os.stat(LOG_FILE)[6] > 100_000:
            os.remove(LOG_FILE)
            print("Log effacé (trop volumineux).")
    except:
        pass

def load_config():
    """Charge la configyration réseau depuis config.json."""
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
            log("Configuration chargée.")
            return cfg
    except Exception as e:
        log(f"Erreur lecture config.json : {e}")
        return {
            "mode": "AP",
            "ap": {"ssid": "ESP32_AP", "password": "12345678", "channel": 6, "hidden":False},
            "sta":{"ssid": "", "password": ""}
        }

def main():
    clear_old_log()
    log("=== Boot ESP32 ===")
    log("Boot terminé - main.py va prendre le relais...")

main()
