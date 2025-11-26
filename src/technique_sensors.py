# src/technique_sensors.py
"""
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
"""
import ujson
import time
try:
    import dht
except ImportError:
    dht = None

class Techniques:    
    """
    Classe pour gérer la lecture des capteurs et la sauvegarde des mesures.
    """
    def __init__(self, config_file="config.json"):
        # Charger les capteurs depuis le fichier JSON        
        """
        Initialise la classe en chargeant la configuration des capteurs.

        Args:
            config_file (str): Chemin du fichier JSON contenant la configuration.
        """
        try:
            with open(config_file, "r") as f:
                cfg = ujson.load(f)
                self.sensors = cfg.get("sensors", [])
        except (OSError, ValueError):
            self.sensors = []

        # dictionnaire de fonctions selon le type de capteur
        self.methods = {
            "analog": self.read_analog,
            "digital": self.read_digital,
            "DHT22": self.read_dht22
        }

    # =====================================================
    # Abstraction pour machine (MicroPython)
    # =====================================================
    def get_machine(self):       
        """
        Retourne le module machine si disponible, sinon None.
        Utilisé pour la compatibilité avec MicroPython.
        """
        try:
            import machine
            return machine
        except ImportError:
            return None

    # ==================== Méthodes des capteurs ====================

    def read_analog(self, pin): 
        """
        Lit un capteur analogique sur la broche spécifiée.

        Args:
            pin (int): Numéro de la broche.

        Returns:
            int: Valeur analogique lue (0-4095) ou valeur simulée si machine indisponible.
        """
        machine = self.get_machine()
        if machine is None:
            return 123 # Valeur simulée pour tests 

        from machine import ADC, Pin
        sensor = ADC(Pin(pin))
        sensor.atten(ADC.ATTN_11DB)
        sensor.width(ADC.WIDTH_12BIT)
        return sensor.read()

    def read_digital(self, pin):        
        """
        Lit un capteur digital sur la broche spécifiée.

        Args:
            pin (int): Numéro de la broche.

        Returns:
            int: 0 ou 1 selon l'état du capteur.
        """
        machine = self.get_machine()
        if machine is None:
            return 0 # Valeur simulée pour tests

        from machine import Pin
        sensor = Pin(pin, Pin.IN)
        return sensor.value()

    def read_dht22(self, pin): 
        """
        Lit un capteur DHT22 (température et humidité).

        Args:
            pin (int): Numéro de la broche.

        Returns:
            dict: Données avec température, humidité et statut.
        """

        machine = self.get_machine()
        if machine is None or dht is None:
            return {"status": "error", "message": "machine non disponible"}

        Pin = machine.Pin
        sensor = dht.DHT22(Pin(pin))
        try:
            sensor.measure()
            return {
                "temperature": sensor.temperature(),
                "humidity": sensor.humidity(),
                "status": "ok"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ==================== Lecture de capteurs ====================

    def read_sensor(self, sensor):
        """
        Lit un capteur en fonction de son type.

        Args:
            sensor (dict): Dictionnaire avec "type" et "pin".

        Returns:
            Valeur lue par le capteur.
        """
        func = self.methods.get(sensor["type"])
        if func is None:
            raise ValueError("Type de capteur inconnu: " + sensor["type"])
        return func(sensor["pin"])

    def read_all(self):
        """
        Lit tous les capteurs définis dans la configuration.

        Returns:
            list: Liste de dictionnaires avec nom, type et valeur.
        """
        results = []
        for s in self.sensors:
            value = self.read_sensor(s)
            results.append({"name": s["name"], "type": s["type"], "value": value})
        return results

    # ==================== Sauvegarde JSON ====================

    def save_measure(self, data, filename="data.json"):      
        """
        Sauvegarde les mesures dans un fichier JSON avec horodatage.

        Args:
            data (list): Liste des mesures à sauvegarder.
            filename (str): Nom du fichier de sortie (par défaut data.json).
        """

        import json
        try:
            with open(filename, "r") as f:
                existing = json.load(f)
        except (OSError, ValueError):
            existing = []

        timestamp = time.time()
        for sensor_data in data:
            sensor_data["timestamp"] = timestamp
            existing.append(sensor_data)

        with open(filename, "w") as f:
            json.dump(existing, f)
