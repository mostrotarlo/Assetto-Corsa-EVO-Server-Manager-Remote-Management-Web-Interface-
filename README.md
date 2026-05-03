# Web EVO Server Manager 🚀

Remote web manager for **Assetto Corsa EVO Dedicated Servers**.

This tool allows communities and private server owners to manage Assetto Corsa EVO dedicated servers from a browser, locally or remotely.

---

## Features

- Create and manage multiple EVO dedicated servers
- Remote web interface
- Start / stop single servers
- Start / stop all servers
- Configure server name, ports, passwords and sessions
- Configure tracks, cars, weather, grip and time settings
- Auto-generate `-serverconfig` and `-seasondefinition` commands
- Designed for private servers and communities

---

## Remote Management

The app can be exposed remotely using:

- public IP + port forwarding
- dynamic DNS
- reverse proxy such as Caddy

Example:

```text
http://YOUR_PUBLIC_IP:5000/evo/
https://your-domain.com/evo/
