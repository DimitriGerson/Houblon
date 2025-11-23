import types
import pytest
from unittest.mock import MagicMock, mock_open

import network_setup

def test_stop_server():
    # Reinitialiser la variable globale avant le test
    network_setup.stop_server_flag = False

    network_setup.stop_server()

    assert network_setup.stop_server_flag is True

def test_start_server_basic_html(monkeypatch):

    # --- Fake network interface ---
    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    # --- Fake socket client ---
    fake_client = MagicMock()
    fake_client.recv.return_value = b"GET / HTTP/1.1"
    fake_client.send = MagicMock()

    # Lorsqu'on ferme, rien à faire
    fake_client.close = MagicMock()

    # --- Fake server socket ---
    fake_server = MagicMock()
    fake_server.accept.return_value = (fake_client, ("1.2.3.4", 1234))
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()

    # --- Mock de socket.socket() ---
    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)

    # --- Mock getaddrinfo ---
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    # --- Mock os.listdir pour générer 2 fichiers json ---
    monkeypatch.setattr(network_setup.os, "listdir",
                        lambda: ["config.json", "data.json", "readme.txt"])

    # --- Empêcher la boucle infinie : 1 requête puis exit ---
    calls = {"n": 0}

    def fake_accept():
        calls["n"] += 1
        if calls["n"] == 1:
            return (fake_client, ("1.2.3.4", 1234))
        raise KeyboardInterrupt  # quitte start_server proprement

    fake_server.accept.side_effect = fake_accept

    # --- Exécution ---
    with pytest.raises(KeyboardInterrupt):
        network_setup.start_server(fake_net, "AP")

    # --- Vérification que le HTML a été envoyé ---
    sent_data = b"".join(
        call.args[0] for call in fake_client.send.call_args_list
    ).decode()

    assert "<h1>ESP8266 AP</h1>" in sent_data
    assert 'Télécharger config.json' in sent_data
    assert 'Télécharger data.json' in sent_data

def test_start_server_download(monkeypatch):

    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    # --- Fake JSON file ---
    monkeypatch.setattr(network_setup.os, "listdir",
                        lambda: ["cfg.json"])

    fake_file = mock_open(read_data='{"ok": true}')
    monkeypatch.setattr(network_setup, "open", fake_file, raising=False)


    # --- Fake socket client ---
    fake_client = MagicMock()
    fake_client.recv.return_value = b"GET /download?file=cfg.json HTTP/1.1"
    fake_client.send = MagicMock()
    fake_client.close = MagicMock()

    # --- Fake server ---
    fake_server = MagicMock()
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()

    # Boucle : 1 accept → stop
    fake_server.accept.side_effect = [
        (fake_client, ("1.2.3.4", 1234)),
        KeyboardInterrupt
    ]

    # Mock socket.socket()
    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    with pytest.raises(KeyboardInterrupt):
        network_setup.start_server(fake_net, "AP")

    # Vérifie que la réponse JSON a été envoyée
    sent_raw = b"".join(
        call.args[0].encode() if isinstance(call.args[0], str) else call.args[0]
        for call in fake_client.send.call_args_list
    )

    assert b"Content-Type: application/json" in sent_raw
    assert b'{"ok": true}' in sent_raw

def test_start_server_bind_fails(monkeypatch):
    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("1.1.1.1", "", "", "")

    fake_socket = MagicMock()

    def fake_bind(addr):
        raise OSError("port in use")

    fake_socket.bind = fake_bind

    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_socket)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    # NE DOIT PAS lever d’erreur
    result = network_setup.start_server(fake_net, "AP")

    assert result is None

def test_start_server_accept_timeout(monkeypatch):

    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    fake_server = MagicMock()
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()
    fake_server.accept.side_effect = [OSError, KeyboardInterrupt]

    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    with pytest.raises(KeyboardInterrupt):
        network_setup.start_server(fake_net, "AP")

    # Vérifie que accept a bien été appelé plusieurs fois
    assert fake_server.accept.call_count == 2
def test_start_server_empty_request(monkeypatch):
    """Teste le cas où recv() renvoie b'' (aucune donnée) et vérifie que cl.close() est appelé."""

    # --- Fake réseau ---
    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    # --- Fake client socket ---
    fake_client = MagicMock()
    fake_client.recv.return_value = b""      # <<< CAS À TESTER : aucune donnée
    fake_client.close = MagicMock()

    # --- Fake server socket ---
    fake_server = MagicMock()
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()

    # Pour stopper la boucle après 1 tour  
    fake_server.accept.side_effect = [
        (fake_client, ("1.2.3.4", 1234)),
        KeyboardInterrupt          # STOP après la première boucle
    ]

    # --- Mock de socket ---
    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    # --- Mock liste de fichiers pour éviter soucis ---
    monkeypatch.setattr(network_setup.os, "listdir", lambda: [])

    with pytest.raises(KeyboardInterrupt):
        network_setup.start_server(fake_net, "AP")

    # Vérifie que close() a été appelé car request était vide
    fake_client.close.assert_called_once()

def test_start_server_download_404(monkeypatch):
    """Teste le cas où le fichier demandé n'existe pas -> réponse 404."""

    # --- Fake réseau ---
    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    # --- Fake système de fichiers ---
    # Le serveur verra seulement "cfg.json" -> "fake.json" doit faire un 404
    monkeypatch.setattr(network_setup.os, "listdir",
                        lambda: ["cfg.json"])

    # --- Fake client socket ---
    fake_client = MagicMock()
    fake_client.recv.return_value = b"GET /download?file=fake.json HTTP/1.1"
    fake_client.close = MagicMock()
    fake_client.send = MagicMock()

    # --- Fake server socket ---
    fake_server = MagicMock()
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()

    # Accepte UNE connexion → puis on stoppe avec KeyboardInterrupt
    fake_server.accept.side_effect = [
        (fake_client, ("1.2.3.4", 1234)),
        KeyboardInterrupt
    ]

    # Mock socket.socket() + getaddrinfo()
    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    with pytest.raises(KeyboardInterrupt):
        network_setup.start_server(fake_net, "AP")

    # --- Vérification : le serveur doit avoir envoyé un 404 ---
    sent_raw = b"".join(
        (arg.encode() if isinstance(arg, str) else arg)
        for call in fake_client.send.call_args_list
        for arg in call.args
    )

    assert b"404 NOT FOUND" in sent_raw
    assert b"Fichier non trouve" in sent_raw or b"Fichier non trouv" in sent_raw

def test_start_server_stop(monkeypatch):
    # --- Fake réseau ---
    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    # --- Fake socket client ---
    fake_client = MagicMock()
    fake_client.recv.return_value = b"GET /stop HTTP/1.1"
    fake_client.send = MagicMock()
    fake_client.close = MagicMock()

    # --- Fake server socket ---
    fake_server = MagicMock()
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()

    # 1 accept() -> stop après
    fake_server.accept.side_effect = [
        (fake_client, ("1.2.3.4", 1234)),
        KeyboardInterrupt  # pour sortir de la boucle
    ]

    # --- Mock socket.socket + getaddrinfo ---
    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    # --- Lancer le serveur ---
    network_setup.start_server(fake_net, "AP")

    # --- Vérification de l'envoi HTTP ---
    sent_raw = b"".join(
        arg.encode() if isinstance(arg, str) else arg
        for call in fake_client.send.call_args_list
        for arg in call.args
    )

    assert b"HTTP/1.0 200 OK" in sent_raw
    assert b"Serveur arr" in sent_raw  # éviter accents exacts

    # --- Vérifie stop_server_flag activé ---
    assert network_setup.stop_server_flag is True

    # --- Vérifie fermeture du client ---
    fake_client.close.assert_called_once()

def test_start_server_restart(monkeypatch):
    # --- Fake réseau ---
    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    # --- Mock machine.reset() pour éviter un vrai reboot ---
    mock_reset = MagicMock()
    monkeypatch.setattr(network_setup.machine, "reset", mock_reset)

    # --- Fake client socket ---
    fake_client = MagicMock()
    fake_client.recv.return_value = b"GET /restart HTTP/1.1"
    fake_client.send = MagicMock()
    fake_client.close = MagicMock()

    # --- Fake server socket ---
    fake_server = MagicMock()
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()

    fake_server.accept.side_effect = [
        (fake_client, ("1.2.3.4", 1234)),
        KeyboardInterrupt    # pour éviter une boucle infinie
    ]

    # --- Mock socket.socket + getaddrinfo ---
    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    # --- Lancer le serveur  ---
    network_setup.start_server(fake_net, "AP")

    # --- Vérifier l'envoi HTTP ---
    sent_raw = b"".join(
        arg.encode() if isinstance(arg, str) else arg
        for call in fake_client.send.call_args_list
        for arg in call.args
    )

    assert b"HTTP/1.0 200 OK" in sent_raw
    assert b"Red" in sent_raw  # pour éviter accents exacts

    # --- Vérifier que reset a bien été appelé ---
    mock_reset.assert_called_once()

    # --- Vérifier que le client a bien été fermé ---
    fake_client.close.assert_called_once()

def test_start_server_download_500(monkeypatch):
    # --- Fake réseau ---
    fake_net = MagicMock()
    fake_net.ifconfig.return_value = ("192.168.4.1", "", "", "")

    # --- Fake liste de fichiers ---
    monkeypatch.setattr(network_setup.os, "listdir", lambda: ["cfg.json"])

    # --- Mock open() pour forcer une exception ---
    def fake_open(*args, **kwargs):
        raise IOError("Erreur lecture fichier")
    monkeypatch.setattr(network_setup, "open", fake_open, raising=False)

    # --- Fake client socket ---
    fake_client = MagicMock()
    fake_client.recv.return_value = b"GET /download?file=cfg.json HTTP/1.1"
    fake_client.send = MagicMock()
    fake_client.close = MagicMock()

    # --- Fake serveur ---
    fake_server = MagicMock()
    fake_server.bind = MagicMock()
    fake_server.listen = MagicMock()
    fake_server.settimeout = MagicMock()
    
    calls = {"n":0}
    def fake_accept():
        calls["n"] +=1
        if calls["n"] == 1:
            return fake_client, ("1.2.3.4", 1234)

        # Arrêter le serveur proprement après le 1er tour
        network_setup.stop_server_flag = True
        return fake_client, ("1.2.3.4", 1234)

    fake_server.accept.side_effect = fake_accept

    # --- Mock socket.socket() + getaddrinfo() ---
    monkeypatch.setattr(network_setup.socket, "socket", lambda: fake_server)
    monkeypatch.setattr(network_setup.socket, "getaddrinfo",
                        lambda *args: [(None, None, None, None, ("0.0.0.0", 8080))])

    # --- Exécution du serveur (il NE bloque plus) ---
    network_setup.start_server(fake_net, "AP")

    # --- Vérification que le serveur a renvoyé le 500 ---
    sent_raw = b"".join(
        arg.encode() if isinstance(arg, str) else arg
        for call in fake_client.send.call_args_list
        for arg in call.args
    )

    assert b"HTTP/1.0 500 ERROR" in sent_raw
    assert b"Erreur lecture fichier" in sent_raw

    # --- Vérifie que le client a été fermé ---
    assert fake_client.close.call_count >=1 # au moins un appel
