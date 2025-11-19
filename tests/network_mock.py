# network_mock.py
# Simulation du module 'network' de MicroPython pour tests sur PC
STA_IF = 0
AP_IF = 1
AUTH_WPA_WPA2_PSK = 3

class MockWLAN:

    def __init__(self, mode):
        self.mode = mode
        self._active = False
        self._connected = False
        self._cfg = {}
        #IP différente selon mode
        self._ip = "192.168.4.1" if mode == AP_IF else "192.168.1.42"

    def active(self, state=None):
        if state is None:
            return self._active
        self._active = state

    def connect(self, ssid, password):
        # Simule une connexion réussie uniquement si ssid non vide
        if ssid and password:
            self._connected = True
        else:
            self._connected = False

    def isconnected(self):
        return self._connected

    def ifconfig(self):
        return ("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8")

    def config(self, **kwargs):
        self._cfg.update(kwargs)
# --- Fonction globale attendue par wifi_utils ---
def wlan(mode):
    return MockWLAN(mode)
