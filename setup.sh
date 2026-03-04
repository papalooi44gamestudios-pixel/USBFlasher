#!/bin/bash
# =============================================================
# USB Flasher - Setup Script
# Ausfuehren mit: sudo bash setup.sh
# =============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "================================================="
echo "   USB Flasher - Setup Script"
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
echo -e "${YELLOW}[1/5] Erstelle Verzeichnisstruktur...${NC}"

mkdir -p /home/pi/isos
mkdir -p /home/pi/logs

echo -e "${GREEN}  OK: /home/pi/isos${NC}"
echo -e "${GREEN}  OK: /home/pi/logs${NC}"

# =============================================================
# BERECHTIGUNGEN SETZEN
# =============================================================
echo -e "${YELLOW}[2/5] Setze Berechtigungen...${NC}"

# Ordner gehoeren root da der Service als root laeuft
chown -R root:root /home/pi/isos
chown -R root:root /home/pi/logs
chmod 755 /home/pi/isos
chmod 755 /home/pi/logs

echo -e "${GREEN}  OK: Berechtigungen gesetzt (root, da Service als root laeuft)${NC}"

# =============================================================
# ABHAENGIGKEITEN INSTALLIEREN
# =============================================================
echo -e "${YELLOW}[2b/5] Installiere Abhaengigkeiten...${NC}"

apt-get update -qq

# Python GPIO
apt-get install -y python3-rpi.gpio -qq
echo -e "${GREEN}  OK: python3-rpi.gpio${NC}"

# woeusb fuer Windows-ISOs - versucht zuerst woeusb dann woeusb-ng
if apt-get install -y woeusb -qq 2>/dev/null; then
    echo -e "${GREEN}  OK: woeusb installiert${NC}"
elif apt-get install -y woeusb-ng -qq 2>/dev/null; then
    echo -e "${GREEN}  OK: woeusb-ng installiert${NC}"
else
    echo -e "${YELLOW}  HINWEIS: woeusb/woeusb-ng konnte nicht installiert werden.${NC}"
    echo -e "${YELLOW}  Windows-ISOs koennen nicht geflasht werden bis es installiert ist.${NC}"
    echo -e "${YELLOW}  Manuell versuchen: sudo apt install woeusb${NC}"
fi

# =============================================================
# FLASHER.PY KOPIEREN
# =============================================================
echo -e "${YELLOW}[3/5] Suche flasher.py...${NC}"

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

if [ -f "$SCRIPT_DIR/flasher.py" ]; then
    cp "$SCRIPT_DIR/flasher.py" /home/pi/flasher.py
    chmod +x /home/pi/flasher.py
    chown root:root /home/pi/flasher.py
    echo -e "${GREEN}  OK: flasher.py nach /home/pi/ kopiert${NC}"

if [ -f "$SCRIPT_DIR/get_isos.sh" ]; then
    cp "$SCRIPT_DIR/get_isos.sh" /home/pi/get_isos.sh
    chmod +x /home/pi/get_isos.sh
    chown root:root /home/pi/get_isos.sh
    echo -e "${GREEN}  OK: get_isos.sh nach /home/pi/ kopiert${NC}"
else
    echo -e "${YELLOW}  HINWEIS: get_isos.sh nicht gefunden - bitte manuell uebertragen${NC}"
fi
else
    echo -e "${YELLOW}  HINWEIS: flasher.py nicht gefunden - bitte manuell uebertragen:${NC}"
    echo "  scp flasher.py pi@flasher.local:/home/pi/flasher.py"
fi

# =============================================================
# SCHUTZFUNKTION: ensurance.MD ANLEGEN
# =============================================================
echo -e "${YELLOW}[4/5] Lege Schutzfunktion an (ensurance.MD)...${NC}"

touch /ensurance.MD
echo -e "${GREEN}  OK: /ensurance.MD angelegt${NC}"
echo -e "${YELLOW}  HINWEIS: Diese Datei schuetzt die SD-Karte vor versehentlichem Ueberschreiben.${NC}"
echo -e "${YELLOW}  Nicht loeschen!${NC}"

# =============================================================
# SYSTEMD SERVICE EINRICHTEN
# =============================================================
echo -e "${YELLOW}[5/5] Richte systemd Service ein...${NC}"

cat > /etc/systemd/system/flasher.service << 'SERVICE'
[Unit]
Description=USB Flasher
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

echo -e "${GREEN}  OK: flasher.service angelegt und aktiviert${NC}"
echo -e "${GREEN}  (Restart=on-failure mit 5s Verzoegerung - kein Restart-Loop bei kritischen Fehlern)${NC}"

# =============================================================
# ABSCHLUSS
# =============================================================
echo ""
echo "================================================="
echo -e "${GREEN}Setup abgeschlossen!${NC}"
echo "================================================="
echo ""
echo "Naechste Schritte:"
echo "  1. TARGET pruefen: USB-Stick anschliessen, dann: lsblk"
echo "  2. ISOs in /home/pi/isos/ ablegen (Dateinamen beachten!)"
echo "  3. Pi neu starten: sudo reboot"
echo ""
echo "Dateistruktur:"
echo "  /home/pi/"
echo "  ├── flasher.py       <- Hauptskript"
echo "  ├── isos/            <- ISOs hier ablegen"
echo "  │   ├── w10.iso"
echo "  │   ├── w11.iso"
echo "  │   ├── u24.iso"
echo "  │   ├── mint.iso"
echo "  │   ├── debian.iso"
echo "  │   ├── fedora.iso"
echo "  │   ├── arch.iso"
echo "  │   ├── z18.iso"
echo "  │   └── bazzite.iso"
echo "  └── logs/            <- Logs werden hier gespeichert"
echo ""
echo "  /ensurance.MD        <- Schutzfunktion (nicht loeschen!)"
echo ""
