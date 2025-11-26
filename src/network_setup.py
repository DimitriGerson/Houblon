#src/network_setup.py
#initialisation du server + creation des pages 
#actuellement le telechargement ne fonctionne pas il faudra le modifier
#penser a parametrer le html
#cette ligne est dupliquée cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n".encode())

"""
network_setup.py
Gestion du serveur web embarqué sur ESP (MicroPython).

Rôle :
- Démarrer un serveur HTTP simple pour l'ESP.
- Fournir des pages HTML pour :
    - Arrêter le serveur
    - Redémarrer l'ESP
    - Télécharger des fichiers JSON présents sur l'ESP
- Afficher des informations réseau (IP, mode).

Limitations :
- Téléchargement des fichiers à améliorer (actuellement basique).
- HTML statique, à paramétrer pour personnalisation.

Utilisation :
Appelé par main.py après configuration du réseau.
"""

import socket, os, time
try:
    import machine
except ImportError:
    # Mock minimal pour les tests sur pc
    class MockMachine:
        Pin = object

        @staticmethod
        def reset():
            print("Fake reset called")

    machine = MockMachine()


# Flag global pour arrêter le serveur
stop_server_flag = False

def stop_server():
    """
    Arrête le serveur web en définissant le flag global.
    """
    global stop_server_flag
    stop_server_flag = True

def start_server(net, mode, port=8080):    
    """
    Démarre un serveur HTTP minimaliste sur l'ESP.

    Args:
        net: Objet réseau (AP ou STA) configuré.
        mode (str): Mode réseau ("AP" ou "STA").
        port (int): Port d'écoute (par défaut 8080).

    Fonctionnalités :
    - Affiche l'IP et le mode.
    - Gère les requêtes GET pour :
        /stop      → Arrêter le serveur
        /restart   → Redémarrer l'ESP
        /download?file=xxx.json → Télécharger un fichier JSON
    - Génère une page HTML avec :
        - IP et mode
        - Liste des fichiers JSON disponibles
        - Boutons STOP et REDEMARRER

    Boucle :
    - Accepte les connexions jusqu'à ce que stop_server_flag soit True.
    """

    global stop_server_flag
    stop_server_flag = False #Réinitialise à chaque lancement

    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(addr)
    except OSError as e:
        print("Erreur bind port " + str(port) + " :", e)
        return

    s.listen(1)
    s.settimeout(1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    ip = net.ifconfig()[0]
    print("Serveur web actif sur http://" + ip + ":" + str(port))

    while not stop_server_flag:
        try:
            cl, addr = s.accept()
            request = cl.recv(1024).decode()
        except Exception:
            continue

        print("Client connecté depuis", addr)
        if not request:
            cl.close()
            continue
        request_line = request.split('\r\n')[0]   # ex: "GET /stop HTTP/1.1"

        # --- STOP via URL ---
        if request_line.startswith("GET /stop"):
            cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n".encode())
            cl.send("<html><body><h1>Serveur arrêté</h1></body></html>".encode())
            stop_server_flag = True
            cl.close()
            break

        # --- REDEMARRER via URL ---
        if request_line.startswith("GET /restart"):
            cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n".encode())
            cl.send("<html><body><h1>Redémarrage...</h1></body></html>".encode())
            cl.close()
            machine.reset() #Redémarre l'ESP
            break

        # --- Génération des liens fichiers ---
        files = [f for f in os.listdir() if f.endswith('.json')]
        file_links = ''.join(
            '<li><a href="/download?file=' + f + '">Télécharger ' + f + '</a></li>'
            for f in files
        )

        # --- Téléchargement ---
        if "/download?file=" in request:
            filename = request.split("/download?file=")[1].split(" ")[0]
            if filename in files:
                try:
                    with open(filename,"r", encoding="utf-8") as fp:
                        content = fp.read()
                    header = "HTTP/1.0 200 OK\r\nContent-Type: application/json; charset=utf-8\r\n\r\n"
                    cl.send(header.encode())
                    cl.send(content.encode("utf-8"))
                except Exception as e:
                    cl.send("HTTP/1.0 500 ERROR\r\n\r\nErreur lecture fichier.".encode())
            else:
                cl.send("HTTP/1.0 404 NOT FOUND\r\n\r\nFichier non trouvé.".encode())
            cl.close()
            continue

        # --- HTML (version allégée pour ESP8266 avec boutons STOP et REDEMARRER) ---
        html = (
            "<html><body>"
            "<h1>ESP8266 " + mode + "</h1>"
            "<p>IP : " + ip + "</p>"
            "<h3>Fichiers :</h3><ul>"
            + file_links +
            "</ul>"
            "<br>"
            "<form action='/stop' method='get'>"
               "<button type='submit'>STOP SERVEUR</button>"
            "</form>"
            "<form action='/restart' method='get'>"
            "<button type='submit'>REDEMARRER ESP</button>"
            "</form>"
            "</body></html>"
        )

        response = "HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf8\r\n\r\n" + html
        cl.send(response.encode())
        cl.close()
    print("Arret du serveur.")
    s.close()
