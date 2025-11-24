import ujson
import time

class Techniques:
    def __init__(self, config_file="config.json"):
        # Charger les capteurs depuis le fichier JSON
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

    # ==================== Méthodes des capteurs ====================

    def read_analog(self, pin):
        from machine import ADC, Pin
        sensor = ADC(Pin(pin))
        sensor.atten(ADC.ATTN_11DB)
        sensor.width(ADC.WIDTH_12BIT)
        return sensor.read()

    def read_digital(self, pin):
        from machine import Pin
        sensor = Pin(pin, Pin.IN)
        return sensor.value()

    def read_dht22(self, pin):
        from machine import Pin
        import dht
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
        """Appelle la fonction correspondante selon le type du capteur"""
        func = self.methods.get(sensor["type"])
        if func is None:
            raise ValueError("Type de capteur inconnu: " + sensor["type"])
        return func(sensor["pin"])

    def read_all(self):
        """Lit tous les capteurs définis dans la config"""
        results = []
        for s in self.sensors:
            value = self.read_sensor(s)
            results.append({"name": s["name"], "type": s["type"], "value": value})
        return results

    # ==================== Sauvegarde JSON ====================

    def save_measure(self, data, filename="data.json"):
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
