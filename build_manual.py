"""Build the English v1.5.0 user manual PDF."""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "dist" / "EVO-Web-Server-Manager-v1.5.0" / "EVO Web Server Manager Manual.pdf"


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(18 * mm, 12 * mm, "EVO Web Server Manager v1.5.0")
    canvas.drawRightString(192 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#b90000"), spaceAfter=12))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Heading2"], alignment=TA_CENTER, textColor=colors.HexColor("#444444"), spaceAfter=18))
styles.add(ParagraphStyle(name="H1Red", parent=styles["Heading1"], textColor=colors.HexColor("#b90000"), spaceBefore=8, spaceAfter=9))
styles.add(ParagraphStyle(name="H2Dark", parent=styles["Heading2"], textColor=colors.HexColor("#292929"), spaceBefore=7, spaceAfter=6))
styles.add(ParagraphStyle(name="BodyRoomy", parent=styles["BodyText"], leading=14, spaceAfter=7))
styles.add(ParagraphStyle(name="Note", parent=styles["BodyText"], backColor=colors.HexColor("#f2f2f2"), borderColor=colors.HexColor("#bbbbbb"), borderWidth=0.5, borderPadding=7, leading=13, spaceBefore=5, spaceAfter=9))


def p(text, style="BodyRoomy"):
    return Paragraph(text, styles[style])


def bullets(items):
    return [Paragraph(f"• {item}", styles["BodyRoomy"]) for item in items]


story = [
    Spacer(1, 35 * mm), p("EVO Web Server Manager", "TitleCenter"),
    p("User Manual - Version 1.5.0", "Subtitle"), Spacer(1, 12 * mm),
    p("Remote management and Windows service launcher for Assetto Corsa EVO Dedicated Server.", "Note"),
    Spacer(1, 35 * mm), p("Developed by Fabio Lombardi", "Subtitle"), PageBreak(),
    p("1. What is new in version 1.5.0", "H1Red"),
    p("Version 1.5.0 separates the desktop controls from the background server engine. This keeps the web interface and dedicated servers running even when the Control Panel window is closed."),
    *bullets([
        "Control Panel: edits application settings and starts, stops or restarts the Engine.",
        "Engine: runs the web interface, watchdog and dedicated-server processes without a desktop window.",
        "Windows service mode: starts the Engine during Windows boot, before a user signs in.",
        "Direct mode and start-at-sign-in mode remain available.",
        "Existing app_config.json and servers folders are compatible and preserved by the installer.",
    ]),
    p("Important", "H2Dark"),
    p("Keep both executable files in the same permanent folder. Do not move or rename the Engine after installing it as a Windows service.", "Note"),
    p("2. Updating from version 1.4.x", "H1Red"),
    *bullets([
        "Stop all dedicated servers and close the old manager.",
        "Run EVO Web Server Manager v1.5.0 Installer.exe.",
        "Select the folder containing the previous installation.",
        "Confirm the summary. The installer copies the two new executables and this manual.",
        "app_config.json, servers, logs and results are not deleted or overwritten.",
        "Recognized legacy v1.4 executable files are removed after the new files are copied.",
    ]), PageBreak(),
    p("3. Control Panel", "H1Red"),
    p("Open EVO Web Server Manager Control Panel.exe. Opening it while the Engine is already running does not start a duplicate process."),
]

rows = [
    [p("Control", "H2Dark"), p("Purpose", "H2Dark")],
    [p("Save Settings"), p("Stores network, paths, authentication, watchdog and startup preferences.")],
    [p("Start / Restart Engine"), p("Starts direct mode or restarts the configured Windows service.")],
    [p("Stop Engine"), p("Stops the direct Engine or the Windows service.")],
    [p("Open Web Interface"), p("Opens the public URL when configured, otherwise the local address.")],
]
table = Table(rows, colWidths=[55 * mm, 112 * mm], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.extend([
    table, Spacer(1, 5 * mm),
    p("Closing the Control Panel does not stop the Engine or the web interface.", "Note"),
    p("4. Startup modes", "H1Red"),
    p("Direct", "H2Dark"), p("The Engine starts only when Start / Restart Engine is pressed. Use this for initial testing."),
    p("Start after user sign-in", "H2Dark"), p("Windows launches the Engine after the configured user signs in. This mode does not run before the sign-in screen."),
    p("Windows service", "H2Dark"), p("The Engine starts automatically with Windows under the LocalSystem account. Administrator approval is required when installing, removing, starting or stopping the service."),
    p("The two automatic startup checkboxes are mutually exclusive.", "Note"), PageBreak(),
    p("5. Web interface", "H1Red"),
    p("The dashboard lists servers in numerical order. From each server card you can open its live page, edit settings, start or stop it, copy its command, clone its race configuration or delete it."),
    p("Creating and cloning servers", "H2Dark"),
    *bullets([
        "Add Server creates a clean configuration with automatically assigned network ports.",
        "Clone copies race, track, car, session and weather settings from the selected server.",
        "Ports, server identity, runtime state and log path are regenerated for the new server.",
    ]),
    p("Dedicated log files", "H2Dark"),
    p("Every server has a Dedicated log file path. The default is servers/server_X/serverConfig/Assetto Corsa EVO Server.txt. The Engine automatically passes -log_file when it launches the official server."),
    p("Additional dedicated server arguments", "H2Dark"),
    p("Use this field only for arguments supported by the current Kunos dedicated server. Invalid or duplicated arguments can prevent the server from starting."),
    p("Mandatory pit stop", "H2Dark"),
    p("Mandatory pit stop options are available only for timed races longer than 20 minutes (more than 1200 seconds), matching the current dedicated-server limitation."),
    p("6. Watchdog", "H1Red"),
    p("When enabled, the watchdog checks servers that should be running. After an unexpected crash it attempts no more than two automatic restarts inside the configured time window. Intentional stops are not restarted."), PageBreak(),
    p("7. Remote access", "H1Red"),
    p("The default local address is http://127.0.0.1:5000. For Internet access, forward the application through a reverse proxy such as Caddy and set Public URL in the Control Panel."),
    p("Example Caddy configuration", "H2Dark"), p("yourdomain.example {<br/>    reverse_proxy localhost:5000<br/>}", "Note"),
    p("Protect the web interface with a strong password. Do not expose the management interface without authentication.", "Note"),
    p("8. Troubleshooting", "H1Red"),
    *bullets([
        "Web page unavailable: confirm Engine status and verify that the configured port is free.",
        "Service does not start: keep the application in its original folder and accept the administrator prompt.",
        "Server immediately crashes: inspect its dedicated log file and verify ports, race rules and extra arguments.",
        "Tracker misses data: verify that it reads the same Dedicated log file path configured for that server.",
        "Update reports a file in use: close the old application and Control Panel, then run the installer again.",
    ]),
    p("9. Removing service mode safely", "H1Red"),
    p("Open the Control Panel, clear Run Engine as a Windows service, and press Save Settings. Approve the administrator request. Do this before moving or deleting the application folder."),
    p("Support", "H1Red"),
    p("GitHub: github.com/mostrotarlo/Assetto-Corsa-EVO-Server-Manager-Remote-Management-Web-Interface-<br/>Discord: mostrotarlo"),
])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
                        topMargin=18 * mm, bottomMargin=20 * mm,
                        title="EVO Web Server Manager v1.5.0 User Manual", author="Fabio Lombardi")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
