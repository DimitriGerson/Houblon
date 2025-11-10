# networ_mock.py
class MockWLAN:
    STA_IF = 0
    AP_IF = 1
    AUTH_WPA_WPA2_PSK = 3

    def __init__(self, mode):
        self.mode = mode
        self._active = False
        self._connected = False
        self._cfg = {}

    def active(self, state=None):
        if state is None:
            return self._active
        self._active = state

    def connect(self, ssid, password):
        # Simule une connexion réussie uniquement si ssid non vide
        if ssid and password:
            self._connected = True

    def isconnected(self):
        return self._connected

    def ifconfig(self):
        return ("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8;8")

    def config(self, **kwargs):
        self._cfg.update(kwargs)
