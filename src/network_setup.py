import socket, os, time
try:
    import machine
except ImportError:
    # Mock minimal pour les tests sur pc
    class MockMachine:
        Pin = object

    machine = MockMachine()


# Flag global pour arrêter le serveur
stop_server_flag = False

def stop_server():
    global stop_server_flag
    stop_server_flag = True

def start_server(net, mode, port=8080):
    global stop_server_flag
    stop_server_flag = False #Réinitialise à chaque lancement

    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(addr)
    except OSError as e:
        print("Erreur bind port " + str(port) + " :", e)
        return

    s.listen(1)
    s.settimeout(1)

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

        # --- STOP via URL ---
        if "GET /stop" in request:
            cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
            cl.send("<html>>body><h1>Serveur arrêté</h1></body></html>")
            stop_server_flag = True
            cl.close()
            break

        # --- REDEMARRER via URL ---
        if "GET /restart" in request:
            cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
            cl.send("<html><body><h1>Redémarrage...</h1></body></html>")
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
                with open(filename) as fp:
                    content = fp.read()
                header = "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n"
                cl.send(header)
                cl.send(content)
            else:
                cl.send("HTTP/1.0 404 NOT FOUND\r\n\r\nFichier non trouvé.")
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
               "<button type='submit'>STOP SERVEUR</buton>"
            "</form>"
            "</body></html>"
        )

        response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n" + html
        cl.send(response.encode())
        cl.close()
    print("Arret du serveur.")
    s.close()
