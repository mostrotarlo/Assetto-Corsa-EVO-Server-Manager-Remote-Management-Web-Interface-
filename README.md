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
python main.py
```

---

## 📦 Build EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "EVO Server Manager" main.py
```

---

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
