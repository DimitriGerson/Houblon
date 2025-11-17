#!/bin/bash

set -e  # Stop si une commande échoue

echo "=== Mise à jour de la branche main ==="
git checkout main
git pull origin main

echo "=== Lancement des tests ==="
pytest tests/
if [ $? -ne 0 ]; then
    echo "❌ Tests échoués. Déploiement annulé."
    exit 1
fi

echo "=== Tests OK. Déploiement sur ESP8266... ==="

# Détecter auto le port USB (modifie selon ton matériel)
PORT=$(ls /dev/ttyUSB* 2>/dev/null)

if [ -z "$PORT" ]; then
    echo "❌ Aucun port USB détecté."
    exit 1
fi

echo "→ Port détecté : $PORT"

# Effacer les anciens fichiers (optionnel)
mpremote connect $PORT fs wipe

# Envoyer les fichiers
for file in src/*.py; do
    echo "Envoi de $file"
    mpremote connect $PORT fs put "$file"
done

echo "=== Déploiement terminé ✔️ ==="
