#!/bin/bash
# =============================================================
# USB Flasher - ISO Download Script
# Laedt ISOs direkt auf den Pi in /home/pi/isos/
# Ausfuehren mit: bash get_isos.sh
# =============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ISO_DIR="/home/pi/isos"
MIN_FREE_GB=7  # Mindest-Speicherplatz in GB vor jedem Download

# =============================================================
# DOWNLOAD-LINKS
# Windows: Keine direkten Links moeglich (Microsoft sperrt diese)
# Alle anderen: Offizielle Mirror/Release-Links
# =============================================================
declare -A ISO_URLS=(
    ["u24"]="https://releases.ubuntu.com/24.04/ubuntu-24.04.2-desktop-amd64.iso"
    ["mint"]="https://mirrors.kernel.org/linuxmint/stable/22.1/linuxmint-22.1-cinnamon-64bit.iso"
    ["debian"]="https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.10.0-amd64-netinst.iso"
    ["fedora"]="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-41-1.4.iso"
    ["arch"]="https://mirrors.kernel.org/archlinux/iso/latest/archlinux-x86_64.iso"
    ["z18"]="https://downloads.zorin.com/ZorinOS-18-Core-64-bit.iso"
    ["bazzite"]="https://dl.bazzite.gg/Bazzite-KDE-stable.iso"
)

declare -A ISO_NAMES=(
    ["u24"]="Ubuntu 24.04"
    ["mint"]="Linux Mint 22.1"
    ["debian"]="Debian 12 (Netinstall)"
    ["fedora"]="Fedora 41 Workstation"
    ["arch"]="Arch Linux"
    ["z18"]="Zorin OS 18"
    ["bazzite"]="Bazzite"
    ["w10"]="Windows 10"
    ["w11"]="Windows 11"
)

declare -A ISO_SIZES=(
    ["u24"]="5"
    ["mint"]="3"
    ["debian"]="1"
    ["fedora"]="2"
    ["arch"]="1"
    ["z18"]="4"
    ["bazzite"]="4"
    ["w10"]="6"
    ["w11"]="7"
)

# =============================================================
# HILFSFUNKTIONEN
# =============================================================

check_tool() {
    if command -v wget &> /dev/null; then
        echo "wget"
    elif command -v curl &> /dev/null; then
        echo "curl"
    else
        echo ""
    fi
}

freier_speicher_gb() {
    df -BG "$ISO_DIR" | awk 'NR==2 {gsub("G",""); print $4}'
}

iso_vorhanden() {
    local key=$1
    [ -f "$ISO_DIR/${key}.iso" ] && echo "true" || echo "false"
}

download_iso() {
    local key=$1
    local url=$2
    local ziel="$ISO_DIR/${key}.iso"
    local tool=$3

    echo ""
    echo -e "${CYAN}Starte Download: ${ISO_NAMES[$key]}${NC}"
    echo -e "Quelle: $url"
    echo -e "Ziel:   $ziel"
    echo ""

    if [ "$tool" = "wget" ]; then
        wget --progress=bar:force -O "$ziel" "$url"
    else
        curl -L --progress-bar -o "$ziel" "$url"
    fi

    if [ $? -eq 0 ]; then
        local size=$(du -sh "$ziel" | cut -f1)
        echo -e "${GREEN}  OK: ${ISO_NAMES[$key]} heruntergeladen ($size)${NC}"
        return 0
    else
        echo -e "${RED}  FEHLER: Download fehlgeschlagen - unvollstaendige Datei wird geloescht${NC}"
        rm -f "$ziel"
        return 1
    fi
}

zeige_status() {
    echo ""
    echo -e "${BOLD}Aktueller ISO-Status in $ISO_DIR:${NC}"
    echo "-------------------------------------------"
    for key in w10 w11 u24 mint debian fedora arch z18 bazzite; do
        if [ -f "$ISO_DIR/${key}.iso" ]; then
            local size=$(du -sh "$ISO_DIR/${key}.iso" | cut -f1)
            echo -e "  ${GREEN}[OK]${NC}    ${ISO_NAMES[$key]} (${key}.iso, $size)"
        else
            echo -e "  ${RED}[FEHLT]${NC} ${ISO_NAMES[$key]} (${key}.iso)"
        fi
    done
    echo "-------------------------------------------"
    echo -e "Freier Speicher: $(freier_speicher_gb) GB"
    echo ""
}

# =============================================================
# START
# =============================================================

echo ""
echo "================================================="
echo -e "   ${BOLD}USB Flasher - ISO Downloader${NC}"
echo "================================================="

# Tool pruefen
TOOL=$(check_tool)
if [ -z "$TOOL" ]; then
    echo -e "${RED}Fehler: weder wget noch curl gefunden.${NC}"
    echo "Installieren mit: sudo apt install wget"
    exit 1
fi
echo -e "Download-Tool: ${GREEN}$TOOL${NC}"

# ISO-Ordner anlegen falls nicht vorhanden
mkdir -p "$ISO_DIR"

# Status anzeigen
zeige_status

# =============================================================
# MENUE
# =============================================================
echo -e "${BOLD}Was moechtest du tun?${NC}"
echo ""
echo "  1) Alle fehlenden Linux-ISOs herunterladen"
echo "  2) Einzelne ISO auswaehlen"
echo "  3) Alle ISOs neu herunterladen (ueberschreiben)"
echo "  4) Nur Status anzeigen"
echo "  5) Beenden"
echo ""
read -rp "Auswahl (1-5): " AUSWAHL

case $AUSWAHL in

    # ----------------------------------------------------------
    1) # Alle fehlenden Linux-ISOs
    # ----------------------------------------------------------
    echo ""
    echo -e "${YELLOW}Lade alle fehlenden Linux-ISOs...${NC}"
    echo -e "${YELLOW}Hinweis: Windows-ISOs (w10, w11) muessen manuell heruntergeladen werden.${NC}"
    echo -e "${YELLOW}  -> https://www.microsoft.com/de-de/software-download/windows10${NC}"
    echo -e "${YELLOW}  -> https://www.microsoft.com/de-de/software-download/windows11${NC}"
    echo ""

    for key in u24 mint debian fedora arch z18 bazzite; do
        if [ "$(iso_vorhanden $key)" = "true" ]; then
            echo -e "${GREEN}  Ueberspringe ${ISO_NAMES[$key]} - bereits vorhanden${NC}"
            continue
        fi

        # Speicherplatz pruefen
        frei=$(freier_speicher_gb)
        benoetigt=${ISO_SIZES[$key]}
        if [ "$frei" -lt "$benoetigt" ]; then
            echo -e "${RED}  Nicht genug Speicher fuer ${ISO_NAMES[$key]} (benoetigt ~${benoetigt}GB, frei: ${frei}GB)${NC}"
            continue
        fi

        download_iso "$key" "${ISO_URLS[$key]}" "$TOOL"
    done
    ;;

    # ----------------------------------------------------------
    2) # Einzelne ISO auswaehlen
    # ----------------------------------------------------------
    echo ""
    echo -e "${BOLD}Welche ISO moechtest du herunterladen?${NC}"
    echo ""
    i=1
    declare -a KEYS_ORDERED=(w10 w11 u24 mint debian fedora arch z18 bazzite)
    for key in "${KEYS_ORDERED[@]}"; do
        status=""
        [ "$(iso_vorhanden $key)" = "true" ] && status="${GREEN}[vorhanden]${NC}" || status="${RED}[fehlt]${NC}"
        echo -e "  $i) ${ISO_NAMES[$key]} ($status)"
        ((i++))
    done
    echo "  0) Zurueck"
    echo ""
    read -rp "Auswahl: " ISO_AUSWAHL

    if [ "$ISO_AUSWAHL" = "0" ]; then
        exit 0
    fi

    idx=$((ISO_AUSWAHL - 1))
    key="${KEYS_ORDERED[$idx]}"

    if [ -z "$key" ]; then
        echo -e "${RED}Ungueltige Auswahl${NC}"
        exit 1
    fi

    # Windows gesondert behandeln
    if [ "$key" = "w10" ] || [ "$key" = "w11" ]; then
        echo ""
        echo -e "${YELLOW}Windows-ISOs koennen nicht automatisch heruntergeladen werden.${NC}"
        echo -e "Microsoft verwendet tokenbasierte Download-Links die nur im Browser funktionieren."
        echo ""
        if [ "$key" = "w10" ]; then
            echo -e "Download-Seite: ${CYAN}https://www.microsoft.com/de-de/software-download/windows10${NC}"
        else
            echo -e "Download-Seite: ${CYAN}https://www.microsoft.com/de-de/software-download/windows11${NC}"
        fi
        echo ""
        echo -e "ISO herunterladen, dann per SCP uebertragen:"
        echo -e "  ${CYAN}scp ${key}.iso pi@flasher.local:/home/pi/isos/${key}.iso${NC}"
        exit 0
    fi

    # Speicherplatz pruefen
    frei=$(freier_speicher_gb)
    benoetigt=${ISO_SIZES[$key]}
    if [ "$frei" -lt "$benoetigt" ]; then
        echo -e "${RED}Nicht genug Speicher (benoetigt ~${benoetigt}GB, frei: ${frei}GB)${NC}"
        exit 1
    fi

    # Bereits vorhanden?
    if [ "$(iso_vorhanden $key)" = "true" ]; then
        read -rp "$(echo -e "${YELLOW}${ISO_NAMES[$key]} ist bereits vorhanden. Ueberschreiben? (j/N): ${NC}")" CONFIRM
        if [[ ! "$CONFIRM" =~ ^[jJ]$ ]]; then
            echo "Abgebrochen."
            exit 0
        fi
    fi

    download_iso "$key" "${ISO_URLS[$key]}" "$TOOL"
    ;;

    # ----------------------------------------------------------
    3) # Alle neu herunterladen
    # ----------------------------------------------------------
    echo ""
    echo -e "${RED}Achtung: Alle vorhandenen Linux-ISOs werden ueberschrieben!${NC}"
    read -rp "Wirklich fortfahren? (j/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[jJ]$ ]]; then
        echo "Abgebrochen."
        exit 0
    fi

    for key in u24 mint debian fedora arch z18 bazzite; do
        frei=$(freier_speicher_gb)
        benoetigt=${ISO_SIZES[$key]}
        if [ "$frei" -lt "$benoetigt" ]; then
            echo -e "${RED}Nicht genug Speicher fuer ${ISO_NAMES[$key]} - ueberspringe${NC}"
            continue
        fi
        download_iso "$key" "${ISO_URLS[$key]}" "$TOOL"
    done
    ;;

    # ----------------------------------------------------------
    4) # Nur Status
    # ----------------------------------------------------------
    zeige_status
    ;;

    5) exit 0 ;;
    *) echo -e "${RED}Ungueltige Auswahl${NC}"; exit 1 ;;
esac

echo ""
zeige_status
echo -e "${GREEN}Fertig!${NC}"
echo ""
