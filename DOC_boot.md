# Documentation pour src/boot.py

boot.py
Initialisation minimale pour l'ESP (MicroPython).
- Gestion des logs
- Chargement de la configuration avec fallback
- Préparation avant main.py

## Fonction: log

Écrit un message dans le log et l'affiche.

Args:
    msg (str): Message à enregistrer.

## Fonction: clear_old_log

Supprime le fichier log s'il dépasse 100 Ko.

## Fonction: load_config

Charge la configuration depuis config.json.

Returns:
    dict: Configuration complète ou valeurs par défaut (fallback).

## Fonction: main

Point d'entrée du boot.
- Nettoie les logs
- Affiche un message de démarrage
