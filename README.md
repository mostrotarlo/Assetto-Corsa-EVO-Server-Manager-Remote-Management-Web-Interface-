# 🚀 EVO Web Server Manager

A simple and powerful web interface to manage **Assetto Corsa EVO Dedicated Servers**.

👉 No configuration needed  
👉 Just run the `.exe` and start your server  

---

## 📥 Download

👉 **[Download latest version](https://github.com/mostrotarlo/Assetto-Corsa-EVO-Server-Manager-Remote-Management-Web-Interface-/releases/latest)**

✔ No installation required  
✔ Just run the `.exe`  
✔ Works locally and remotely  

---

## 📸 Preview

![Dashboard](Screenshot%201.png)
![Server](Screenshot%202.png)

---

## ⚡ Quick Start

1. Download the `.exe`
2. Run it
3. Open your browser:

http://127.0.0.1:5000

4. Login and start managing your servers

---

## ✨ Features

- Create and manage multiple EVO dedicated servers  
- Remote web interface  
- Start / stop single server  
- Start / stop all servers  
- Automatic server folder setup  

### Configuration:
- Tracks  
- Cars  
- Weather  
- Grip  
- Sessions  

### Automation:
- Auto-generate `-serverconfig`  
- Auto-generate `-seasondefinition`  

✔ Remote access via IP or domain (Caddy supported)

---

## 🌐 Remote Access (Caddy example)

```caddy
yourdomain.com {
    reverse_proxy localhost:5000
}
```

---

## 🧠 How it works

The application generates encoded configuration strings required by Assetto Corsa EVO:

- `-serverconfig`
- `-seasondefinition`

Then launches the official dedicated server automatically.

---

## ⚠️ Requirements (DEV only)

```bash
pip install -r requirements.txt
python main.py
```

---

## 📦 Build EXE

```bash
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "EVO Web Server Manager" ^
  --add-data "templates;templates" ^
  main.py
```

---

## ❤️ Support

💰 [Donate via PayPal](https://www.paypal.com/donate/?business=7AVK9RRTQHSNJ&no_recurring=1&currency_code=EUR)

Every contribution helps improve the project and add new features 🚀

---

## 📬 Contact

Discord: `mostrotarlo`

---

## 📜 License

MIT License

---

## 👤 Author

Developed by **Fabio Lombardi**

---

## 🔥 Roadmap

- Multi-server dashboard improvements  
- Better UI/UX  
- Auto-detect EVO installation  
- Discord integration  
- Server monitoring  

---

## ⚠️ Disclaimer

This project is **not affiliated with Kunos Simulazioni**.
