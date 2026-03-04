# 🚀 PiZero Multi-OS USB Flasher

Verwandle einen **Raspberry Pi Zero 2W** in eine autarke Flash-Station.  
Wähle per Knopfdruck aus bis zu 9 Betriebssystemen und flashe sie direkt auf einen USB-Stick – ohne PC, ohne Monitor, ohne Tastatur.

---

## ✨ Features

- **Stand-alone Betrieb** – 9 dedizierte Taster für verschiedene OS-Images + Power-Button
- **Smart-Download** – Mitgeliefertes Script lädt aktuelle Linux-ISOs direkt auf den Pi
- **Sicherheitsmechanismus** – `ensurance.MD` verhindert versehentliches Überschreiben der SD-Karte
- **Visuelles Feedback** – 3 LEDs zeigen Status: Bereit (Grün), Arbeitet/Blinkt (Gelb), Fehler (Rot)
- **Windows-Support** – Windows 10/11 via `woeusb` oder `woeusb-ng`
- **Automatische Geräteerkennung** – Ziel-USB-Stick wird automatisch via `lsblk` erkannt
- **Session-Logging** – Jeder Flash-Vorgang wird mit Zeitstempel protokolliert

---

## 🛠 Hardware

| Komponente | Details |
|---|---|
| Controller | Raspberry Pi Zero 2W |
| Adapter | Micro-USB auf USB-A (OTG) |
| Taster | 9x OS-Auswahl + 1x Power-Button (GPIO) |
| LEDs | 3x 5mm (Grün, Gelb, Rot) + je 1x 330Ω Widerstand |
| Speicher | SD-Karte 128 GB |
| Stromversorgung | Micro-USB Netzteil 5V/2,5A |

### GPIO-Belegung

| Funktion | GPIO | Pin |
|---|---|---|
| LED Grün | GPIO 18 | Pin 12 |
| LED Gelb | GPIO 23 | Pin 16 |
| LED Rot | GPIO 24 | Pin 18 |
| Power Button | GPIO 26 | Pin 37 |
| Windows 10 | GPIO 2 | Pin 3 |
| Windows 11 | GPIO 3 | Pin 5 |
| Ubuntu | GPIO 4 | Pin 7 |
| Linux Mint | GPIO 17 | Pin 11 |
| Debian | GPIO 27 | Pin 13 |
| Fedora | GPIO 22 | Pin 15 |
| Arch Linux | GPIO 10 | Pin 19 |
| Zorin OS 18 | GPIO 9 | Pin 21 |
| Bazzite | GPIO 11 | Pin 23 |

---

## 🚀 Schnellstart

### 1. Repository klonen und Setup ausführen

```bash
git clone https://github.com/DEIN-PROFIL/usb-flasher.git
cd usb-flasher
sudo bash setup.sh
```

Das Setup-Script erledigt automatisch:
- Ordnerstruktur anlegen (`/home/pi/isos/`, `/home/pi/logs/`)
- Abhängigkeiten installieren (`python3-rpi.gpio`, `woeusb`/`woeusb-ng`)
- Schutzfunktion aktivieren (`/ensurance.MD`)
- systemd-Service einrichten (Autostart beim Boot)

### 2. ISOs laden

Linux-ISOs automatisch herunterladen:

```bash
bash get_isos.sh
```

Windows-ISOs müssen manuell heruntergeladen und übertragen werden:

```bash
# Download unter: https://www.microsoft.com/de-de/software-download/windows10
scp windows10.iso pi@flasher.local:/home/pi/isos/w10.iso

# Download unter: https://www.microsoft.com/de-de/software-download/windows11
scp windows11.iso pi@flasher.local:/home/pi/isos/w11.iso
```

### 3. Betrieb

Nach dem Booten blinkt die grüne LED 3x → Gerät ist bereit.  
USB-Stick einstecken, gewünschten OS-Knopf drücken, gelbe LED blinkt während des Flash-Vorgangs.  
**Power-Button 3 Sekunden halten** für sauberen Shutdown.

---

## 📂 Projektstruktur

```
usb-flasher/
├── flasher.py            # Hauptskript – GPIO, LEDs, Flash-Logik
├── setup.sh              # Einrichtung: Ordner, Abhängigkeiten, systemd
├── get_isos.sh           # Menügeführtes ISO-Download-Tool
└── USB_Flasher_Anleitung.pdf  # Vollständige Bauanleitung
```

### ISO-Dateinamen (müssen exakt stimmen)

| System | Dateiname |
|---|---|
| Windows 10 | `w10.iso` |
| Windows 11 | `w11.iso` |
| Ubuntu 24.04 | `u24.iso` |
| Linux Mint | `mint.iso` |
| Debian | `debian.iso` |
| Fedora | `fedora.iso` |
| Arch Linux | `arch.iso` |
| Zorin OS 18 | `z18.iso` |
| Bazzite | `bazzite.iso` |

---

## 🔒 Sicherheitsmechanismus

Auf der SD-Karte des Pi liegt eine Datei `/ensurance.MD`.  
Vor jedem Flash-Vorgang prüft das Skript ob diese Datei auf dem **Zielgerät** vorhanden ist.  
Wird sie gefunden → Flash wird blockiert, rote LED leuchtet.  
So wird verhindert dass die SD-Karte des Pi versehentlich als Ziel verwendet wird.

> **Hinweis:** Zu flashende USB-Sticks dürfen diese Datei **nicht** enthalten.

---

## 🔧 Troubleshooting

| Problem | Ursache | Lösung |
|---|---|---|
| Grüne LED blinkt nicht beim Start | Service nicht gestartet | `sudo systemctl status flasher.service` |
| Rote LED nach Knopfdruck | ISO fehlt oder USB-Stick nicht erkannt | `cat $(ls -t /home/pi/logs/*.txt \| head -1)` |
| Windows-Flash schlägt fehl | woeusb nicht installiert | `sudo apt install woeusb` |
| USB-Stick wird nicht erkannt | Falscher Port (PWR statt OTG) | OTG-Port verwenden (rechter Micro-USB) |
| Pi startet nicht sauber | Schlechtes Netzteil/Kabel | Offizielles Pi-Netzteil + hochwertiges Kabel |
| Service startet in Loop | Kritischer Fehler im Skript | `sudo journalctl -u flasher.service -n 50` |

### Logs auswerten

```bash
# Neueste Log-Datei anzeigen
cat /home/pi/logs/$(ls -t /home/pi/logs/ | head -1)

# Live mitlesen
tail -f /home/pi/logs/$(ls -t /home/pi/logs/ | head -1)

# Alle Fehler suchen
grep "FEHLER" /home/pi/logs/*.txt
```

---

## 📄 Lizenz

MIT License – frei zum Nachbauen, Modifizieren und Teilen.
