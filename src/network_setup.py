import network, socket, os, time, json

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        print("Erreur lecture config.json")
        return {}

def setup_network():
    config = load_config()
    mode = config.get("mode", "AP").upper()

    if mode == "AP":
        ap_cfg = config.get("ap", {})
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(
            essid=ap_cfg.get("ssid", "ESP32_AP"),
            password=ap_cfg.get("password", "12345678"),
            channel=ap_cfg.get("channel", 6),
            hidden=ap_cfg.get("hidden", False)
        )
        while not ap.active():
            pass
        print("AP actif :", ap.ifconfig())
        return ap, "AP"

    elif mode == "STA":
        sta_cfg = config.get("sta", {})
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if sta_cfg.get("ssid") and sta_cfg.get("password"):
            sta.connect(sta_cfg["ssid"], sta_cfg["password"])
            while not sta.isconnected():
                print("Connexion au Wi-Fi…")
                time.sleep(1)
            print("STA connecté :", sta.ifconfig())
            return sta, "STA"
        else:
            print("STA sans SSID, fallback AP")
            return setup_network()

def start_server(net, mode, timeout=300):
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    s.settimeout(1)
    print("Serveur web actif sur port 80")

    ip = net.ifconfig()[0]
    last_activity = time.time()

    while True:
        if time.time() - last_activity > timeout:
            print("Aucune activité, arrêt du serveur.")
            s.close()
            break

        try:
            cl, addr = s.accept()
        except OSError:
            continue

        print("Client connecté depuis", addr)
        request = cl.recv(1024)
        request = str(request)
        last_activity = time.time()

        files = [f for f in os.listdir() if f.endswith(".json")]
        file_links = "".join([
            f'<li><a href="/download?file={f}">⬇️ Télécharger {f}</a></li>'
            for f in files
        ])

        # ✅ Gestion du téléchargement
        if "/download?file=" in request:
            try:
                filename = request.split("/download?file=")[1].split(" ")[0]
                if filename in files:
                    with open(filename, "r") as file:
                        content = file.read()
                    headers = (
                        "HTTP/1.0 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        f"Content-Disposition: attachment; filename={filename}\r\n\r\n"
                    )
                    cl.send(headers + content)
                else:
                    cl.send("HTTP/1.0 404 NOT FOUND\r\n\r\nFichier non trouvé.")
            except Exception as e:
                cl.send("HTTP/1.0 500 ERROR\r\n\r\nErreur interne.")
            cl.close()
            continue

        # ✅ Page principale
        html = f"""
        <html>
        <head>
            <title>ESP32 Logs</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f3f3f3;
                    color: #333;
                }}
                .card {{
                    background: white;
                    padding: 16px;
                    border-radius: 12px;
                    max-width: 420px;
                    margin: 40px auto;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                }}
                h1 {{ text-align: center; }}
                ul {{ list-style: none; padding: 0; }}
                li {{ margin: 8px 0; }}
                a {{
                    text-decoration: none;
                    color: #0066cc;
                    background: #e0e8ff;
                    padding: 6px 10px;
                    border-radius: 6px;
                }}
                a:hover {{ background: #cbd8ff; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>ESP32 ({mode})</h1>
                <p><strong>Adresse IP :</strong> {ip}</p>
                <p><strong>Dernière activité :</strong> {time.strftime('%H:%M:%S')}</p>
                <hr>
                <h3>Fichiers disponibles :</h3>
                <ul>{file_links}</ul>
            </div>
        </body>
        </html>
        """

        response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n" + html
        cl.send(response)
        cl.close()
