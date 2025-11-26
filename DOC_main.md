# Documentation pour src/main.py

main.py
Programme principal pour l'ESP32 sous MicroPython.

Rôle :
- Charger la configuration depuis config.json.
- Choisir le mode réseau (AP ou STA) et initialiser le Wi-Fi.
- Lancer le serveur web.
- Lire les capteurs et sauvegarder les mesures.
- Gérer les bascules et redémarrages en cas d'erreur.

Fonctionnalités :
- Mode AP : création d'un point d'accès et démarrage du serveur.
- Mode STA : connexion au réseau Wi-Fi existant, sinon fallback en AP.
- Lecture des capteurs via la classe Techniques.
- Sauvegarde des mesures dans data.json.
- Redémarrage sécurisé en cas d'échec critique.

Utilisation :
Exécuter ce fichier après boot.py. Il s'appuie sur :
- boot.py pour la configuration et les logs.
- wifi_utils.py pour la gestion Wi-Fi.
- technique_sensors.py pour la lecture des capteurs.
- network_setup.py pour le serveur web.

## Fonction: safe_restart

Redémarre l'ESP32 après un délai de 5 secondes.
Utilisé en cas d'erreur critique.

## Fonction: main

Point d'entrée principal :
- Charge la configuration
- Sélectionne le mode réseau (AP ou STA)
- Lance le serveur web
- Gère la lecture des capteurs et la sauvegarde des données
