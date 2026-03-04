import RPi.GPIO as GPIO
import subprocess
import os
import time
import threading
from datetime import datetime

# =============================================================
# KONFIGURATION
# =============================================================

# ISO-Verzeichnis auf der SD-Karte
# Ordner anlegen mit: mkdir -p /home/pi/isos
# ISOs per SCP uebertragen: scp mein.iso pi@flasher.local:/home/pi/isos/
ISO_DIR = "/home/pi/isos/"

# Log-Verzeichnis
LOG_DIR = "/home/pi/logs/"

# Knopf-GPIO : (Anzeigename, ISO-Dateiname, Windows=True/False)
# Windows-ISOs benoetigen woeusb oder woeusb-ng
# Linux-ISOs werden mit dd geflasht
SYSTEMS = {
    2:  ("Windows 10",  "w10.iso",      True),
    3:  ("Windows 11",  "w11.iso",      True),
    4:  ("Ubuntu",      "u24.iso",      False),
    17: ("Linux Mint",  "mint.iso",     False),
    27: ("Debian",      "debian.iso",   False),
    22: ("Fedora",      "fedora.iso",   False),
    10: ("Arch Linux",  "arch.iso",     False),
    9:  ("Zorin OS 18",  "z18.iso",      False),
    11: ("Bazzite",     "bazzite.iso",  False),
}

# GPIO-Pins der LEDs
LED_GREEN  = 18   # Gruen  = Fertig / Bereit
LED_YELLOW = 23   # Gelb   = Flashvorgang laeuft (blinkt)
LED_RED    = 24   # Rot    = Fehler aufgetreten

# Power Button - 3 Sekunden halten fuer sauberen Shutdown
POWER_BTN  = 26

# Debounce-Zeit in Sekunden
DEBOUNCE_TIME = 0.3

# =============================================================
# SETUP
# =============================================================

os.makedirs(LOG_DIR, exist_ok=True)

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_GREEN,  GPIO.OUT)
GPIO.setup(LED_YELLOW, GPIO.OUT)
GPIO.setup(LED_RED,    GPIO.OUT)

for pin in SYSTEMS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(POWER_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Globale Flash-Sperre - verhindert Race Condition bei mehrfachem Tasterdruck
flash_laeuft = threading.Lock()

# =============================================================
# HILFSFUNKTIONEN
# =============================================================

# SESSION_LOG einmalig beim Programmstart festlegen
# Muss vor log() definiert sein damit die Funktion es findet
SESSION_LOG = datetime.now().strftime("logs_%Y-%m-%d_%H-%M-%S") + ".txt"

def log(message, level="INFO"):
    # Schreibt Eintrag in Konsole und in die Session-Log-Datei
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    print(entry)
    with open(os.path.join(LOG_DIR, SESSION_LOG), "a") as f:
        f.write(entry + "\n")

def set_led(green=False, yellow=False, red=False):
    GPIO.output(LED_GREEN,  GPIO.HIGH if green  else GPIO.LOW)
    GPIO.output(LED_YELLOW, GPIO.HIGH if yellow else GPIO.LOW)
    GPIO.output(LED_RED,    GPIO.HIGH if red    else GPIO.LOW)

def blink_yellow(stop_event):
    # Blinkt die gelbe LED solange ein Flash-Vorgang laeuft
    # Gibt dem Nutzer ein Lebenszeichen bei langen Flash-Vorgaengen
    while not stop_event.is_set():
        GPIO.output(LED_YELLOW, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_YELLOW, GPIO.LOW)
        time.sleep(0.5)

def ermittle_target():
    # Ermittelt automatisch den ersten angeschlossenen USB-Stick via lsblk
    # Gibt /dev/sdX zurueck oder None wenn kein USB-Stick gefunden
    try:
        result = subprocess.run(
            ["lsblk", "-ndo", "NAME,TYPE,TRAN"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[1] == "disk" and parts[2] == "usb":
                device = f"/dev/{parts[0]}"
                log(f"USB-Stick erkannt: {device}")
                return device
    except Exception as e:
        log(f"Fehler bei USB-Erkennung: {e}", "FEHLER")
    return None

def usb_stick_vorhanden(device):
    # Prueft ob Geraet existiert und wirklich ein USB-Datentraeger ist
    if device is None or not os.path.exists(device):
        return False
    try:
        result = subprocess.run(
            ["lsblk", "-ndo", "TRAN", device],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "usb"
    except Exception:
        return False

def get_mountpoint(device):
    # Gibt den Mountpoint eines Geraets zurueck falls gemountet
    try:
        result = subprocess.run(
            ["lsblk", "-no", "MOUNTPOINT", device],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().splitlines():
            mp = line.strip()
            if mp:
                return mp
    except Exception:
        pass
    return None

def ermittle_partition(device):
    # Gibt die erste Partition eines Geraets zurueck (z.B. /dev/sda1)
    # Fallback auf das Geraet selbst wenn keine Partition gefunden
    try:
        result = subprocess.run(
            ["lsblk", "-nro", "NAME,TYPE", device],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == "part":
                return f"/dev/{parts[0]}"
    except Exception:
        pass
    return device

def schutz_datei_vorhanden(device):
    # Prueft ob auf dem Zielgeraet eine ensurance.MD liegt
    # Wenn ja wird der Flash blockiert
    # Hinweis: schuetzt nur wenn Datei auf dem Zielgeraet liegt,
    # nicht als absoluter Schutz vor manuell falsch gesetztem TARGET gedacht

    partition = ermittle_partition(device)

    # Zuerst pruefen ob bereits gemountet
    mountpoint = get_mountpoint(partition)
    if mountpoint:
        return os.path.isfile(os.path.join(mountpoint, "ensurance.MD"))

    # Sonst kurz mounten und pruefen
    tmp = "/tmp/flasher_check"
    os.makedirs(tmp, exist_ok=True)
    try:
        mount_result = subprocess.run(
            ["mount", partition, tmp],
            capture_output=True, text=True
        )
        if mount_result.returncode != 0:
            log(f"Mount fehlgeschlagen (Partition: {partition}) - Schutzcheck uebersprungen", "WARNUNG")
            return False
        found = os.path.isfile(os.path.join(tmp, "ensurance.MD"))
        # Sync vor Umount
        subprocess.run(["sync"], capture_output=True)
        subprocess.run(["umount", tmp], capture_output=True)
        return found
    except Exception as e:
        log(f"Fehler beim Schutzcheck: {e}", "WARNUNG")
        # Im Zweifelsfall sicher bleiben und nicht flashen
        try:
            subprocess.run(["umount", tmp], capture_output=True)
        except Exception:
            pass
        return False

def woeusb_cmd():
    # Prueft welches woeusb-Kommando verfuegbar ist
    # Unterstuetzt sowohl woeusb als auch woeusb-ng
    for cmd in ["woeusb", "woeusb-ng"]:
        result = subprocess.run(["which", cmd], capture_output=True)
        if result.returncode == 0:
            log(f"Windows-Flash Tool gefunden: {cmd}")
            return cmd
    return None

def flash(pin):
    # Globale Sperre: verhindert dass waehrend eines laufenden Flashvorgangs
    # ein weiterer gestartet wird (Race Condition)
    if not flash_laeuft.acquire(blocking=False):
        log("Flash laeuft bereits - Eingabe ignoriert", "WARNUNG")
        return

    try:
        # Debounce: warte und pruefe nochmal ob Knopf noch gedrueckt
        time.sleep(DEBOUNCE_TIME)
        if GPIO.input(pin) == GPIO.HIGH:
            return

        name, iso_file, is_windows = SYSTEMS[pin]
        iso_path = os.path.join(ISO_DIR, iso_file)

        log(f"Knopf gedrueckt: {name}")

        # Pruefen ob ISO existiert
        if not os.path.isfile(iso_path):
            log(f"ISO nicht gefunden: {iso_path}", "FEHLER")
            set_led(red=True)
            time.sleep(5)
            set_led()
            return

        # TARGET dynamisch ermitteln
        target = ermittle_target()

        # Pruefen ob USB-Stick angeschlossen und erkannt
        if not usb_stick_vorhanden(target):
            log("Kein USB-Stick gefunden oder Geraet ist kein USB-Datentraeger", "FEHLER")
            set_led(red=True)
            time.sleep(5)
            set_led()
            return

        # Schutzpruefung: ensurance.MD auf dem Zielgeraet?
        if schutz_datei_vorhanden(target):
            log(f"SCHUTZ AKTIV: ensurance.MD auf {target} - Flash blockiert!", "WARNUNG")
            set_led(red=True)
            time.sleep(5)
            set_led()
            return

        log(f"Starte Flash: {name} -> {target}")

        # Gelbe LED blinkt als Lebenszeichen waehrend des Flash-Vorgangs
        stop_blink = threading.Event()
        blink_thread = threading.Thread(target=blink_yellow, args=(stop_blink,), daemon=True)
        blink_thread.start()

        try:
            if is_windows:
                woecmd = woeusb_cmd()
                if woecmd is None:
                    raise Exception("Weder woeusb noch woeusb-ng gefunden. Installieren mit: sudo apt install woeusb")
                result = subprocess.run(
                    [woecmd, "--device", iso_path, target],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        result.returncode, woecmd, result.stderr
                    )
            else:
                # dd ohne capture_output damit status=progress im Journal sichtbar bleibt
                result = subprocess.run(
                    ["dd", f"if={iso_path}", f"of={target}",
                     "bs=4M", "status=progress", "conv=fdatasync"]
                )
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, "dd", "dd Fehler")

            stop_blink.set()
            blink_thread.join()
            log(f"Erfolgreich geflasht: {name}")
            set_led(green=True)
            time.sleep(5)
            set_led()

        except subprocess.CalledProcessError as e:
            stop_blink.set()
            blink_thread.join()
            log(f"Flash fehlgeschlagen: {name} | {e.output}", "FEHLER")
            set_led(red=True)
            time.sleep(5)
            set_led()

        except Exception as e:
            stop_blink.set()
            blink_thread.join()
            log(f"Unerwarteter Fehler: {str(e)}", "FEHLER")
            set_led(red=True)
            time.sleep(5)
            set_led()

    finally:
        # Sperre immer freigeben auch bei Fehler
        flash_laeuft.release()

# =============================================================
# START
# =============================================================

log("USB Flasher gestartet")
log(f"ISO-Verzeichnis: {ISO_DIR}")

# Vorhandene ISOs beim Start pruefen und loggen
for pin, (name, iso_file, _) in SYSTEMS.items():
    iso_path = os.path.join(ISO_DIR, iso_file)
    status = "OK" if os.path.isfile(iso_path) else "FEHLT"
    log(f"  [{status}] {name}: {iso_file}")

# woeusb Verfuegbarkeit pruefen
woecmd = woeusb_cmd()
if woecmd:
    log(f"Windows-Flash: {woecmd} verfuegbar")
else:
    log("Windows-Flash: woeusb/woeusb-ng nicht gefunden - Windows-ISOs nicht flashbar!", "WARNUNG")

# Bereit-Signal (kurzes Blinken)
for _ in range(3):
    set_led(green=True)
    time.sleep(0.2)
    set_led()
    time.sleep(0.2)

log("Bereit. Warte auf Eingabe...")

# =============================================================
# HAUPTSCHLEIFE
# =============================================================

try:
    while True:
        for pin in SYSTEMS:
            if GPIO.input(pin) == GPIO.LOW:
                flash(pin)
                time.sleep(0.3)

        # Power Button: 3 Sekunden halten fuer sauberen Shutdown
        # Laeuft bereits als root (systemd) - kein sudo noetig
        if GPIO.input(POWER_BTN) == GPIO.LOW:
            time.sleep(3)
            if GPIO.input(POWER_BTN) == GPIO.LOW:
                log("Power Button - fahre herunter...")
                set_led(red=True)
                time.sleep(1)
                set_led()
                GPIO.cleanup()
                subprocess.run(["shutdown", "-h", "now"])

        time.sleep(0.05)

except KeyboardInterrupt:
    log("Programm manuell beendet")
    set_led()
    GPIO.cleanup()

except Exception as e:
    log(f"Kritischer Fehler: {str(e)}", "FEHLER")
    set_led(red=True)
    GPIO.cleanup()
