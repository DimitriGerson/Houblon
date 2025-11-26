# Documentation pour src/network_setup.py

network_setup.py
Gestion du serveur web embarqué sur ESP (MicroPython).

Rôle :
- Démarrer un serveur HTTP simple pour l'ESP.
- Fournir des pages HTML pour :
    - Arrêter le serveur
    - Redémarrer l'ESP
    - Télécharger des fichiers JSON présents sur l'ESP
- Afficher des informations réseau (IP, mode).

Limitations :
- Téléchargement des fichiers à améliorer (actuellement basique).
- HTML statique, à paramétrer pour personnalisation.

Utilisation :
Appelé par main.py après configuration du réseau.

## Fonction: stop_server

Arrête le serveur web en définissant le flag global.

## Fonction: start_server

Démarre un serveur HTTP minimaliste sur l'ESP.

Args:
    net: Objet réseau (AP ou STA) configuré.
    mode (str): Mode réseau ("AP" ou "STA").
    port (int): Port d'écoute (par défaut 8080).

Fonctionnalités :
- Affiche l'IP et le mode.
- Gère les requêtes GET pour :
    /stop      → Arrêter le serveur
    /restart   → Redémarrer l'ESP
    /download?file=xxx.json → Télécharger un fichier JSON
- Génère une page HTML avec :
    - IP et mode
    - Liste des fichiers JSON disponibles
    - Boutons STOP et REDEMARRER

Boucle :
- Accepte les connexions jusqu'à ce que stop_server_flag soit True.
