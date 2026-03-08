#!/bin/bash
# =============================================================
# USB Flasher v2 - Setup Script
# Ausfuehren mit: sudo bash setup.sh
# =============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "================================================="
echo "   USB Flasher v2 - Setup Script"
echo "================================================="
echo ""

# Root-Check
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Fehler: Bitte als root ausfuehren: sudo bash setup.sh${NC}"
    exit 1
fi

# =============================================================
# ORDNER ERSTELLEN
# =============================================================
echo -e "${YELLOW}[1/6] Erstelle Verzeichnisstruktur...${NC}"

mkdir -p /home/pi/isos
mkdir -p /home/pi/logs
chown -R root:root /home/pi/isos /home/pi/logs
chmod 755 /home/pi/isos /home/pi/logs

echo -e "${GREEN}  OK: /home/pi/isos und /home/pi/logs${NC}"

# =============================================================
# ABHAENGIGKEITEN
# =============================================================
echo -e "${YELLOW}[2/6] Installiere System-Abhaengigkeiten...${NC}"

apt-get update -qq

# Python Grundlagen
apt-get install -y python3-pip python3-smbus i2c-tools -qq
echo -e "${GREEN}  OK: python3-pip, python3-smbus, i2c-tools${NC}"

# Python GPIO
apt-get install -y python3-rpi.gpio -qq
echo -e "${GREEN}  OK: python3-rpi.gpio${NC}"

# evdev fuer USB-Numpad
apt-get install -y python3-evdev -qq
echo -e "${GREEN}  OK: python3-evdev${NC}"

# RPLCD fuer LCD-Display
pip3 install RPLCD --break-system-packages -q
echo -e "${GREEN}  OK: RPLCD${NC}"

# woeusb fuer Windows-ISOs
if apt-get install -y woeusb -qq 2>/dev/null; then
    echo -e "${GREEN}  OK: woeusb${NC}"
elif apt-get install -y woeusb-ng -qq 2>/dev/null; then
    echo -e "${GREEN}  OK: woeusb-ng${NC}"
else
    echo -e "${YELLOW}  HINWEIS: woeusb nicht verfuegbar - Windows-ISOs nicht flashbar${NC}"
    echo -e "${YELLOW}  Manuell: sudo apt install woeusb${NC}"
fi

# =============================================================
# I2C AKTIVIEREN
# =============================================================
echo -e "${YELLOW}[3/6] Aktiviere I2C fuer LCD...${NC}"

# I2C via raspi-config aktivieren (noninteraktiv)
raspi-config nonint do_i2c 0

# Sicherstellen dass i2c-dev beim Boot geladen wird
if ! grep -q "^i2c-dev" /etc/modules; then
    echo "i2c-dev" >> /etc/modules
fi

echo -e "${GREEN}  OK: I2C aktiviert${NC}"
echo -e "${YELLOW}  Tipp: LCD-Adresse pruefen mit: i2cdetect -y 1${NC}"
echo -e "${YELLOW}  Standard: 0x27, alternativ: 0x3F${NC}"
echo -e "${YELLOW}  Falls Adresse abweicht: LCD_I2C_ADRESSE in flasher.py anpassen${NC}"

# =============================================================
# FLASHER DATEIEN KOPIEREN
# =============================================================
echo -e "${YELLOW}[4/6] Kopiere Skripte...${NC}"

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

if [ -f "$SCRIPT_DIR/flasher.py" ]; then
    cp "$SCRIPT_DIR/flasher.py" /home/pi/flasher.py
    chmod +x /home/pi/flasher.py
    chown root:root /home/pi/flasher.py
    echo -e "${GREEN}  OK: flasher.py${NC}"
else
    echo -e "${YELLOW}  HINWEIS: flasher.py nicht gefunden - manuell uebertragen:${NC}"
    echo "  scp flasher.py pi@flasher.local:/home/pi/"
fi

if [ -f "$SCRIPT_DIR/get_isos.sh" ]; then
    cp "$SCRIPT_DIR/get_isos.sh" /home/pi/get_isos.sh
    chmod +x /home/pi/get_isos.sh
    chown root:root /home/pi/get_isos.sh
    echo -e "${GREEN}  OK: get_isos.sh${NC}"
else
    echo -e "${YELLOW}  HINWEIS: get_isos.sh nicht gefunden${NC}"
fi

# =============================================================
# SCHUTZFUNKTION
# =============================================================
echo -e "${YELLOW}[5/6] Lege Schutzfunktion an (ensurance.MD)...${NC}"

touch /ensurance.MD
echo -e "${GREEN}  OK: /ensurance.MD angelegt${NC}"
echo -e "${YELLOW}  Diese Datei schuetzt die SD-Karte vor versehentlichem Ueberschreiben.${NC}"

# =============================================================
# SYSTEMD SERVICE
# =============================================================
echo -e "${YELLOW}[6/6] Richte systemd Service ein...${NC}"

cat > /etc/systemd/system/flasher.service << 'SERVICE'
[Unit]
Description=USB Flasher v2
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/flasher.py
Restart=on-failure
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable flasher.service

echo -e "${GREEN}  OK: flasher.service aktiviert${NC}"

# =============================================================
# ABSCHLUSS
# =============================================================
echo ""
echo "================================================="
echo -e "${GREEN}Setup abgeschlossen!${NC}"
echo "================================================="
echo ""
echo "Naechste Schritte:"
echo "  1. LCD-Adresse pruefen: i2cdetect -y 1"
echo "     Falls nicht 0x27: LCD_I2C_ADRESSE in flasher.py anpassen"
echo "  2. Button-Pins pruefen (Datenblatt JOY-IT RB-LCD20X4)"
echo "     Falls noetig: BTN_HOCH/RUNTER/OK/ZURUECK in flasher.py anpassen"
echo "  3. ISOs in /home/pi/isos/ ablegen:"
echo "     Entweder per get_isos.sh oder manuell per SCP"
echo "  4. Pi neu starten: sudo reboot"
echo ""
echo "Dateistruktur:"
echo "  /home/pi/"
echo "  ├── flasher.py"
echo "  ├── get_isos.sh"
echo "  ├── isos/"
echo "  │   ├── w10.iso, w11.iso"
echo "  │   ├── u24.iso, mint.iso, debian.iso"
echo "  │   ├── fedora.iso, arch.iso"
echo "  │   ├── z18.iso, bazzite.iso"
echo "  └── logs/"
echo ""
echo "  /ensurance.MD  <- nicht loeschen!"
echo ""
echo "Bedienung:"
echo "  LCD-Buttons: Hoch/Runter/OK/Zurueck"
echo "  Numpad 1-9:  Direktauswahl OS"
echo "  Numpad 0:    Herunterfahren"
echo "  Numpad Enter: Bestaetigen"
echo ""
