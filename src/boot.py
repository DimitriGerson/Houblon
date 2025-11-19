#boot.py
#initialisation minimal + gestion des logs + chargement config

import time, os, json

try:
    ticks_ms = time.ticks_ms # MicroPython
except AttributeError:
    # fallback pour tests PC
    ticks_ms = lambda: int(time.time() * 1000)

LOG_FILE = "boot.log"
CONFIG_FILE = "config.json"

def log(msg):
    """Affiche et écrit un message dans boot.log."""
    t = ticks_ms() / 1000
    line = "[{:.2f}] ".format(t) + msg + "\n"
    print(line, end="")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line)

    except Exception as e:
        print("Une erreur est survenue : " + e)

def clear_old_log():
    """Efface le log s'il dépasse 100 Ko."""
    try:
        if LOG_FILE in os.listdir() and os.stat(LOG_FILE)[6] > 100_000:
            os.remove(LOG_FILE)
            print("Log effacé (trop volumineux).")
    except OSError as e:
        print("Erreur lors de la suppression du log : " + e )

def load_config():
    """Charge la configyration réseau depuis config.json."""
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
            log("Configuration chargée.")
            return cfg
    except Exception as e:
        log("Erreur lecture config.json : " + str(e) )
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
