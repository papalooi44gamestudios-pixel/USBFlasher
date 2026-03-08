from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

doc = SimpleDocTemplate("/mnt/user-data/outputs/USB_Flasher_Anleitung.pdf", pagesize=A4,
                        leftMargin=20*mm, rightMargin=20*mm,
                        topMargin=20*mm, bottomMargin=20*mm)

title_style = ParagraphStyle('title', fontSize=22, fontName='Helvetica-Bold', spaceAfter=6, textColor=colors.HexColor('#1a1a2e'))
h1_style    = ParagraphStyle('h1', fontSize=14, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=4, textColor=colors.HexColor('#16213e'))
h2_style    = ParagraphStyle('h2', fontSize=11, fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=3, textColor=colors.HexColor('#0f3460'))
body_style  = ParagraphStyle('body', fontSize=9, fontName='Helvetica', spaceAfter=4, leading=13)
code_style  = ParagraphStyle('code', fontSize=7.5, fontName='Courier', spaceAfter=3,
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
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ])

def code_block(text):
    return Paragraph(text.replace('\n','<br/>').replace(' ','&nbsp;'), code_style)

def cell(text, style=None):
    if style is None:
        style = ParagraphStyle('cell', fontSize=8, fontName='Helvetica', leading=10, wordWrap='CJK')
    return Paragraph(str(text), style)

def hcell(text):
    style = ParagraphStyle('hcell', fontSize=8, fontName='Helvetica-Bold', leading=10, textColor=colors.white, wordWrap='CJK')
    return Paragraph(str(text), style)

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

# =============================================================
# TITEL
# =============================================================
story.append(Paragraph("USB Flasher v2 – Projektdokumentation", title_style))
story.append(Paragraph("Raspberry Pi Zero 2W | LCD-Menue + Numpad | Multi-OS Flash-Geraet", 
    ParagraphStyle('sub', fontSize=11, fontName='Helvetica', textColor=colors.grey, spaceAfter=4)))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
story.append(Spacer(1, 6))
story.append(Paragraph("Projektbeschreibung", h1_style))
story.append(Paragraph(
    "Ein kompaktes Geraet das per LCD-Menue oder USB-Numpad ein Betriebssystem auswaehlt und "
    "einen angeschlossenen USB-Stick damit flasht. Das JOY-IT LCD-Modul (20x4 Zeichen + 4 Buttons) "
    "steckt direkt auf den GPIO-Header des Pi Zero 2W. Ueber einen USB-Hub werden Numpad und "
    "USB-Stick gleichzeitig betrieben. Das Geraet startet automatisch beim Einschalten, "
    "Herunterfahren erfolgt ueber einen Menue-Eintrag.",
    body_style))

# =============================================================
# MATERIALLISTE
# =============================================================
story.append(Paragraph("Materialliste", h1_style))
mat_data = [
    [hcell('Teil'), hcell('Menge'), hcell('Preis (ca.)'), hcell('Hinweis'), hcell('OK')],
    [cell('Raspberry Pi Zero 2W (mit Pins)'), cell('1x'), cell('~22 EUR'),
     cell('MIT vorgeloetetem GPIO-Header kaufen (z.B. Berrybase "with headers")'), cb()],
    [cell('JOY-IT LCD 20x4 + 4 Buttons'), cell('1x'), cell('4,50 EUR'),
     cell('Reichelt Art.-Nr.: RPI LCD20X4 4BYL – steckt direkt auf GPIO-Header'), cb()],
    [cell('Powered USB Hub'), cell('1x'), cell('~10 EUR'),
     cell('Mit eigener Stromversorgung, mind. 2 Ports'), cb()],
    [cell('USB Numpad'), cell('1x'), cell('~8 EUR'),
     cell('Beliebiges USB-Numpad, wird per evdev ausgelesen'), cb()],
    [cell('SD-Karte (min. 64 GB)'), cell('1x'), cell('~10 EUR'),
     cell('Fuer OS + ISOs (alle 9 ISOs ca. 31 GB)'), cb()],
    [cell('Micro-USB Netzteil 5V/2,5A'), cell('1x'), cell('~8 EUR'),
     cell('Offizielles Raspberry Pi Netzteil empfohlen'), cb()],
    [cell('Micro-USB Kabel (hochwertig)'), cell('1x'), cell('-'),
     cell('Billiges Kabel verursacht Spannungsabfaelle – Originalzubehoer nutzen'), cb()],
    [cell('Gehaeuse'), cell('1x'), cell('-'),
     cell('Wird selbst 3D-gedruckt'), cb()],
]
mat_t = Table(mat_data, colWidths=[45*mm, 14*mm, 22*mm, 72*mm, 11*mm])
mat_t.setStyle(TableStyle([
    *tbl_style().getCommands(),
    ('ALIGN', (4,0), (4,-1), 'CENTER'),
    ('VALIGN', (4,1), (4,-1), 'MIDDLE'),
]))
story.append(mat_t)
story.append(Spacer(1,4))
story.append(Paragraph("<b>Gesamtkosten (ca.): 63 EUR</b>", body_style))

# =============================================================
# ANSCHLUESSE
# =============================================================
story.append(Paragraph("Anschluesse – Uebersicht", h1_style))
story.append(Paragraph(
    "Die Hardware-Verkabelung ist minimal – das LCD-Modul steckt direkt auf den GPIO-Header, "
    "alles andere laeuft ueber die USB-Ports.",
    body_style))

anschluss_data = [
    [hcell('Pi Zero 2W Anschluss'), hcell('Verbunden mit'), hcell('Hinweis')],
    [cell('GPIO-Header (40 Pin)'), cell('JOY-IT LCD-Modul (direkt aufgesteckt)'),
     cell('Modul nutzt I2C: Pin 2 (5V), Pin 3 (SDA), Pin 5 (SCL), Pin 6 (GND)')],
    [cell('Micro-USB Power (links)'), cell('5V Netzteil'),
     cell('Nur Strom – kein Datentransfer')],
    [cell('Micro-USB OTG (rechts)'), cell('Powered USB Hub'),
     cell('Hub -> USB Numpad + USB Stick (zu flashen)')],
    [cell('Mini-HDMI'), cell('Ungenutzt'), cell('Wird nicht benoetigt')],
]
story.append(Table(anschluss_data, colWidths=[45*mm, 60*mm, 56*mm], style=tbl_style('#16213e')))
story.append(Spacer(1,6))

story.append(Paragraph("GPIO-Belegung durch LCD-Modul", h1_style))
story.append(Paragraph(
    "Das JOY-IT RB-LCD20X4 kommuniziert per I2C und belegt daher nur 4 Pins. "
    "Die 4 Buttons auf dem Modul sind intern verdrahtet und werden ueber GPIO ausgelesen. "
    "Genaue Button-Pins laut Datenblatt pruefen und ggf. in flasher.py anpassen.",
    body_style))

gpio_data = [
    [hcell('Funktion'), hcell('GPIO (BCM)'), hcell('Physischer Pin'), hcell('Hinweis')],
    [cell('LCD I2C SDA (Daten)'), cell('GPIO 2'), cell('Pin 3'),
     cell('I2C Datenleitung')],
    [cell('LCD I2C SCL (Takt)'), cell('GPIO 3'), cell('Pin 5'),
     cell('I2C Taktleitung')],
    [cell('LCD VCC'), cell('–'), cell('Pin 2 (5V)'),
     cell('Versorgungsspannung')],
    [cell('LCD GND'), cell('–'), cell('Pin 6 (GND)'),
     cell('Masse')],
    [cell('LCD Button 1 (Hoch)'), cell('GPIO 21'), cell('Pin 40'),
     cell('Standardwert – laut Datenblatt pruefen')],
    [cell('LCD Button 2 (Runter)'), cell('GPIO 20'), cell('Pin 38'),
     cell('Standardwert – laut Datenblatt pruefen')],
    [cell('LCD Button 3 (OK)'), cell('GPIO 16'), cell('Pin 36'),
     cell('Standardwert – laut Datenblatt pruefen')],
    [cell('LCD Button 4 (Zurueck)'), cell('GPIO 12'), cell('Pin 32'),
     cell('Standardwert – laut Datenblatt pruefen')],
]
story.append(Table(gpio_data, colWidths=[42*mm, 25*mm, 30*mm, 64*mm], style=tbl_style('#16213e')))
story.append(Spacer(1,4))
story.append(Paragraph(
    "Tipp: I2C-Adresse des LCD pruefen mit: i2cdetect -y 1 (Standard: 0x27, alternativ 0x3F). "
    "Falls abweichend, LCD_I2C_ADRESSE in flasher.py anpassen.",
    body_style))
story.append(Paragraph(
    "Hinweis zu Button-Pins: Die genauen GPIO-Pins der 4 Buttons sind im Datenblatt des "
    "JOY-IT RB-LCD20X4 dokumentiert. Download: "
    "reichelt.de -> RPI LCD20X4 4BYL -> Datasheet. "
    "Falls die Pins abweichen: BTN_HOCH, BTN_RUNTER, BTN_OK, BTN_ZURUECK in flasher.py anpassen.",
    body_style))

# =============================================================
# BEDIENUNG
# =============================================================
story.append(Paragraph("Bedienung", h1_style))
story.append(Paragraph("LCD-Buttons:", h2_style))
lcd_btn_data = [
    [hcell('Button'), hcell('Funktion')],
    [cell('BTN1'), cell('Menue hoch')],
    [cell('BTN2'), cell('Menue runter')],
    [cell('BTN3'), cell('Auswaehlen / OK / Bestaetigen')],
    [cell('BTN4'), cell('Zurueck / Abbrechen')],
]
story.append(Table(lcd_btn_data, colWidths=[30*mm, 130*mm], style=tbl_style('#0f3460')))
story.append(Spacer(1,6))

story.append(Paragraph("USB Numpad (Direktsteuerung):", h2_style))
numpad_data = [
    [hcell('Taste'), hcell('Funktion')],
    [cell('1'), cell('Windows 10 direkt auswaehlen')],
    [cell('2'), cell('Windows 11 direkt auswaehlen')],
    [cell('3'), cell('Ubuntu 24.04 direkt auswaehlen')],
    [cell('4'), cell('Linux Mint direkt auswaehlen')],
    [cell('5'), cell('Debian direkt auswaehlen')],
    [cell('6'), cell('Fedora direkt auswaehlen')],
    [cell('7'), cell('Arch Linux direkt auswaehlen')],
    [cell('8'), cell('Zorin OS 18 direkt auswaehlen')],
    [cell('9'), cell('Bazzite direkt auswaehlen')],
    [cell('0'), cell('Herunterfahren')],
    [cell('+'), cell('Menue hoch')],
    [cell('-'), cell('Menue runter')],
    [cell('Enter'), cell('Bestaetigen')],
    [cell('*'), cell('Zurueck / Abbrechen')],
]
story.append(Table(numpad_data, colWidths=[30*mm, 130*mm], style=tbl_style('#0f3460')))
story.append(Spacer(1,4))
story.append(Paragraph(
    "Nach Auswahl eines OS wird auf dem LCD eine Bestaetigung angefragt (BTN3 oder Numpad-Enter). "
    "Der Flash-Vorgang laeuft dann automatisch durch, das LCD zeigt Fortschritt und Ergebnis. "
    "Beim Herunterfahren (Taste 0 oder Menue-Eintrag) wird der Pi sauber gestoppt.",
    body_style))

# =============================================================
# LCD ANZEIGE
# =============================================================
story.append(Paragraph("LCD-Anzeige", h1_style))
story.append(Paragraph("Das Display zeigt je nach Zustand unterschiedliche Inhalte:", h2_style))
lcd_data = [
    [hcell('Zustand'), hcell('Zeile 1'), hcell('Zeile 2'), hcell('Zeile 3'), hcell('Zeile 4')],
    [cell('Menue'),      cell('=== USB Flasher ===='), cell('> Windows 10'),   cell('  Windows 11'),    cell('  Ubuntu 24.04')],
    [cell('Bestaetigung'), cell('Bestaetigen?'),        cell('Windows 10'),    cell('>OK     Abbruch'),  cell('BTN3=OK  BTN4=Nein')],
    [cell('Flashvorgang'), cell('Flashe...'),            cell('Windows 10'),   cell('-> /dev/sda'),      cell('Bitte warten... |')],
    [cell('Fertig'),     cell('Fertig!'),                cell('Windows 10'),   cell('erfolgreich'),      cell('geflasht!')],
    [cell('Fehler'),     cell('FEHLER!'),                cell('Windows 10'),   cell('Flash fehlge-'),    cell('schlagen!')],
    [cell('Shutdown'),   cell('Fahre herunter...'),      cell(''),             cell('Bitte warten'),     cell('')],
]
story.append(Table(lcd_data,
    colWidths=[22*mm, 38*mm, 28*mm, 28*mm, 45*mm],
    style=tbl_style('#16213e')))
story.append(Spacer(1,4))
story.append(Paragraph(
    "Das Menue ist scrollbar – alle 9 OS-Eintraege plus Herunterfahren sind erreichbar. "
    "Der Pfeil (>) zeigt den aktuell markierten Eintrag. "
    "Beim Flashvorgang rotiert ein Animations-Symbol in Zeile 4 als Lebenszeichen.",
    body_style))

# =============================================================
# GIT INSTALLATION
# =============================================================
story.append(Paragraph("Installation via Git (empfohlen)", h1_style))
story.append(Paragraph(
    "Die einfachste Methode: Repository klonen, setup.sh ausfuehren. "
    "Spaetere Updates mit git pull + setup.sh.",
    body_style))
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
    "cd /home/pi/usb-flasher\n"
    "git pull\n"
    "sudo bash setup.sh"
))

# =============================================================
# SD-KARTE VORBEREITEN
# =============================================================
story.append(Paragraph("SD-Karte vorbereiten", h1_style))
story.append(Paragraph("Schritt 1: Raspberry Pi OS Lite flashen", h2_style))
story.append(Paragraph(
    "Raspberry Pi Imager von raspberrypi.com/software herunterladen. "
    "Geraet: Raspberry Pi Zero 2, OS: Raspberry Pi OS Lite (64-bit), Speicher: SD-Karte. "
    "Vor dem Flashen Zahnrad-Icon oeffnen.", body_style))

story.append(Paragraph("Schritt 2: SSH und WLAN konfigurieren", h2_style))
story.append(Paragraph(
    "In erweiterten Einstellungen: Hostname 'flasher', SSH aktivieren, "
    "Benutzer 'pi' mit Passwort, WLAN-Daten eintragen, Zeitzone Europe/Berlin.", body_style))

story.append(Paragraph("Schritt 3: Pi starten und verbinden", h2_style))
story.append(code_block(
    "# IP herausfinden:\n"
    "ping flasher.local\n\n"
    "# SSH verbinden:\n"
    "ssh pi@flasher.local"
))

story.append(Paragraph("Schritt 4: System aktualisieren", h2_style))
story.append(code_block(
    "sudo apt update && sudo apt upgrade -y"
))

# =============================================================
# SETUP SCRIPT
# =============================================================
story.append(Paragraph("Setup Script (setup.sh)", h1_style))
story.append(Paragraph(
    "Das setup.sh Script erledigt die gesamte Einrichtung automatisch.",
    body_style))

story.append(code_block(
    "# Am Haupt-PC:\n"
    "scp flasher.py setup.sh get_isos.sh pi@flasher.local:/home/pi/\n\n"
    "# Auf dem Pi:\n"
    "sudo bash /home/pi/setup.sh"
))

setup_data = [
    [hcell('Schritt'), hcell('Aktion')],
    [cell('1'), cell('Erstellt /home/pi/isos/ und /home/pi/logs/')],
    [cell('2'), cell('Installiert python3-rpi.gpio, python3-evdev, python3-smbus, i2c-tools')],
    [cell('3'), cell('Installiert RPLCD per pip (LCD-Bibliothek fuer HD44780 via I2C)')],
    [cell('4'), cell('Installiert woeusb oder woeusb-ng fuer Windows-ISOs')],
    [cell('5'), cell('Aktiviert I2C via raspi-config (fuer LCD-Kommunikation)')],
    [cell('6'), cell('Kopiert flasher.py und get_isos.sh nach /home/pi/')],
    [cell('7'), cell('Legt /ensurance.MD Schutzfunktion an')],
    [cell('8'), cell('Erstellt und aktiviert systemd flasher.service (Autostart)')],
]
story.append(Table(setup_data, colWidths=[18*mm, 143*mm], style=tbl_style('#0f3460')))
story.append(Spacer(1,4))
story.append(Paragraph(
    "Nach dem Setup: i2cdetect -y 1 ausfuehren um LCD-Adresse zu pruefen. "
    "Dann ISOs in /home/pi/isos/ ablegen und sudo reboot.",
    body_style))

# =============================================================
# I2C PRUEFEN
# =============================================================
story.append(Paragraph("I2C und LCD pruefen", h1_style))
story.append(code_block(
    "# I2C-Bus scannen – zeigt angeschlossene Geraete:\n"
    "i2cdetect -y 1\n\n"
    "# Erwartete Ausgabe (Adresse 0x27 oder 0x3F):\n"
    "#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f\n"
    "# 20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --\n\n"
    "# Falls Adresse abweicht, in flasher.py anpassen:\n"
    "# LCD_I2C_ADRESSE = 0x27   # oder 0x3F\n\n"
    "# Kontrast-Einstellung: Poti auf der Rueckseite des LCD-Moduls drehen\n"
    "# falls Anzeige leer bleibt obwohl LCD initialisiert wurde"
))

# =============================================================
# ISO VORBEREITUNG
# =============================================================
story.append(Paragraph("ISOs vorbereiten", h1_style))
iso_namen = [
    [hcell('System'), hcell('Dateiname'), hcell('Groesse ca.')],
    [cell('Windows 10'),   cell('w10.iso'),     cell('5,5 GB')],
    [cell('Windows 11'),   cell('w11.iso'),     cell('6,5 GB')],
    [cell('Ubuntu 24.04'), cell('u24.iso'),     cell('5,0 GB')],
    [cell('Linux Mint'),   cell('mint.iso'),    cell('2,5 GB')],
    [cell('Debian 12'),    cell('debian.iso'),  cell('1,0 GB')],
    [cell('Fedora 41'),    cell('fedora.iso'),  cell('2,0 GB')],
    [cell('Arch Linux'),   cell('arch.iso'),    cell('0,9 GB')],
    [cell('Zorin OS 18'),  cell('z18.iso'),     cell('3,5 GB')],
    [cell('Bazzite'),      cell('bazzite.iso'), cell('~4,0 GB')],
    [hcell('Gesamt'),      hcell(''),           hcell('~ 31 GB')],
]
t = Table(iso_namen, colWidths=[40*mm, 35*mm, 86*mm])
s = tbl_style('#16213e')
s.add('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
s.add('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e8f4f8'))
t.setStyle(s)
story.append(t)
story.append(Spacer(1,4))
story.append(code_block(
    "# Linux-ISOs: automatisch per get_isos.sh\n"
    "bash /home/pi/get_isos.sh\n\n"
    "# Windows-ISOs: manuell per SCP (microsoft.com)\n"
    "scp windows10.iso pi@flasher.local:/home/pi/isos/w10.iso\n"
    "scp windows11.iso pi@flasher.local:/home/pi/isos/w11.iso"
))

# =============================================================
# BAUANLEITUNG
# =============================================================
story.append(Paragraph("Bauanleitung", h1_style))
story.append(Paragraph(
    "Die Hardware-Montage ist sehr einfach – keine Loetarbeiten am Pi noetig.",
    body_style))

schritte = [
    ("1. Pi Zero 2W vorbereiten",
     "Pi Zero 2W MIT vorgeloetetem GPIO-Header kaufen. "
     "SD-Karte einlegen und Pi einmal booten damit Ersteinrichtung ablaeuft."),
    ("2. LCD-Modul aufstecken",
     "JOY-IT RB-LCD20X4 direkt auf den 40-Pin GPIO-Header des Pi Zero 2W aufstecken. "
     "Auf korrekte Ausrichtung achten – Pin 1 (eckige Ecke) am Pi entspricht "
     "Pin 1 am LCD-Modul. Modul sitzt ohne weitere Befestigung stabil auf dem Header."),
    ("3. Netzteil anschliessen",
     "Micro-USB Netzteil an den linken Micro-USB Port (PWR IN) des Pi anschliessen. "
     "Noch nicht einschalten."),
    ("4. USB Hub vorbereiten",
     "Powered USB Hub an den rechten Micro-USB OTG Port des Pi anschliessen "
     "(ggf. mit Micro-USB OTG Adapter). "
     "USB Numpad und spaeter den zu flashenden USB-Stick in den Hub einstecken."),
    ("5. Software einrichten",
     "Pi einschalten, per SSH verbinden, setup.sh ausfuehren (siehe Setup-Abschnitt). "
     "I2C-Adresse mit i2cdetect -y 1 pruefen."),
    ("6. Button-Pins pruefen",
     "Datenblatt des JOY-IT RB-LCD20X4 herunterladen und die GPIO-Pins der 4 Buttons pruefen. "
     "Falls abweichend: BTN_HOCH, BTN_RUNTER, BTN_OK, BTN_ZURUECK in flasher.py anpassen."),
    ("7. Testen",
     "sudo python3 /home/pi/flasher.py ausfuehren. "
     "LCD sollte 'USB Flasher v2' anzeigen und das Menue erscheinen. "
     "Buttons testen. Numpad pruefen: python3 -c \"import evdev; print(evdev.list_devices())\""),
    ("8. ISOs uebertragen",
     "Linux-ISOs per get_isos.sh herunterladen. "
     "Windows-ISOs manuell per SCP uebertragen."),
    ("9. Einbau ins Gehaeuse",
     "Pi mit aufgestecktem LCD-Modul einbauen. "
     "LCD-Modul zeigt nach vorne durch Ausschnitt im Gehaeuse. "
     "USB-Hub intern montieren oder extern lassen. "
     "Netzteil-Kabel und Hub-Kabel nach hinten/unten fuehren."),
    ("10. Abschluss",
     "sudo reboot – ab jetzt startet der Flasher automatisch beim Einschalten. "
     "Zum Herunterfahren im Menue ganz nach unten scrollen: '--- Herunterfahren ---'."),
]
for titel, text in schritte:
    story.append(Paragraph(f"<b>{titel}</b>", body_style))
    story.append(Paragraph(text, ParagraphStyle('ind', fontSize=9, fontName='Helvetica',
                           leftIndent=10, spaceAfter=5, leading=13)))

# =============================================================
# GEHAEUSE
# =============================================================
story.append(Paragraph("Gehaeuse-Hinweise (3D-Druck)", h1_style))
layout_data = [
    [hcell('Position'), hcell('Element'), hcell('Abmessung')],
    [cell('Vorne oben'), cell('LCD-Modul Ausschnitt'), cell('97 x 40 mm (Modulabmessung)')],
    [cell('Vorne unten'), cell('optional: USB-A Ausschnitt fuer Hub'), cell('~15 x 8 mm')],
    [cell('Hinten links'), cell('Micro-USB PWR IN'), cell('Ausschnitt fuer Stecker')],
    [cell('Hinten rechts'), cell('Micro-USB OTG / Hub-Kabel'), cell('Ausschnitt fuer Stecker')],
]
story.append(Table(layout_data, colWidths=[30*mm, 90*mm, 41*mm], style=tbl_style('#16213e')))
story.append(Spacer(1,4))
story.append(Paragraph("Pi Zero 2W Abmessungen: 65 x 30 mm. LCD-Modul: 97 x 40 mm.", body_style))
story.append(Paragraph(
    "Das LCD-Modul ist breiter als der Pi – Gehaeuse-Breite mindestens 100 mm einplanen. "
    "Mindest-Innenhoehe: ca. 30 mm (Pi + aufgestecktes Modul).",
    body_style))

# =============================================================
# AUTOSTART
# =============================================================
story.append(Paragraph("Autostart (systemd)", h1_style))
story.append(code_block(
    "# Service-Datei:\n"
    "[Unit]\n"
    "Description=USB Flasher v2\n"
    "After=multi-user.target\n\n"
    "[Service]\n"
    "ExecStart=/usr/bin/python3 /home/pi/flasher.py\n"
    "Restart=on-failure\n"
    "RestartSec=5\n"
    "User=root\n\n"
    "[Install]\n"
    "WantedBy=multi-user.target\n\n"
    "# Befehle:\n"
    "sudo systemctl enable flasher.service\n"
    "sudo systemctl start flasher.service\n"
    "sudo systemctl status flasher.service"
))

# =============================================================
# SCHUTZFUNKTION
# =============================================================
story.append(Paragraph("Schutzfunktion: ensurance.MD", h1_style))
story.append(Paragraph(
    "Vor jedem Flash prueft der Flasher ob /ensurance.MD auf dem Zielgeraet vorhanden ist. "
    "Diese Datei liegt auf der SD-Karte des Pi. "
    "Wird sie auf dem Zielgeraet gefunden, wird der Flash blockiert und "
    "eine Fehlermeldung auf dem LCD angezeigt. "
    "Das verhindert versehentliches Ueberschreiben der eigenen SD-Karte.",
    body_style))
story.append(code_block(
    "# Schutzdatei anlegen (einmalig, setup.sh erledigt dies automatisch):\n"
    "sudo touch /ensurance.MD\n\n"
    "# Pruefen:\n"
    "ls -la /ensurance.MD"
))

# =============================================================
# LOGS
# =============================================================
story.append(Paragraph("Logs", h1_style))
story.append(code_block(
    "# Neueste Log-Datei lesen:\n"
    "cat /home/pi/logs/$(ls -t /home/pi/logs/ | head -1)\n\n"
    "# Live mitverfolgen:\n"
    "tail -f /home/pi/logs/$(ls -t /home/pi/logs/ | head -1)\n\n"
    "# Alle Fehler:\n"
    "grep 'FEHLER' /home/pi/logs/*.txt\n\n"
    "# Systemd Journal:\n"
    "sudo journalctl -u flasher.service -f"
))

# =============================================================
# TROUBLESHOOTING
# =============================================================
story.append(Paragraph("Troubleshooting", h1_style))
ts_data = [
    [hcell('Problem'), hcell('Loesung')],
    [cell('LCD zeigt nichts'),
     cell('I2C-Adresse pruefen: i2cdetect -y 1. Kontrast-Poti auf Modulrueckseite drehen. '
          'LCD_I2C_ADRESSE in flasher.py anpassen falls Adresse abweicht.')],
    [cell('Buttons reagieren nicht'),
     cell('Datenblatt pruefen, GPIO-Pins in flasher.py anpassen '
          '(BTN_HOCH, BTN_RUNTER, BTN_OK, BTN_ZURUECK).')],
    [cell('Numpad nicht erkannt'),
     cell('python3 -c "import evdev; print(evdev.list_devices())" – '
          'Numpad muss als Eingabegeraet gelistet sein. evdev installiert? '
          'sudo apt install python3-evdev')],
    [cell('RPLCD Import-Fehler'),
     cell('pip3 install RPLCD --break-system-packages')],
    [cell('I2C nicht verfuegbar'),
     cell('sudo raspi-config -> Interface Options -> I2C aktivieren. '
          'Oder: sudo raspi-config nonint do_i2c 0')],
    [cell('Service startet nicht'),
     cell('sudo journalctl -u flasher.service -n 50')],
    [cell('Flash schlaegt fehl'),
     cell('Log pruefen: cat /home/pi/logs/$(ls -t /home/pi/logs/ | head -1)')],
    [cell('woeusb fehlt'),
     cell('sudo apt install woeusb oder sudo apt install woeusb-ng')],
    [cell('USB-Stick nicht erkannt'),
     cell('lsblk ausfuehren – Stick muss als usb-TRAN erscheinen. '
          'Hub mit eigener Stromversorgung nutzen.')],
]
story.append(Table(ts_data, colWidths=[40*mm, 121*mm], style=tbl_style('#16213e')))

# =============================================================
# ERWEITERUNG
# =============================================================
story.append(Paragraph("Erweiterung – Neues OS hinzufuegen", h1_style))
story.append(Paragraph(
    "Neues OS einfach in die SYSTEMS-Liste in flasher.py eintragen. "
    "Kein Hardware-Umbau noetig – das Menue scrollt automatisch.",
    body_style))
story.append(code_block(
    "# In flasher.py, SYSTEMS-Liste ergaenzen:\n"
    "SYSTEMS = [\n"
    "    ...\n"
    "    (\"Pop!_OS\", \"popos.iso\", False),   # einfach anfuegen\n"
    "    (\"Kali Linux\", \"kali.iso\", False),\n"
    "]"
))

doc.build(story)
print("PDF erstellt: USB_Flasher_Anleitung.pdf")
