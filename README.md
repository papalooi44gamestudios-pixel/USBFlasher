# USB Flasher v2

Raspberry Pi Zero 2W basierter USB-Flasher mit LCD-Menü und Numpad-Steuerung.
Unterstützt 9 Betriebssysteme (Linux + Windows), unbegrenzt erweiterbar.

---

## Hardware

| Komponente | Modell | Preis | Quelle |
|---|---|---|---|
| Raspberry Pi Zero 2WH | SC0510 | ~22 € | Berrybase – "WH" = mit vorgelötetem GPIO-Header (zwingend erforderlich!) |
| LCD 20x4 + 4 Buttons | JOY-IT RB-LCD20X4 | 4,50 € | Reichelt (RPI LCD20X4 4BYL) |
| USB Hub (powered) | beliebig | ~10 € | – |
| USB Numpad | beliebig | ~8 € | – |
| SD-Karte (min. 64 GB) | – | ~10 € | – |
| Netzteil 5V/2,5A Micro-USB | – | ~8 € | – |
| **Gesamt** | | **~63 €** | |

---

## Anschlüsse

```
Pi Zero 2W
├── GPIO-Header (40 Pin)  →  JOY-IT LCD direkt aufgesteckt
│   ├── Pin 2  (5V)       →  LCD VCC
│   ├── Pin 3  (SDA)      →  LCD I2C Daten
│   ├── Pin 5  (SCL)      →  LCD I2C Takt
│   └── Pin 6  (GND)      →  LCD GND
├── Micro-USB Power        →  5V Netzteil
└── Micro-USB OTG          →  Powered USB Hub
    ├── USB Numpad
    └── USB Stick (zu flashen)
```

---

## LCD-Buttons

| Button | Funktion |
|---|---|
| BTN1 (GPIO 21) | Menü hoch |
| BTN2 (GPIO 20) | Menü runter |
| BTN3 (GPIO 16) | Auswählen / OK |
| BTN4 (GPIO 12) | Zurück / Abbrechen |

> Pins laut Datenblatt prüfen. Falls nötig in `flasher.py` anpassen:
> `BTN_HOCH`, `BTN_RUNTER`, `BTN_OK`, `BTN_ZURUECK`

---

## Numpad-Belegung

| Taste | Funktion |
|---|---|
| 1–9 | Direktauswahl OS (1=Windows 10, 2=Windows 11, ...) |
| 0 | Herunterfahren |
| + | Menü hoch |
| - | Menü runter |
| Enter | Bestätigen |
| * | Zurück |

---

## ISO-Dateinamen

| Betriebssystem | Dateiname |
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

ISOs liegen in `/home/pi/isos/`

---

## Installation

```bash
# Repo klonen
git clone https://github.com/dein-user/usb-flasher.git
cd usb-flasher

# Setup ausführen (als root)
sudo bash setup.sh
```

Setup erledigt automatisch:
- I2C aktivieren
- Python-Abhängigkeiten installieren (RPLCD, evdev, RPi.GPIO)
- woeusb für Windows-ISOs installieren
- systemd Service einrichten (Autostart)
- ensurance.MD Schutzfunktion anlegen

---

## ISOs übertragen

```bash
# Mit get_isos.sh (Linux-ISOs automatisch)
sudo bash /home/pi/get_isos.sh

# Manuell per SCP
scp u24.iso pi@flasher.local:/home/pi/isos/u24.iso
```

Windows-ISOs müssen manuell von microsoft.com heruntergeladen werden:
- Windows 10: https://www.microsoft.com/de-de/software-download/windows10ISO
- Windows 11: https://www.microsoft.com/de-de/software-download/windows11

---

## LCD-Adresse prüfen

```bash
i2cdetect -y 1
```

Standard: `0x27`. Falls abweichend, in `flasher.py` anpassen:
```python
LCD_I2C_ADRESSE = 0x27  # oder 0x3F
```

---

## Sicherheitsmechanismus

`/ensurance.MD` liegt auf der SD-Karte des Pi. Vor jedem Flash prüft der Flasher ob diese Datei auf dem **Zielgerät** vorhanden ist. Falls ja → Flash blockiert. Verhindert versehentliches Überschreiben der SD-Karte des Pi.

---

## Troubleshooting

| Problem | Lösung |
|---|---|
| LCD zeigt nichts | I2C-Adresse prüfen: `i2cdetect -y 1`, ggf. Kontrast-Poti am LCD drehen |
| Buttons reagieren nicht | GPIO-Pins im Datenblatt prüfen, in `flasher.py` anpassen |
| Numpad wird nicht erkannt | `python3 -c "import evdev; print(evdev.list_devices())"` |
| Service startet nicht | `journalctl -u flasher.service -n 50` |
| Flash schlägt fehl | Log prüfen: `ls -t /home/pi/logs/ \| head -1` |
| woeusb fehlt | `sudo apt install woeusb` |

---

## Erweiterung

Neues OS hinzufügen – in `flasher.py` einfach in die Liste eintragen:

```python
SYSTEMS = [
    ...
    ("Pop!_OS", "popos.iso", False),  # einfach anfügen
]
```

Kein weiterer Umbau nötig. Das Menü scrollt automatisch.

---

## Legal

This software is provided for educational and personal use.

Regarding age-verification laws (Colorado SB 24-041, California AB 1043 and similar legislation): This project is a hobbyist open-source tool for flashing operating system installation media. It does not distribute operating systems or other digital products directly. Any compliance obligations regarding age-verification for digital products rest with the respective OS vendors (Microsoft, Canonical, etc.), not with this tool. Users are responsible for ensuring they obtain OS images through official, legal channels.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
