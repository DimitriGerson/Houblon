# Documentation pour src/wifi_utils.py

wifi_utils.py
Fonctions utilitaires pour la gestion du Wi-Fi sur ESP (MicroPython).

Rôle :
- Activer ou désactiver les modes Wi-Fi (AP ou STA).
- Démarrer un point d'accès (AP).
- Connecter l'ESP à un réseau existant (STA).
- Fournir un mode simulation pour tests sur PC.

Utilisation :
Importé par main.py pour configurer le réseau selon config.json.

## Fonction: disable_all_wifi

Désactive tous les modes Wi-Fi actifs (AP et STA).

Cette fonction est appelée avant de changer de mode
pour éviter les conflits entre interfaces.

## Fonction: start_ap

Démarre le point d'accès Wi-Fi (mode AP).

Args:
    cfg (dict): Configuration du point d'accès avec clés :
        - ssid (str): Nom du réseau AP.
        - password (str): Mot de passe.
        - channel (int): Canal Wi-Fi (par défaut 6).
        - hidden (bool): Réseau caché ou non.

Returns:
    network.WLAN: Objet AP actif si succès, sinon None.

## Fonction: start_sta

Connecte l'ESP en mode Station (STA) à un réseau existant.

Args:
    cfg (dict): Configuration STA avec clés :
        - ssid (str): Nom du réseau Wi-Fi.
        - password (str): Mot de passe.

Returns:
    network.WLAN: Objet STA connecté si succès, sinon None.
