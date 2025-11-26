# Documentation pour src/technique_sensors.py

technique_sensors.py
Gestion des capteurs pour l'ESP (MicroPython).

Rôle :
- Charger la configuration des capteurs depuis un fichier JSON.
- Fournir des méthodes pour lire différents types de capteurs :
    - Analogiques
    - Digitaux
    - DHT22 (température et humidité)
- Sauvegarder les mesures dans un fichier JSON avec horodatage.

Utilisation :
Instancier la classe Techniques avec le chemin du fichier de configuration.
Exemple :
    tech = Techniques("config.json")
    data = tech.read_all()
    tech.save_measure(data)
