import socket, os, time

def start_server(net, mode, port=8080, timeout=300, stop_event=None):

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

    ip = net.ifconfig()[0]
    print("Serveur web actif sur http://" + ip + ":" + str(port))

    last_activity = time.time()

    while True:

        try:
            cl, addr = s.accept()
        except OSError:
            continue

        print("Client connecté depuis", addr)

        request = cl.recv(1024)
        if not request:
            cl.close()
            continue

        request = request.decode()

        # --- Génération des liens fichiers ---
        files = [f for f in os.listdir() if f.endswith(".json")]
        file_links = ""
        for f in files:
            file_links += '<li><a href="/download?file=' + f + '">Télécharger ' + f + '</a></li>'

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

        # --- HTML (version allégée pour ESP8266) ---
        html = (
            "<html><body>"
            "<h1>ESP8266 " + mode + "</h1>"
            "<p>IP : " + ip + "</p>"
            "<h3>Fichiers :</h3><ul>"
            + file_links +
            "</ul>"
            "</body></html>"
        )

        response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n" + html
        cl.send(response.encode())
        cl.close()
