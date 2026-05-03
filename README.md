<<<<<<< HEAD
# EVO Web Server Manager 🚀

Remote web manager for **Assetto Corsa EVO Dedicated Servers**.

This tool allows communities and private server owners to create, configure, start and stop EVO dedicated servers from a browser, locally or remotely.

> This project is unofficial and is not affiliated with Kunos Simulazioni.

---

## Download

Download the latest compiled `.exe` from the **Releases** section.

No Python installation is required for the compiled version.

---

## Main Features

- Create and manage multiple EVO dedicated servers
- Copy the official EVO Dedicated Server folder automatically for each server instance
- Start / stop single servers
- Start / stop all servers
- Configure server name, ports, passwords and session type
- Configure track, layout, cars, weather, grip and time settings
- Generate EVO `-serverconfig` and `-seasondefinition` launch arguments automatically
- Local browser access
- Remote browser access through IP, domain or reverse proxy
- Caddy reverse proxy / subpath support

---

## Default Web Port

The application runs on:

```text
http://127.0.0.1:5000
```

When exposed on your LAN or behind a reverse proxy, it listens on:

```text
0.0.0.0:5000
```

---

## Quick Start - EXE Version

1. Download `EVO Web Server Manager.exe` from Releases.
2. Run the executable.
3. Select your official **Assetto Corsa EVO Dedicated Server** folder.
4. Set the login password.
5. Press **Start Web App**.
6. Open:

```text
http://127.0.0.1:5000
```

Default password, if unchanged:

```text
admin
```

---

## Remote Access Example with Caddy

Example using a subpath like:

```text
https://yourdomain.com/evo
```

Caddyfile:

```caddy
yourdomain.com {
    handle /evo* {
        reverse_proxy 127.0.0.1:5000
    }
}
```

In the app setup window set:

```text
Base path: /evo
Public URL: https://yourdomain.com/evo
```

Then open:

```text
https://yourdomain.com/evo
```

---

## Run from Source

Requirements:

- Windows
- Python 3
- Assetto Corsa EVO Dedicated Server installed from Steam

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
=======
# 🚀 EVO Web Server Manager

A modern web interface to manage **Assetto Corsa EVO Dedicated Servers** locally or remotely.

---

## 📥 Download

👉 **[Download latest version](https://github.com/TUOUSERNAME/EVO-Web-Server-Manager/releases)**

✔ No installation required
✔ Just run the `.exe`

---

## 📸 Preview

![Dashboard](screenshot.png)

---

## ⚡ Quick Start

1. Download the `.exe`
2. Run it
3. Open your browser:

```
http://127.0.0.1:5060
```

4. Login and start managing your servers

---

## ✨ Features

* Create and manage multiple EVO servers
* Remote web interface
* Start / stop single server
* Start / stop all servers
* Automatic server folder setup
* Configure:

  * Tracks
  * Cars
  * Weather
  * Grip
  * Sessions
* Auto-generate:

  * `-serverconfig`
  * `-seasondefinition`
* Remote access via IP or domain (Caddy supported)

---

## 🌐 Remote Access (Caddy example)

```caddy
yourdomain.com {
    reverse_proxy localhost:5060
}
```

---

## 🧠 How it works

The app generates encoded configuration strings required by EVO:

* `-serverconfig`
* `-seasondefinition`

Then launches the official dedicated server automatically.

---

## ⚠️ Requirements (DEV only)

If you want to run from source:

```
pip install -r requirements.txt
>>>>>>> 70da6f3f4fc4ae3fabf1c980dab525628d850bcf
python main.py
```

---

<<<<<<< HEAD
## Build the EXE

Use the included build script:

```bat
build_exe.bat
```

The final executable will be generated here:

```text
dist/EVO Web Server Manager.exe
```

Manual PyInstaller command:

```bat
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "EVO Web Server Manager" ^
  --add-data "templates;templates" ^
  --hidden-import werkzeug.middleware.proxy_fix ^
  main.py
=======
## 📦 Build EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "EVO Server Manager" main.py
>>>>>>> 70da6f3f4fc4ae3fabf1c980dab525628d850bcf
```

---

<<<<<<< HEAD
## Repository Structure

```text
EVO-Web-Server-Manager/
├── main.py
├── web_server.py
├── evo_encoder.py
├── evo_mapper.py
├── requirements.txt
├── build_exe.bat
├── START.bat
├── app_config.example.json
├── templates/
│   ├── login.html
│   ├── index.html
│   ├── server.html
│   └── settings.html
└── servers/
    └── .gitkeep
```

---

## Important Notes

- The tool uses port **5000**.
- Each created server gets its own copied EVO Dedicated Server folder.
- Server data is stored locally in the `servers` folder.
- Running server PIDs are stored in `running_servers.json`.
- Do not upload your personal `app_config.json` if it contains private paths or passwords.

---

## License

MIT License.

---

## Author

Developed by **Fabio Lombardi**.
=======
## ❤️ Support

If you like the project and want to support development:

👉 [PayPal link]

---

## 📜 License

MIT License

---

## 👤 Author

Developed by **Fabio Lombardi**

---

## 🔥 Roadmap

* Multi-server dashboard improvements
* Better UI/UX
* Auto-detect EVO installation
* Discord integration
* Server monitoring

---

## ⚠️ Disclaimer

This project is **not affiliated with Kunos Simulazioni**.

---

## 🌍 Community

Feel free to share feedback, ideas or improvements!
>>>>>>> 70da6f3f4fc4ae3fabf1c980dab525628d850bcf
