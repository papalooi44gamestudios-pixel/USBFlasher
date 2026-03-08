import RPi.GPIO as GPIO
import subprocess
import os
import time
import threading
import queue
from datetime import datetime

# Versuche RPLCD zu importieren, sonst Dummy fuer Tests
try:
    from RPLCD.i2c import CharLCD
    LCD_VERFUEGBAR = True
except ImportError:
    LCD_VERFUEGBAR = False
    print("[WARNUNG] RPLCD nicht gefunden - LCD deaktiviert (pip install RPLCD)")

# Versuche evdev zu importieren fuer USB-Numpad
try:
    import evdev
    from evdev import ecodes
    NUMPAD_VERFUEGBAR = True
except ImportError:
    NUMPAD_VERFUEGBAR = False
    print("[WARNUNG] evdev nicht gefunden - Numpad deaktiviert (pip install evdev)")

# =============================================================
# KONFIGURATION
# =============================================================

ISO_DIR  = "/home/pi/isos/"
LOG_DIR  = "/home/pi/logs/"

# Betriebssysteme: (Anzeigename, ISO-Dateiname, Windows=True/False)
SYSTEMS = [
    ("Windows 10",   "w10.iso",     True),
    ("Windows 11",   "w11.iso",     True),
    ("Ubuntu 24.04", "u24.iso",     False),
    ("Linux Mint",   "mint.iso",    False),
    ("Debian",       "debian.iso",  False),
    ("Fedora",       "fedora.iso",  False),
    ("Arch Linux",   "arch.iso",    False),
    ("Zorin OS 18",  "z18.iso",     False),
    ("Bazzite",      "bazzite.iso", False),
]

# LCD Konfiguration
# I2C Adresse: Standard 0x27, alternativ 0x3F
# Mit i2cdetect -y 1 pruefen
LCD_I2C_ADRESSE   = 0x27
LCD_I2C_PORT      = 1       # /dev/i2c-1 auf Pi Zero 2W
LCD_ZEILEN        = 4
LCD_SPALTEN       = 20

DEBOUNCE_ZEIT = 0.25  # Sekunden (fuer Numpad)

# =============================================================
# SETUP
# =============================================================

os.makedirs(LOG_DIR, exist_ok=True)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Keine GPIO-Buttons - Navigation ausschliesslich per USB-Numpad

# Globale Flash-Sperre gegen Race Condition
flash_laeuft = threading.Lock()

# Menuesteuerung
menue_index    = 0    # Aktuell ausgewaehltes Element
scroll_offset  = 0    # Erste sichtbare Zeile im Menue

# =============================================================
# LOGGING
# =============================================================

SESSION_LOG = datetime.now().strftime("log_%Y-%m-%d_%H-%M-%S.txt")

def log(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eintrag = f"[{ts}] [{level}] {message}"
    print(eintrag)
    with open(os.path.join(LOG_DIR, SESSION_LOG), "a") as f:
        f.write(eintrag + "\n")

# =============================================================
# LCD ANZEIGE
# =============================================================

lcd = None

def lcd_init():
    global lcd
    if not LCD_VERFUEGBAR:
        return
    try:
        lcd = CharLCD(
            i2c_expander='PCF8574',
            address=LCD_I2C_ADRESSE,
            port=LCD_I2C_PORT,
            cols=LCD_SPALTEN,
            rows=LCD_ZEILEN,
            dotsize=8,
            auto_linebreaks=False
        )
        lcd.clear()
        log("LCD initialisiert")
    except Exception as e:
        log(f"LCD Init fehlgeschlagen: {e}", "FEHLER")
        lcd = None

def lcd_schreibe(zeile, text):
    # Schreibt Text in eine Zeile (0-3), fuellt mit Leerzeichen auf
    if lcd is None:
        return
    try:
        lcd.cursor_pos = (zeile, 0)
        lcd.write_string(text.ljust(LCD_SPALTEN)[:LCD_SPALTEN])
    except Exception as e:
        log(f"LCD Schreibfehler: {e}", "FEHLER")

def lcd_clear():
    if lcd is None:
        return
    try:
        lcd.clear()
    except Exception:
        pass

def zeige_menue():
    # Zeigt das scrollbare OS-Menue auf dem LCD
    # Zeile 1: Titel
    # Zeilen 2-4: 3 OS-Eintraege (mit Pfeil beim ausgewaehlten)
    eintraege = [s[0] for s in SYSTEMS] + ["--- Herunterfahren ---"]

    lcd_schreibe(0, "=== USB Flasher ====")

    for i in range(3):
        idx = scroll_offset + i
        if idx < len(eintraege):
            pfeil = ">" if idx == menue_index else " "
            text = f"{pfeil}{eintraege[idx]}"
        else:
            text = ""
        lcd_schreibe(1 + i, text)

def zeige_status(zeile1="", zeile2="", zeile3="", zeile4=""):
    lcd_schreibe(0, zeile1)
    lcd_schreibe(1, zeile2)
    lcd_schreibe(2, zeile3)
    lcd_schreibe(3, zeile4)

def zeige_bestaetigung(name):
    lcd_schreibe(0, "Bestaetigen?")
    lcd_schreibe(1, name[:LCD_SPALTEN])
    lcd_schreibe(2, "Enter=OK    *=Nein")
    lcd_schreibe(3, "")

# =============================================================
# USB NUMPAD
# =============================================================

numpad_geraet = None

# Mapping Numpad-Tasten -> Aktionen
# 1-9: direkter OS-Index (0-basiert: 1=Index 0, etc.)
# 0:   Shutdown
# +:   Hoch
# -:   Runter
# Enter: OK
# *:   Zurueck
NUMPAD_MAPPING = {
    ecodes.KEY_KP1:     ("select", 0),
    ecodes.KEY_KP2:     ("select", 1),
    ecodes.KEY_KP3:     ("select", 2),
    ecodes.KEY_KP4:     ("select", 3),
    ecodes.KEY_KP5:     ("select", 4),
    ecodes.KEY_KP6:     ("select", 5),
    ecodes.KEY_KP7:     ("select", 6),
    ecodes.KEY_KP8:     ("select", 7),
    ecodes.KEY_KP9:     ("select", 8),
    ecodes.KEY_KP0:     ("shutdown", None),
    ecodes.KEY_KPPLUS:  ("hoch", None),
    ecodes.KEY_KPMINUS: ("runter", None),
    ecodes.KEY_KPENTER: ("ok", None),
    ecodes.KEY_KPASTERISK: ("zurueck", None),
} if NUMPAD_VERFUEGBAR else {}

def finde_numpad():
    # Sucht nach angeschlossenem USB-Numpad via evdev
    if not NUMPAD_VERFUEGBAR:
        return None
    try:
        geraete = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for g in geraete:
            caps = g.capabilities()
            # Numpad hat KEY_KP1 bis KEY_KP9
            if ecodes.EV_KEY in caps:
                keys = caps[ecodes.EV_KEY]
                if ecodes.KEY_KP1 in keys and ecodes.KEY_KP2 in keys:
                    log(f"Numpad gefunden: {g.name} ({g.path})")
                    return g
    except Exception as e:
        log(f"Numpad-Suche fehlgeschlagen: {e}", "WARNUNG")
    return None

# Eingabe-Queue fuer Numpad-Events (Thread-sicher)
eingabe_queue = queue.Queue()

def numpad_thread():
    # Liest Numpad-Events im Hintergrund und legt sie in die Queue
    global numpad_geraet
    while True:
        if numpad_geraet is None:
            numpad_geraet = finde_numpad()
            if numpad_geraet is None:
                time.sleep(3)
                continue
        try:
            for event in numpad_geraet.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    if key_event.keystate == evdev.KeyEvent.key_down:
                        if event.code in NUMPAD_MAPPING:
                            eingabe_queue.put(("numpad", NUMPAD_MAPPING[event.code]))
        except Exception as e:
            log(f"Numpad getrennt oder Fehler: {e}", "WARNUNG")
            numpad_geraet = None
            time.sleep(2)

# =============================================================
# USB-STICK ERKENNUNG
# =============================================================

def ermittle_target():
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
        log(f"Fehler USB-Erkennung: {e}", "FEHLER")
    return None

def usb_stick_vorhanden(device):
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

def ermittle_partition(device):
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
    partition = ermittle_partition(device)
    tmp = "/tmp/flasher_check"
    os.makedirs(tmp, exist_ok=True)

    # Pruefen ob bereits gemountet
    try:
        result = subprocess.run(
            ["lsblk", "-no", "MOUNTPOINT", partition],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().splitlines():
            mp = line.strip()
            if mp:
                return os.path.isfile(os.path.join(mp, "ensurance.MD"))
    except Exception:
        pass

    try:
        r = subprocess.run(["mount", partition, tmp], capture_output=True, text=True)
        if r.returncode != 0:
            log(f"Mount fehlgeschlagen - Flash wird zur Sicherheit blockiert", "WARNUNG")
            return True  # Im Zweifel blockieren
        found = os.path.isfile(os.path.join(tmp, "ensurance.MD"))
        subprocess.run(["sync"], capture_output=True)
        subprocess.run(["umount", tmp], capture_output=True)
        return found
    except Exception as e:
        log(f"Fehler Schutzcheck: {e}", "WARNUNG")
        try:
            subprocess.run(["umount", tmp], capture_output=True)
        except Exception:
            pass
        return False

def woeusb_cmd():
    for cmd in ["woeusb", "woeusb-ng"]:
        result = subprocess.run(["which", cmd], capture_output=True)
        if result.returncode == 0:
            return cmd
    return None

# =============================================================
# FLASH VORGANG
# =============================================================

def starte_flash(index):
    global menue_index, scroll_offset

    if not flash_laeuft.acquire(blocking=False):
        log("Flash laeuft bereits", "WARNUNG")
        zeige_status("Fehler:", "Flash laeuft", "bereits!", "")
        time.sleep(3)
        zeige_menue()
        return

    try:
        name, iso_file, is_windows = SYSTEMS[index]
        iso_path = os.path.join(ISO_DIR, iso_file)

        log(f"Flash gestartet: {name}")

        # ISO vorhanden?
        if not os.path.isfile(iso_path):
            log(f"ISO fehlt: {iso_path}", "FEHLER")
            zeige_status("FEHLER:", "ISO nicht", f"gefunden:", iso_file[:LCD_SPALTEN])
            time.sleep(4)
            return

        # USB-Stick erkennen
        target = ermittle_target()
        if not usb_stick_vorhanden(target):
            log("Kein USB-Stick gefunden", "FEHLER")
            zeige_status("FEHLER:", "Kein USB-Stick", "angeschlossen!", "")
            time.sleep(4)
            return

        # Schutzcheck
        if schutz_datei_vorhanden(target):
            log(f"SCHUTZ: ensurance.MD auf {target}", "WARNUNG")
            zeige_status("SCHUTZ AKTIV!", "Ziel ist SD-Karte", "Flash blockiert", "")
            time.sleep(4)
            return

        # Flash starten - Status anzeigen
        zeige_status(
            "Flashe...",
            name[:LCD_SPALTEN],
            f"-> {target}",
            "Bitte warten..."
        )
        log(f"Flashe {name} auf {target}")

        # Fortschritts-Thread fuer LCD (rotierender Balken)
        stop_event = threading.Event()

        def fortschritt_animation():
            symbole = ["|", "/", "-", "\\"]
            i = 0
            while not stop_event.is_set():
                lcd_schreibe(3, f"Bitte warten... {symbole[i % 4]}")
                i += 1
                time.sleep(0.4)

        anim = threading.Thread(target=fortschritt_animation, daemon=True)
        anim.start()

        try:
            if is_windows:
                woecmd = woeusb_cmd()
                if woecmd is None:
                    raise Exception("woeusb/woeusb-ng nicht gefunden")
                result = subprocess.run(
                    [woecmd, "--device", iso_path, target],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    raise Exception(result.stderr[:80])
            else:
                result = subprocess.run(
                    ["dd", f"if={iso_path}", f"of={target}",
                     "bs=8M", "conv=fdatasync"],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    raise Exception("dd Fehler")

            stop_event.set()
            anim.join()
            log(f"Erfolgreich: {name}")
            zeige_status(
                "Fertig!",
                name[:LCD_SPALTEN],
                "erfolgreich",
                "geflasht!"
            )
            time.sleep(5)

        except Exception as e:
            stop_event.set()
            anim.join()
            log(f"Flash fehlgeschlagen: {e}", "FEHLER")
            zeige_status("FEHLER!", name[:LCD_SPALTEN], "Flash fehlge-", "schlagen!")
            time.sleep(5)

    finally:
        flash_laeuft.release()
        zeige_menue()

# =============================================================
# MENUE NAVIGATION
# =============================================================

GESAMT_EINTRAEGE = len(SYSTEMS) + 1  # +1 fuer Shutdown

def menue_hoch():
    global menue_index, scroll_offset
    if menue_index > 0:
        menue_index -= 1
        if menue_index < scroll_offset:
            scroll_offset = menue_index
        zeige_menue()

def menue_runter():
    global menue_index, scroll_offset
    if menue_index < GESAMT_EINTRAEGE - 1:
        menue_index += 1
        if menue_index >= scroll_offset + 3:
            scroll_offset = menue_index - 2
        zeige_menue()

def menue_ok():
    global menue_index
    if menue_index < len(SYSTEMS):
        # OS ausgewaehlt - Bestaetigung anfordern
        name = SYSTEMS[menue_index][0]
        zeige_bestaetigung(name)

        # Warte auf Numpad Enter oder Stern
        start = time.time()
        while time.time() - start < 30:
            try:
                aktion, wert = eingabe_queue.get_nowait()
                if aktion == "numpad":
                    typ, val = wert
                    if typ == "ok":
                        starte_flash(menue_index)
                        return
                    elif typ == "zurueck":
                        zeige_menue()
                        return
            except queue.Empty:
                pass
            time.sleep(0.05)

        # Timeout - zurueck zum Menue
        zeige_menue()

    else:
        # Shutdown-Eintrag ausgewaehlt
        fahre_herunter()

def direktauswahl(index):
    # Direktauswahl per Numpad-Ziffer
    global menue_index, scroll_offset
    if 0 <= index < len(SYSTEMS):
        menue_index = index
        scroll_offset = max(0, index - 1)
        zeige_menue()
        time.sleep(0.3)
        menue_ok()

def fahre_herunter():
    log("Herunterfahren...")
    zeige_status(
        "Fahre herunter...",
        "",
        "Bitte warten",
        ""
    )
    time.sleep(2)
    GPIO.cleanup()
    subprocess.run(["shutdown", "-h", "now"])

# =============================================================
# EINGABE VERARBEITUNG
# =============================================================

def verarbeite_eingabe(typ, wert):
    if typ == "numpad":
        aktion, val = wert
        if aktion == "select":
            direktauswahl(val)
        elif aktion == "hoch":
            menue_hoch()
        elif aktion == "runter":
            menue_runter()
        elif aktion == "ok":
            menue_ok()
        elif aktion == "zurueck":
            zeige_menue()
        elif aktion == "shutdown":
            fahre_herunter()

# =============================================================
# START
# =============================================================

log("USB Flasher v2 gestartet")
log(f"ISO-Verzeichnis: {ISO_DIR}")

# LCD initialisieren
lcd_init()

# Startmeldung anzeigen
zeige_status(
    "=USB Flasher v2=====",
    "Initialisierung...",
    "",
    ""
)

# ISOs beim Start pruefen
log("ISO-Status:")
for name, iso_file, _ in SYSTEMS:
    iso_path = os.path.join(ISO_DIR, iso_file)
    status = "OK   " if os.path.isfile(iso_path) else "FEHLT"
    log(f"  [{status}] {name}: {iso_file}")

# woeusb pruefen
woecmd = woeusb_cmd()
if woecmd:
    log(f"Windows-Flash: {woecmd} verfuegbar")
else:
    log("Windows-Flash: woeusb nicht gefunden", "WARNUNG")

# Numpad-Thread starten
if NUMPAD_VERFUEGBAR:
    t = threading.Thread(target=numpad_thread, daemon=True)
    t.start()
    log("Numpad-Thread gestartet")

time.sleep(1)
zeige_menue()
log("Bereit.")

# =============================================================
# HAUPTSCHLEIFE
# =============================================================

try:
    while True:
        # Numpad-Events aus Queue verarbeiten
        try:
            typ, wert = eingabe_queue.get_nowait()
            verarbeite_eingabe(typ, wert)
        except queue.Empty:
            pass

        time.sleep(0.05)

except KeyboardInterrupt:
    log("Manuell beendet")
    lcd_clear()
    GPIO.cleanup()

except Exception as e:
    log(f"Kritischer Fehler: {e}", "FEHLER")
    try:
        zeige_status("KRITISCHER", "FEHLER!", str(e)[:LCD_SPALTEN], "Reboot noetig")
    except Exception:
        pass
    GPIO.cleanup()
