#!/bin/bash

# --- Vérification root ---
if [ "$EUID" -ne 0 ]; then
  echo "Veuillez exécuter ce script en root (sudo)."
  exit 1
fi

echo "=== Mise à jour du système ==="
apt update && apt upgrade -y

echo "=== Installation de Mosquitto ==="
apt install -y mosquitto mosquitto-clients

echo "=== Activation du service Mosquitto ==="
systemctl enable mosquitto
systemctl start mosquitto

# --- Création d’un utilisateur MQTT ---
echo ""
read -p "Nom d'utilisateur MQTT (par défaut 'mqttuser'): " MQTT_USER
MQTT_USER=${MQTT_USER:-mqttuser}

read -s -p "Mot de passe MQTT pour l'utilisateur $MQTT_USER : " MQTT_PASS
echo ""

echo "=== Création de l'utilisateur MQTT ==="
mosquitto_passwd -c -b /etc/mosquitto/passwd "$MQTT_USER" "$MQTT_PASS"

# --- Configuration de Mosquitto ---
echo "=== Configuration de Mosquitto ==="
cat > /etc/mosquitto/conf.d/default.conf <<EOF
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
EOF

echo "=== Redémarrage du service ==="
systemctl restart mosquitto

# --- Test ---
echo ""
echo "=== Test du serveur MQTT ==="
echo "Pour tester en local, ouvrez un autre terminal et tapez :"
echo "  mosquitto_sub -h localhost -t test/topic -u $MQTT_USER -P $MQTT_PASS"
echo ""
echo "Puis envoyez un message avec :"
echo "  mosquitto_pub -h localhost -t test/topic -m 'Hello MQTT' -u $MQTT_USER -P $MQTT_PASS"
echo ""
echo "Installation terminée avec succès !"
