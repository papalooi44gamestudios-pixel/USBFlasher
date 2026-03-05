from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

doc = SimpleDocTemplate("/mnt/user-data/outputs/USB_Flasher_Anleitung.pdf", pagesize=A4,
                        leftMargin=20*mm, rightMargin=20*mm,
                        topMargin=20*mm, bottomMargin=20*mm)

title_style  = ParagraphStyle('title', fontSize=22, fontName='Helvetica-Bold', spaceAfter=6, textColor=colors.HexColor('#1a1a2e'))
h1_style     = ParagraphStyle('h1', fontSize=14, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=4, textColor=colors.HexColor('#16213e'))
h2_style     = ParagraphStyle('h2', fontSize=11, fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=3, textColor=colors.HexColor('#0f3460'))
body_style   = ParagraphStyle('body', fontSize=9, fontName='Helvetica', spaceAfter=4, leading=13)
code_style   = ParagraphStyle('code', fontSize=7.5, fontName='Courier', spaceAfter=3,
                               backColor=colors.HexColor('#f0f0f0'), leftIndent=8,
                               rightIndent=8, leading=11, spaceBefore=2)

def tbl_style(header_color='#1a1a2e'):
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(header_color)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ])

def code_block(text):
    return Paragraph(text.replace('\n','<br/>').replace(' ','&nbsp;'), code_style)

class Checkbox(Flowable):
    def __init__(self, size=8):
        Flowable.__init__(self)
        self.size = size
        self.width = size
        self.height = size
    def draw(self):
        self.canv.setStrokeColor(colors.HexColor('#333333'))
        self.canv.setLineWidth(0.8)
        self.canv.rect(0, 0, self.size, self.size, fill=0)

def cb(): return Checkbox(8)

story = []

# TITEL
story.append(Paragraph("USB Flasher – Projektdokumentation", title_style))
story.append(Paragraph("Raspberry Pi Zero 2W | Multi-OS Flash-Geraet", ParagraphStyle('sub', fontSize=11, fontName='Helvetica', textColor=colors.grey, spaceAfter=4)))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
story.append(Spacer(1, 6))
story.append(Paragraph("Projektbeschreibung", h1_style))
story.append(Paragraph(
    "Ein kompaktes Geraet mit 9 Knoepfen, das per Knopfdruck einen angeschlossenen USB-Stick "
    "mit einem vordefinierten Betriebssystem-Image flasht. Drei zentrale LEDs (Gruen/Gelb/Rot) "
    "zeigen den Status an. Das Gehaeuse wird selbst 3D-gedruckt.",
    body_style))

# MATERIALLISTE
story.append(Paragraph("Materialliste", h1_style))
mat_data = [
    ['Teil', 'Menge', 'Preis (ca.)', 'Hinweis', 'OK'],
    ['Raspberry Pi Zero 2W', '1x', '18-22 EUR', 'Kompakter als 3A+', cb()],
    ['Micro-USB OTG Adapter', '1x', '~2-3 EUR', 'Fuer USB-A Stick am OTG-Port', cb()],
    ['Panel-Mount Drucktaster', '10x', '~5 EUR', 'Mit Loetanschluss, direkt ins Gehaeuse schraubbar (z.B. Reichelt T250A)', cb()],
    ['Power Button (beleuchtet)', '1x', '~1-2 EUR', 'Fuer sauberen Shutdown, oben', cb()],
    ['LED Gruen 5mm', '1x', '~0,10 EUR', 'Zentrale Status-LED', cb()],
    ['LED Gelb 5mm', '1x', '~0,10 EUR', 'Zentrale Status-LED', cb()],
    ['LED Rot 5mm', '1x', '~0,10 EUR', 'Zentrale Status-LED', cb()],
    ['Widerstand 330 Ohm', '3x', '~0,15 EUR', 'Je eine pro LED', cb()],
    ['Jumperkabel female-female', '30x', '~3 EUR', 'Fuer GPIO-Verbindungen', cb()],
    ['Schrumpfschlauch Sortiment', '1x', '~3 EUR', 'Zum Isolieren aller Loetstellen', cb()],
    ['Kabelverbinder/Luesterklemmen', '1x', '~2 EUR', 'Optional: fuer GND-Sammelleitung', cb()],
    ['SD-Karte 128 GB', '1x', '~10-15 EUR', 'Fuer OS + ISOs', cb()],
    ['Micro-USB Netzteil 5V/2,5A', '1x', '~8-12 EUR', 'Pi-Netzteil empfohlen', cb()],
    ['Gehaeuse', '1x', '-', 'Wird selbst 3D-gedruckt', cb()],
]
mat_t = Table(mat_data, colWidths=[45*mm, 16*mm, 24*mm, 56*mm, 20*mm])
mat_t.setStyle(TableStyle([
    *tbl_style().getCommands(),
    ('ALIGN', (4,0), (4,-1), 'CENTER'),
    ('VALIGN', (4,1), (4,-1), 'MIDDLE'),
]))
story.append(mat_t)
story.append(Spacer(1,4))
story.append(Paragraph("<b>Gesamtkosten (ca.): 42-58 EUR</b>", body_style))
story.append(Paragraph("Tipp: LEDs, Widerstaende und Taster als Sortiment-Set auf AliExpress bestellen.", body_style))
story.append(Paragraph(
    "Wichtig: Ein hochwertiges Micro-USB Kabel verwenden! Billlige Kabel verursachen Spannungsabfaelle unter Last (Flash + USB-Stromaufnahme) und koennen zu Abstuerzen oder korrupten Images fuehren. Am besten das offizielle Raspberry Pi Netzteil mit original Kabel nutzen.",
    body_style))
story.append(Paragraph(
    "Hinweis zum OTG-Port: Der Pi Zero 2W hat zwei Micro-USB Ports. "
    "Der linke (PWR) ist nur fuer Strom, der rechte (USB) ist der OTG-Port fuer den Stick. "
    "Mit dem OTG-Adapter kann ein normaler USB-A Stick angeschlossen werden. "
    "Verkabelung: Alle Taster und LEDs werden direkt per Jumperkabel und Loetstellen mit den GPIO-Pins verbunden - "
    "keine Lochrasterplatine noetig. GND-Pins koennen ueber eine gemeinsame Ader zusammengefuehrt werden.",
    body_style))

# GPIO PINBELEGUNG
story.append(Paragraph("GPIO-Pinbelegung", h1_style))
story.append(Paragraph("Status-LEDs (zentral fuer das gesamte Geraet):", h2_style))
led_data = [
    ['Funktion', 'GPIO Pin', 'Physischer Pin'],
    ['LED Gruen (Fertig/Bereit)', 'GPIO 18', 'Pin 12'],
    ['LED Gelb (Flashvorgang laeuft)', 'GPIO 23', 'Pin 16'],
    ['LED Rot (Fehler)', 'GPIO 24', 'Pin 18'],
]
story.append(Table(led_data, colWidths=[70*mm, 40*mm, 50*mm], style=tbl_style('#16213e')))
story.append(Spacer(1,6))
story.append(Paragraph("Knoepfe (9 Systeme):", h2_style))
btn_data = [
    ['System', 'GPIO Pin', 'Physischer Pin'],
    ['Windows 10', 'GPIO 2',  'Pin 3'],
    ['Windows 11', 'GPIO 3',  'Pin 5'],
    ['Ubuntu',     'GPIO 4',  'Pin 7'],
    ['Linux Mint', 'GPIO 17', 'Pin 11'],
    ['Debian',     'GPIO 27', 'Pin 13'],
    ['Fedora',     'GPIO 22', 'Pin 15'],
    ['Arch Linux', 'GPIO 10', 'Pin 19'],
    ['Zorin OS',   'GPIO 9',  'Pin 21'],
    ['Bazzite',    'GPIO 11', 'Pin 23'],
]
story.append(Table(btn_data, colWidths=[70*mm, 40*mm, 50*mm], style=tbl_style('#16213e')))
story.append(Spacer(1,4))
story.append(Paragraph("Alle Knoepfe: ein Bein an GPIO-Pin, anderes an GND. Pull-up wird per Software gesetzt.", body_style))
story.append(Paragraph("Alle LEDs: Anode (+) ueber 330-Ohm-Widerstand an GPIO, Kathode (-) an GND.", body_style))
story.append(Spacer(1,6))
story.append(Paragraph("Power Button:", h2_style))
power_data = [
    ['Funktion', 'GPIO Pin', 'Physischer Pin'],
    ['Power Button (Shutdown)', 'GPIO 26', 'Pin 37'],
]
story.append(Table(power_data, colWidths=[70*mm, 40*mm, 50*mm], style=tbl_style('#0f3460')))
story.append(Spacer(1,4))
story.append(Paragraph("Power Button 3 Sekunden gedruckt halten fuer sauberen Shutdown. Kurzes Druecken wird ignoriert um versehentliches Ausschalten zu verhindern.", body_style))

# GIT INSTALLATION
story.append(Paragraph("Installation via Git (empfohlen)", h1_style))
story.append(Paragraph(
    "Die einfachste Methode alle Projektdateien auf den Pi zu bringen ist Git. "
    "Alle Dateien kommen auf einmal und spaetere Updates sind mit einem einzigen Befehl moeglich.",
    body_style))

story.append(Paragraph("Auf dem Pi (per SSH) ausfuehren:", h2_style))
story.append(code_block(
    "# Git installieren:\n"
    "sudo apt install git -y\n\n"
    "# Repository klonen:\n"
    "git clone https://github.com/DEIN-PROFIL/usb-flasher.git /home/pi/usb-flasher\n\n"
    "# Setup ausfuehren:\n"
    "cd /home/pi/usb-flasher\n"
    "sudo bash setup.sh"
))

story.append(Paragraph("Spaetere Updates:", h2_style))
story.append(code_block(
    "# Neueste Version laden und Setup erneut ausfuehren:\n"
    "cd /home/pi/usb-flasher\n"
    "git pull\n"
    "sudo bash setup.sh"
))

story.append(Paragraph(
    "Alternative ohne Git: Dateien einzeln per SCP uebertragen (siehe naechste Abschnitte). "
    "Bei Git-Nutzung koennen die manuellen SCP-Schritte uebersprungen werden.",
    body_style))

# SD-KARTE VORBEREITEN
story.append(Paragraph("SD-Karte vorbereiten (auf dem Haupt-PC)", h1_style))
story.append(Paragraph("Die gesamte Einrichtung erfolgt am Haupt-PC. Der Pi braucht weder Tastatur noch Bildschirm.", body_style))

story.append(Paragraph("Schritt 1: Raspberry Pi OS Lite flashen", h2_style))
story.append(Paragraph(
    "Raspberry Pi Imager herunterladen von https://www.raspberrypi.com/software/ und installieren. "
    "SD-Karte einlegen, im Imager auswaehlen: Geraet = Raspberry Pi Zero 2, "
    "OS = Raspberry Pi OS Lite (64-bit), Speicher = SD-Karte. "
    "Vor dem Flashen das Zahnrad-Icon oeffnen fuer erweiterte Einstellungen.", body_style))

story.append(Paragraph("Schritt 2: SSH und WLAN im Imager konfigurieren", h2_style))
story.append(Paragraph(
    "In den erweiterten Einstellungen: Hostname z.B. 'flasher', SSH aktivieren "
    "(Passwort-Authentifizierung), Benutzername 'pi' mit eigenem Passwort, "
    "WLAN-SSID und Passwort eintragen, Zeitzone Europe/Berlin setzen. Dann flashen.", body_style))

story.append(Paragraph("Schritt 3: Pi starten und IP herausfinden", h2_style))
story.append(code_block(
    "# Am Router (z.B. Fritzbox) unter angeschlossene Geraete nachschauen\n"
    "# Oder im Terminal des Haupt-PCs:\n"
    "ping flasher.local\n\n"
    "# Alternativ mit nmap:\n"
    "nmap -sn 192.168.1.0/24"
))

story.append(Paragraph("Schritt 4: Per SSH verbinden", h2_style))
story.append(code_block(
    "# Im Terminal des Haupt-PCs:\n"
    "ssh pi@flasher.local\n"
    "# oder mit IP:\n"
    "ssh pi@192.168.1.XXX\n\n"
    "# Beim ersten Verbinden Fingerprint mit 'yes' bestaetigen\n"
    "# Dann das im Imager gesetzte Passwort eingeben"
))

story.append(Paragraph("Schritt 5: Pi aktualisieren und Pakete installieren", h2_style))
story.append(code_block(
    "# System aktualisieren:\n"
    "sudo apt update && sudo apt upgrade -y\n\n"
    "# Benoetigt fuer Windows-ISOs:\n"
    "sudo apt install woeusb -y\n\n"
    "# Falls woeusb nicht gefunden wird (neuere Systeme):\n"
    "sudo apt install woeusb-ng -y\n"
    "# flasher.py erkennt automatisch ob woeusb oder woeusb-ng vorhanden ist\n\n"
    "# Python GPIO Bibliothek:\n"
    "sudo apt install python3-rpi.gpio -y"
))

story.append(Paragraph("Schritt 6: Ordner anlegen und Skript uebertragen", h2_style))
story.append(code_block(
    "# Auf dem Pi (per SSH):\n"
    "mkdir -p /home/pi/isos\n"
    "mkdir -p /home/pi/logs\n\n"
    "# flasher.py vom Haupt-PC zum Pi uebertragen (am Haupt-PC ausfuehren):\n"
    "scp /pfad/zu/flasher.py pi@flasher.local:/home/pi/flasher.py\n\n"
    "# Skript ausfuehrbar machen (auf dem Pi):\n"
    "chmod +x /home/pi/flasher.py"
))

# ISOs VORBEREITEN
story.append(Paragraph("ISOs vorbereiten und uebertragen", h1_style))
story.append(Paragraph(
    "ISOs werden am Haupt-PC heruntergeladen und per SCP auf den Pi uebertragen. "
    "Alle ISO-Dateien muessen exakt so heissen wie im Skript unter SYSTEMS definiert.", body_style))

story.append(Paragraph("ISO-Dateinamen (muessen exakt stimmen):", h2_style))
iso_namen = [
    ['System', 'Dateiname', 'Download'],
    ['Windows 10', 'w10.iso',      'microsoft.com/de-de/software-download/windows10'],
    ['Windows 11', 'w11.iso',      'microsoft.com/de-de/software-download/windows11'],
    ['Ubuntu',     'u24.iso',      'ubuntu.com/download/desktop'],
    ['Linux Mint', 'mint.iso',     'linuxmint.com/download.php'],
    ['Debian',     'debian.iso',   'debian.org/distrib/'],
    ['Fedora',     'fedora.iso',   'fedoraproject.org/workstation/download'],
    ['Arch Linux', 'arch.iso',     'archlinux.org/download/'],
    ['Zorin OS',   'z18.iso',      'zorin.com/os/download/'],
    ['Bazzite',    'bazzite.iso',  'bazzite.gg'],
]
t = Table(iso_namen, colWidths=[28*mm, 30*mm, 100*mm])
t.setStyle(tbl_style('#16213e'))
story.append(t)
story.append(Spacer(1,4))

story.append(Paragraph("ISOs uebertragen (am Haupt-PC ausfuehren):", h2_style))
story.append(code_block(
    "# Einzelne ISO uebertragen (Zieldateiname muss stimmen!):\n"
    "scp /home/user/Downloads/ubuntu-24.04.iso pi@flasher.local:/home/pi/isos/u24.iso\n\n"
    "# Auf dem Pi pruefen ob alle angekommen sind:\n"
    "ls -lh /home/pi/isos/"
))

story.append(Paragraph("WICHTIG: TARGET (USB-Stick Pfad) richtig setzen", h2_style))
story.append(Paragraph(
    "Bevor der Flasher das erste Mal genutzt wird, muss der korrekte Pfad des USB-Sticks "
    "im Skript eingetragen sein. Ein falscher Pfad kann andere Laufwerke zerstoeren!", body_style))
story.append(code_block(
    "# USB-Stick (via OTG-Adapter) an den Pi anschliessen, dann per SSH:\n"
    "lsblk\n\n"
    "# Beispielausgabe:\n"
    "# NAME      MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT\n"
    "# sda         8:0    1  32G  0  disk            <-- USB-Stick (via OTG)\n"
    "# mmcblk0   179:0    0 128G  0  disk            <-- SD-Karte (NIEMALS als TARGET!)\n\n"
    "# In flasher.py anpassen:\n"
    "# TARGET = \"/dev/sda\"    (richtig - USB-Stick)\n"
    "# NIEMALS: TARGET = \"/dev/mmcblk0\"  (das waere die SD-Karte!)"
))

# BAUANLEITUNG
story.append(Paragraph("Bauanleitung – Schritt fuer Schritt", h1_style))
story.append(Paragraph(
    "Die Schritte 5-9 koennen alternativ automatisch mit dem mitgelieferten setup.sh Script erledigt werden "
    "(siehe Abschnitt 'Setup Script'). Empfohlen fuer einfache Einrichtung.",
    body_style))
story.append(Spacer(1,4))
schritte = [
    ("1. Vorbereitung", "Raspberry Pi OS Lite auf SD-Karte flashen wie oben beschrieben. SSH und WLAN im Imager konfigurieren."),
    ("2. LEDs anschliessen", "Jumperkabel direkt an LED-Beinchen loeten: Anode (+, laengeres Bein) -> Draht -> 330-Ohm-Widerstand -> Draht -> GPIO-Pin. Kathode (-, kuerzeres Bein) -> Draht -> GND. Alle GND-Kabel koennen zusammen an einen gemeinsamen GND-Pin des Pi gefuehrt werden. Jede Loetstelle mit Schrumpfschlauch isolieren."),
    ("3. Knoepfe anschliessen", "Panel-Mount Taster von innen durch die Gehaeusebohrung stecken, Mutter von aussen festziehen. Direkt an die beiden Loetanschluesse des Tasters loeten: ein Kabel an GPIO-Pin, eines an GND. Alle GND-Kabel aller Taster koennen auf einer gemeinsamen Ader zusammengefuehrt und dann mit einem einzigen Kabel an einen GND-Pin des Pi angeschlossen werden. Schrumpfschlauch ueber alle Loetstellen. Kein externer Widerstand noetig - Pull-up wird per Software gesetzt."),
    ("4. Verbindung testen", "Pi starten, per SSH verbinden, GPIO testen mit: python3 -c \"import RPi.GPIO as GPIO; print('GPIO OK')\" - gibt GPIO OK aus wenn erfolgreich."),
    ("5. TARGET pruefen", "USB-Stick via OTG-Adapter anschliessen und mit lsblk pruefen. flasher.py ermittelt das Zielgeraet automatisch via lsblk beim Flash-Vorgang."),
    ("6. Dateien uebertragen", "flasher.py und setup.sh per SCP auf den Pi uebertragen (siehe unten)."),
    ("7. Setup Script ausfuehren", "sudo bash setup.sh - erstellt Ordner, kopiert flasher.py, legt ensurance.MD an, richtet systemd ein."),
    ("8. ISOs uebertragen", "ISOs mit den korrekten Dateinamen nach /home/pi/isos/ kopieren (siehe ISO-Tabelle)."),
    ("9. Testen", "Skript manuell starten: sudo python3 /home/pi/flasher.py - Gruene LED blinkt 3x wenn bereit."),
    ("10. Neu starten", "sudo reboot - Ab jetzt startet der Flasher automatisch beim Booten."),
]
for titel, text in schritte:
    story.append(Paragraph(f"<b>{titel}</b>", body_style))
    story.append(Paragraph(text, ParagraphStyle('ind', fontSize=9, fontName='Helvetica', leftIndent=10, spaceAfter=5, leading=13)))

# SETUP SCRIPT
story.append(Paragraph("Setup Script (setup.sh)", h1_style))
story.append(Paragraph(
    "Das mitgelieferte setup.sh Script automatisiert die gesamte Einrichtung auf dem Pi. "
    "Es erstellt alle benoetigten Ordner, kopiert flasher.py, legt die Schutzfunktion an "
    "und richtet den systemd-Service ein - alles in einem Schritt.",
    body_style))

story.append(Paragraph("Dateien per SCP auf den Pi uebertragen:", h2_style))
story.append(code_block(
    "# Am Haupt-PC ausfuehren:\n"
    "scp flasher.py setup.sh pi@flasher.local:/home/pi/\n\n"
    "# Auf dem Pi ausfuehren:\n"
    "sudo bash /home/pi/setup.sh"
))

story.append(Paragraph("Was das Script erledigt:", h2_style))
setup_data = [
    ['Schritt', 'Aktion'],
    ['1', 'Prueft ob es als root laeuft'],
    ['2', 'Erstellt /home/pi/isos/ und /home/pi/logs/'],
    ['3', 'Setzt Berechtigungen fuer Ordner'],
    ['4', 'Kopiert flasher.py nach /home/pi/ falls im selben Ordner'],
    ['5', 'Legt /ensurance.MD Schutzfunktion an'],
    ['6', 'Erstellt und aktiviert systemd flasher.service'],
]
setup_t = Table(setup_data, colWidths=[15*mm, 145*mm])
setup_t.setStyle(tbl_style('#0f3460'))
story.append(setup_t)
story.append(Spacer(1,4))
story.append(Paragraph(
    "Nach dem Script muessen nur noch die ISOs in /home/pi/isos/ abgelegt "
    "und TARGET in flasher.py geprueft werden. Dann sudo reboot und das Geraet ist einsatzbereit.",
    body_style))
story.append(code_block(
    "# Erwartete Ausgabe nach erfolgreichem Setup:\n"
    "# [1/5] Erstelle Verzeichnisstruktur... OK\n"
    "# [2/5] Setze Berechtigungen (root)...  OK\n"
    "# [3/5] Suche flasher.py...             OK\n"
    "# [4/5] Lege Schutzfunktion an...       OK\n"
    "# [5/5] Richte systemd Service ein...   OK"
))

# AUTOSTART
story.append(Paragraph("Autostart beim Boot (systemd)", h1_style))
story.append(code_block(
    "# Datei anlegen:\n"
    "sudo nano /etc/systemd/system/flasher.service\n\n"
    "# Inhalt:\n"
    "[Unit]\n"
    "Description=USB Flasher\n"
    "After=multi-user.target\n\n"
    "[Service]\n"
    "ExecStart=/usr/bin/python3 /home/pi/flasher.py\n"
    "Restart=on-failure\n"
    "RestartSec=5\n"
    "User=root\n\n"
    "[Install]\n"
    "WantedBy=multi-user.target\n\n"
    "# Service aktivieren und starten:\n"
    "sudo systemctl enable flasher.service\n"
    "sudo systemctl start flasher.service\n\n"
    "# Status pruefen:\n"
    "sudo systemctl status flasher.service"
))
story.append(Paragraph(
    "Hinweis: Der Service laeuft als root - kein sudo noetig innerhalb des Skripts. "
    "Restart=on-failure statt Restart=always verhindert einen Restart-Loop bei kritischen Fehlern.",
    body_style))

# SCHUTZFUNKTION
story.append(Paragraph("Schutzfunktion: ensurance.MD", h1_style))
story.append(Paragraph(
    "Um zu verhindern dass der Pi versehentlich seine eigene SD-Karte ueberschreibt, "
    "wird vor jedem Flash-Vorgang geprueft ob die Datei ensurance.MD auf dem Zielgeraet vorhanden ist. "
    "Wird sie gefunden, wird der Flash sofort blockiert und die rote LED leuchtet.", body_style))
story.append(code_block(
    "# Schutzdatei einmalig auf der SD-Karte anlegen:\n"
    "sudo touch /ensurance.MD\n\n"
    "# Pruefen ob vorhanden:\n"
    "ls -la /ensurance.MD"
))
story.append(Paragraph(
    "Die Datei liegt im Wurzelverzeichnis (/) der SD-Karte. Andere USB-Sticks ohne "
    "diese Datei koennen weiterhin normal geflasht werden. "
    "Hinweis: Dieser Mechanismus ist eine Sicherheitsnetz-Funktion, kein absoluter Schutz. "
    "Ein manuell falsch gesetztes TARGET kann den Schutz umgehen - "
    "daher TARGET immer sorgfaeltig mit lsblk pruefen.", body_style))

# LOGS
story.append(Paragraph("Logs lesen und auswerten", h1_style))
story.append(Paragraph(
    "Jede Session erstellt eine eigene Log-Datei in /home/pi/logs/ mit Datum und Uhrzeit "
    "im Dateinamen. Beim Start wird geprueft welche ISOs vorhanden sind, "
    "jeder Flash-Vorgang und jeder Fehler wird mit Zeitstempel eingetragen. "
    "Hinweis: Da der Service als root laeuft, gehoert der Ordner root. "
    "Zum Loeschen alter Logs sudo verwenden: sudo rm /home/pi/logs/*.txt", body_style))
story.append(code_block(
    "# Alle Log-Dateien anzeigen:\n"
    "ls -lh /home/pi/logs/\n\n"
    "# Neueste Log-Datei lesen:\n"
    "cat /home/pi/logs/$(ls -t /home/pi/logs/ | head -1)\n\n"
    "# Log live mitverfolgen waehrend der Flasher laeuft:\n"
    "tail -f /home/pi/logs/$(ls -t /home/pi/logs/ | head -1)\n\n"
    "# Alle Fehler aus allen Logs anzeigen:\n"
    "grep 'FEHLER' /home/pi/logs/*.txt\n\n"
    "# Logs auch ueber systemd Journal einsehbar:\n"
    "sudo journalctl -u flasher.service -f"
))

# ISO SPEICHERBEDARF
story.append(Paragraph("Speicherbedarf ISOs (Richtwerte)", h1_style))
iso_data = [
    ['Betriebssystem', 'ISO-Groesse (ca.)'],
    ['Windows 10',    '5,5 GB'],
    ['Windows 11',    '6,5 GB'],
    ['Ubuntu 24.04',  '5,0 GB'],
    ['Linux Mint 21', '2,5 GB'],
    ['Debian 12',     '1,0 GB'],
    ['Fedora 40',     '2,0 GB'],
    ['Arch Linux',    '0,9 GB'],
    ['Zorin OS 18',   '3,5 GB'],
    ['Bazzite',       '~4,0 GB'],
    ['Gesamt (9 Systeme)', '~ 31 GB'],
]
iso_t = Table(iso_data, colWidths=[80*mm, 80*mm])
s = tbl_style('#16213e')
s.add('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
s.add('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f4f8'))
iso_t.setStyle(s)
story.append(iso_t)
story.append(Spacer(1,4))
story.append(Paragraph("128-GB-SD-Karte reicht. 256 GB gibt Platz fuer weitere Systeme.", body_style))

# GET_ISOS
story.append(Paragraph("ISO Download Script (get_isos.sh)", h1_style))
story.append(Paragraph(
    "Das mitgelieferte get_isos.sh Script laedt alle Linux-ISOs direkt auf den Pi herunter. "
    "Windows-ISOs koennen wegen Microsofts tokenbasierter Download-Links nicht automatisiert werden "
    "und muessen manuell per SCP uebertragen werden.",
    body_style))

story.append(Paragraph("Ausfuehren:", h2_style))
story.append(code_block(
    "# Script uebertragen (am Haupt-PC):\n"
    "scp get_isos.sh pi@flasher.local:/home/pi/\n\n"
    "# Auf dem Pi ausfuehren:\n"
    "bash /home/pi/get_isos.sh"
))

story.append(Paragraph("Menue-Optionen:", h2_style))
menu_data = [
    ['Option', 'Funktion'],
    ['1', 'Alle fehlenden Linux-ISOs automatisch herunterladen'],
    ['2', 'Einzelne ISO auswaehlen und herunterladen'],
    ['3', 'Alle Linux-ISOs neu herunterladen (ueberschreiben)'],
    ['4', 'Nur Status der vorhandenen ISOs anzeigen'],
]
story.append(Table(menu_data, colWidths=[20*mm, 140*mm], style=tbl_style('#0f3460')))
story.append(Spacer(1,4))

story.append(Paragraph("Windows-ISOs manuell uebertragen:", h2_style))
story.append(code_block(
    "# Windows 10 ISO herunterladen:\n"
    "# https://www.microsoft.com/de-de/software-download/windows10\n\n"
    "# Windows 11 ISO herunterladen:\n"
    "# https://www.microsoft.com/de-de/software-download/windows11\n\n"
    "# Dann per SCP auf den Pi:\n"
    "scp windows10.iso pi@flasher.local:/home/pi/isos/w10.iso\n"
    "scp windows11.iso pi@flasher.local:/home/pi/isos/w11.iso"
))
story.append(Paragraph(
    "Das Script prueft vor jedem Download ob genuegend Speicherplatz vorhanden ist "
    "und ueberspringt bereits vorhandene ISOs automatisch.",
    body_style))

# GEHAEUSE
story.append(Paragraph("Gehaeuse-Design (Hinweise fuer 3D-Druck)", h1_style))
layout_data = [
    ['Position', 'Element'],
    ['Oben links',       '3x LEDs (Gruen, Gelb, Rot) nebeneinander'],
    ['Oben mitte',       '1x Power Button (Shutdown)'],
    ['Oben rechts',      '1x USB-A Port via OTG-Adapter (fuer den zu flashenden Stick)'],
    ['Mitte zentriert',  'Alle 9 Knoepfe in Raster-Anordnung'],
    ['Hinten',           '2x Micro-USB: links Strom, rechts OTG fuer Stick'],
]
story.append(Table(layout_data, colWidths=[50*mm, 110*mm], style=tbl_style('#16213e')))
story.append(Spacer(1,4))
story.append(Paragraph("Pi Zero 2W Abmessungen: 65 x 30 mm. Mindest-Innenraum: ca. 75 x 40 x 25 mm.", body_style))
story.append(Paragraph("LED-Bohrungen: 5 mm Durchmesser. Taster: je nach Modell 6-12 mm.", body_style))
story.append(Paragraph("Tipp: Der Zero 2W ist deutlich schmaler als der 3A+ - das Gehaeuse kann entsprechend kompakter gestaltet werden.", body_style))

doc.build(story)
print("PDF erstellt.")
