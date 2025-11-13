import unittest
import socket
import threading
import time
import os
import threading

import network_setup  # ton fichier à tester

# === MOCK du Wi-Fi (pour remplacer network.WLAN) ===
class MockNetwork:
    def ifconfig(self):
        # retourne une IP simulée
        return ("127.0.0.1", "255.255.255.0", "127.0.0.1", "8.8.8.8")

# === TESTS UNITAIRES ===
class TestStartServer(unittest.TestCase):

    def setUp(self):
        # Crée un fichier JSON temporaire pour les tests
        with open("test.json", "w") as f:
            f.write('{"test": "ok"}')

    def tearDown(self):
        # Nettoyage après chaque test
        if os.path.exists("test.json"):
            os.remove("test.json")

    def test_server_serves_main_page(self):
        """Le serveur doit renvoyer une page HTML valide"""
        net = MockNetwork()

        # Lance le serveur dans un thread séparé
        stop_event = threading.Event()
        server_thread = threading.Thread(
            target=network_setup.start_server,
            args=(net, "AP", 10, 8081, stop_event),
            daemon=True
        )
        server_thread.start()
        for _ in range(20):
            try:
                s = socket.socket()
                s.connect(("127.0.0.1", 8081))
                s.close()
                break # le serveur est prêt
            except ConnectionRefusedError:
                time.sleep(0.5)  # laisse le temps au serveur de démarrer
        else:
            raise RuntimeError("Le server ne s'est pas lancé à temps")
        # Se connecte au serveur
        s = socket.socket()
        s.connect(("127.0.0.1", 8081))
        s.send(b"GET / HTTP/1.0\r\n\r\n")
        data = s.recv(4096).decode()
        s.close()
        # après la requete HTTP
        stop_event.set() #après la requête HTTP
        server_thread.join()
        self.assertIn("ESP32 (AP)", data)
        self.assertIn("Fichiers disponibles", data)

    def test_server_download_json(self):
        """Le serveur doit renvoyer le contenu du fichier JSON demandé"""
        net = MockNetwork()
        stop_event = threading.Event()
        # Lance le serveur dans un thread séparé
        server_thread = threading.Thread(
            target=network_setup.start_server,
            args=(net, "AP", 10,8081, stop_event),
            daemon=True
        )
        server_thread.start()
        time.sleep(0.5)

        s = socket.socket()
        s.connect(("127.0.0.1", 8081))
        s.send(b"GET /download?file=test.json HTTP/1.0\r\n\r\n")
        data = s.recv(4096).decode()
        s.close()
        stop_event.set()
        server_thread.join()
        self.assertIn('"test": "ok"', data)

    def test_server_timeout(self):
        """Le serveur doit s'arrêter après inactivité"""
        net = MockNetwork()
        start_time = time.time()
        network_setup.start_server(net, "AP", timeout=2)
        duration = time.time() - start_time
        # Il devrait s'arrêter au bout d'environ 2 secondes
        self.assertLess(duration, 5)


if __name__ == "__main__":
    unittest.main()
