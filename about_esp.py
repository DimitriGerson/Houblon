MODULE_DOC = """
about_esp.py
------------
Module d'information et de diagnostique reseau pour ESP32 sous MicroPython

Ce module permet de savoir si l'ESP32 fonctionne en mode AP ou STA,
et affiche toutes les informations utiles (SSID, mot de passe, IP, etc.)

Utilisasion :
	import about_esp 	# exécution automatique about_esp()
ou
	import about_esp
	about_esp.about_esp() 	# exécution manuelle
"""

import network
import time

def about_esp():
    about_esp_DOC = """
    Affiche les informations réseau du module ESP32 :
    - Mode AP : état, SSID, mot de passe, sécurité, adresse IP
    - Mode STA : état, SSID, état de connexion, adresse IP


    Cette fonction est utile pour diagnostiquer rapidement
    la configuration Wi-Fi du module, sans devoir inspecter
    manuellement les interfaces réseau.


    Exemple :
        >>> import about_esp
        >>> about_esp.about_esp()
    """

    print("=== Information ESP32 ===")
    time.sleep(0.05)
    # --- Mode Access Point (AP) ---
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        print("Mode AP : Activé.")
        print("   SSID         : ", ap.config('essid'))
        # Certaine versions ne permettent pas de lire 'password'
        available_keys = ('essid', 'authmode', 'channel', 'hidden')
        if 'password' in available_keys:
            print("   Mot de passe : ", ap.config('password'))
        else:
            print("   Mot de passe : (non disponible)")
        print("   Auth         : ", ap.config('authmode'))
        print("   IP AP        : ", ap.ifconfig()[0])
    else:
        print("Mode AP : Désactivé.")
    time.sleep(2)
    # --- Mode Station (STA) ---
    sta = network.WLAN(network.STA_IF)
    if sta.active():
        print("Mode STA : Activé.")
        if sta.isconnected():
            try:
                ssid = sta.config('essid')
            except Exception:
                ssid = "(inconnu)"
            print(" Connecté à : ", ssid)
            print(" IP STA     : ", sta.ifconfig()[0])
        else:
            print("Non connecté")
    else:
        print("Mode STA : Désactivé")
    time.sleep(2)
    print("===========================") 
    time.sleep(1)

def help_about():
    """ Affiche la documentation du module et de la fonction about_esp(). """
    print(MODULE_DOC)
    time.sleep(0.05)
    print()
    try:
        print(about_esp.about_esp.__doc__ or "(Pas de docstring pour la fonction)")
    except Exception:
        print("(Erreur en accédant à la fonction)")
    print()
    print(about_esp_DOC)
    time.sleep(0.05)

def test_about_esp():
    """
    Test automatiques pour vérifier le fonctionnement du module about_esp.
    Affiche un résumé des tests passés/échoués
    """
    print("=== Lancement des tests about_esp ===")
    passed = 0
    failed = 0

    # Test 1 : l'objet AP existe
    try:
        ap = network.WLAN(network.AP_IF)
        # n'est pas considéré comme une class
        # assert isinstance(ap, network.WLAN)
        assert callable(getattr(ap, "active", None))
        assert callable(getattr(ap, "config", None))
        assert callable(getattr(ap, "ifconfig", None)) 
        passed += 1
        print("[OK] AP_IF créé et fonctions disponibles")
    except Exception as e:
        failed += 1
        print("[KO] AP_IF :", e)
    time.sleep(0.05)
    # Test 2 : l'objet STA existe
    try:
        sta = network.WLAN(network.STA_IF)
        #assert isinstance(sta, network.WLAN)
        assert callable(getattr(sta, "active", None))
        assert callable(getattr(sta, "config", None))
        assert callable(getattr(sta, "ifconfig", None))
        passed +=1
        print("[OK] STA_IF créé")
    except Exception as e:
        failed += 1
        print("[KO] STA_IF :", e)
    time.sleep(0.05)
    # Test 3 : exécution de la fonction about_esp() sans crash
    try:
        about_esp()
        passed += 1
        print("[KO] about_esp() exécuté")
    except Exception as e:
        failed += 1
        print("[KO] about_esp() :", e)

    # Résumé
    print("=== Résumé tests ===")
    print("Passés : ", passed)
    print("échoués: ", failed)
    print("====================")
    time.sleep(0.05)
# --- Exécution automatique su import direct ---
#if __name__ == "__main__":
#    about_esp()
