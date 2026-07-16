# Wir holen uns die Werkzeuge um mit den Pins(zum Steuern einzelner Pins am ESP32) und SPI(Kommunikationsprotokoll) zu arbeiten
from machine import Pin, SPI


class MFRC522:

    # Das sind Statuscodes - wie Ampelfarben
    OK = 0        # Alles hat geklappt ✅
    NOTAGERR = 1  # Keine Karte gefunden ⚠️
    ERR = 2       # Fehler ❌

    # Befehle die wir an den Reader schicken können
    REQIDL = 0x26    # "Suche nach Karten in der Nähe"
    REQALL = 0x52    # "Suche nach allen Karten"
    AUTHENT1A = 0x60 # Passwort Typ A (Lesen)
    AUTHENT1B = 0x61 # Passwort Typ B (Schreiben)

    # Diese Funktion wird einmal aufgerufen wenn wir den Reader starten
    # Sie richtet alle Pins und die SPI Verbindung ein
    #def __init__(self, sck, mosi, miso, rst, cs):
    def __init__(self, spi, cs):
        # Wir sagen dem ESP32 welche Pins er benutzen soll
        #self.sck = Pin(sck, Pin.OUT)   # Takt Pin - gibt den Rhythmus vor
        #self.mosi = Pin(mosi, Pin.OUT) # Daten rausschicken (ESP32->Reader) Pin
        #self.miso = Pin(miso)          # Daten empfangen (Reader->ESP32) Pin
        #self.rst = Pin(rst, Pin.OUT)   # Reset Pin - startet Reader neu
        #self.cs = Pin(cs, Pin.OUT)     # Chip Select - aktiviert den Reader

        # Reader erstmal ausschalten und deaktivieren
        #self.rst.value(0)  # Reset auf 0 = Reader schläft
        #self.cs.value(1)   # CS auf 1 = Reader nicht ausgewählt (deaktiviert)

        # SPI Verbindung einrichten - das ist die "Datenautobahn" zwischen
        # ESP32 und RFID Reader
        #self.spi = SPI(1, baudrate=100000, polarity=0, phase=0,
        #               sck=self.sck, mosi=self.mosi, miso=self.miso)
        #self.spi.init() # Verbindung starten
        self.spi = spi
        self.cs = cs
        self.cs.value(1)
        # Reader wieder aufwecken
        #self.rst.value(1)  # Reset auf 1 = Reader ist wach
        self.init()        # Reader initialisieren

    # Diese Funktion schreibt einen Wert in ein Register des Readers
    # Register sind wie kleine Speicherfächer im Reader
    def _wreg(self, reg, val):

        self.cs.value(0)  # Reader aktivieren - "Ich rede jetzt mit dir"
        # Adresse des Registers schicken:
        #  - reg << 1: Adresse um 1 Bit nach links verschieben (weil das LSB für Lesen/Schreiben reserviert ist)
        #  - & 0x7e: Sicherstellen, dass Bit 0 (Lesen) & Bit 7 auf 0 bleiben -> bedeutet Schreiben
        #  - & 0xff: nur 8 Bits behalten
        self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
        # Den eigentlichen Wert schicken
        self.spi.write(b'%c' % int(0xff & val))
        self.cs.value(1)  # Reader deaktivieren - "Ich bin fertig"

    # Diese Funktion liest einen Wert aus einem Register
    def _rreg(self, reg):

        self.cs.value(0)  # Reader aktivieren
        # Adresse schicken und sagen dass wir lesen wollen
        #  gleich wie in _wreg aber mit | 0x80 um Bit 7 auf 1 zu setzen -> bedeutet dem Reader "Lese von diesem Register"
        self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
        val = self.spi.read(1)  # Einen Wert zurücklesen
        self.cs.value(1)  # Reader deaktivieren

        return val[0]  # Wert zurückgeben

    # Bestimmte Bits in einem Register auf 1 setzen
    #   Erst lesen (_rreg), dann mit | bestimmte Bits auf 1 setzen, dann zurückschreiben (_wreg)
    #   Bsp.: mask = 0x03 = 00000011 -> letzten 2 Bits werden 1, Rest bleibt gleich 
    def _sflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    # Bestimmte Bits in einem Register auf 0 setzen
    #   ~mask = alle Bits umdrehen, dann mit & die gewünschten Bits auf 0 setzen
    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    # Diese Funktion schickt einen Befehl an die Karte und wartet auf Antwort
    # cmd = welcher Befehl, send = welche Daten mitschicken
    def _tocard(self, cmd, send):

        recv = []              # Leere Liste für die Antwort
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR        # Erstmal gehen wir von Fehler aus

        # Je nach Befehl verschiedene Einstellungen
        if cmd == 0x0E:        # Authentifizierungs-Befehl?
            irq_en = 0x12      # Für diese Ereignisse Interrupt aktivieren
            wait_irq = 0x10    # Auf diesen Interrupt warten
        elif cmd == 0x0C:      # Sende/Empfangs-Befehl?
            irq_en = 0x77
            wait_irq = 0x30

        # Reader für Kommunikation vorbereiten
        self._wreg(0x02, irq_en | 0x80) # Interrupts aktivieren
        self._cflags(0x04, 0x80)        # Interrupt-Flags löschen
        self._sflags(0x0A, 0x80)        # FIFO-Puffer leeren
        self._wreg(0x01, 0x00)          # Aktuellen Befehl stoppen

        # Daten in den Sendepuffer nach FIFO schreiben
        for c in send:
            self._wreg(0x09, c) # Jeden Byte ins FIFO schreiben
        self._wreg(0x01, cmd)  # Befehl ausführen

        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)  # Senden starten

        # Fragen 2000 Mal nach ob der Reader fertig ist
        # Schleife endet wenn Reader fertig ist oder wenn 2000 Durchläufe erreicht sind
        i = 2000
        while True:
            n = self._rreg(0x04)  # Interrupt-Status lesen
            i -= 1
            # Schleife beenden wenn fertig oder Timeout
            if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break

        self._cflags(0x0D, 0x80)  # Senden stoppen

        # Antwort auswerten
        # 0x06 ist das Fehler-Register - wenn Bits 0x1B alle 0 sind = kein Fehler
        if i:   # Wenn nicht Timeout
            if (self._rreg(0x06) & 0x1B) == 0x00:  # Kein Fehler?
                stat = self.OK  # Alles gut!

                if n & irq_en & 0x01:   
                    stat = self.NOTAGERR  # Timer abgelaufen = Keine Karte gefunden
                elif cmd == 0x0C:
                    # Empfangene Daten auslesen
                    n = self._rreg(0x0A)    # Anzahl der empfangenen Bytes
                    lbits = self._rreg(0x0C) & 0x07 # Anzahl der empfangenen Bits im letzten Byte
                    # Gesamte Bit-Anzahl berechnen
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8

                    if n == 0: # wenn nichts da, lesen wir trotzdem 1 Byte
                        n = 1
                    elif n > 16: # wenn mehr als 16 Bytes da, lesen wir trotzdem nur 16 Bytes
                        n = 16

                    # Alle empfangenen Bytes sammeln
                    for _ in range(n):
                        recv.append(self._rreg(0x09))   # Alle Bytes aus FIFO lesen
            else:
                stat = self.ERR  # Fehler aufgetreten

        return stat, recv, bits  # Status + empfangene Daten + Bit-Anzahl zurückgeben

    # Prüfsumme berechnen - wie eine Kontrollrechnung ob Daten korrekt sind
    def _crc(self, data):

        self._cflags(0x05, 0x04)    # CRC-Fertig-Flag löschen
        self._sflags(0x0A, 0x80)    # FIFO leeren

        for c in data:
            self._wreg(0x09, c) # Daten in FIFO schreiben

        self._wreg(0x01, 0x03)  # CRC Berechnung starten

        i = 0xFF
        # Warten bis die CRC Berechnung fertig ist (Bit 0x04 in Register 0x05 wird gesetzt)
        while True:
            n = self._rreg(0x05)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break

        # Die zwei Bytes der Prüfsumme zurückgeben
        return [self._rreg(0x22), self._rreg(0x21)]

    # Reader grundlegend einrichten - wird einmal beim Start aufgerufen
    def init(self):

        self.reset()             # Erstmal alles zurücksetzen
        self._wreg(0x2A, 0x8D)   # Timer: Vorteiler einstellen
        self._wreg(0x2B, 0x3E)   # Timer: weiterer Vorteiler
        self._wreg(0x2D, 30)     # Timer: läuft 30 Einheiten
        self._wreg(0x2C, 0)      # Timer: Startwert 0
        self._wreg(0x15, 0x40)   # ASK Modulation = wie das Funksignal aussieht
        self._wreg(0x11, 0x3D)   # CRC: auf beide Richtungen aktivieren
        self.antenna_on()         # Antenne einschalten

    # Reader komplett zurücksetzen
    def reset(self):
        self._wreg(0x01, 0x0F)

    # Antenne ein oder ausschalten
    # on=True = Antenne an, on=False = Antenne aus
    def antenna_on(self, on=True):

        if on and ~(self._rreg(0x14) & 0x03):   # Register 0x14 steuert Antennentreiber
            self._sflags(0x14, 0x03)  # Antenne AN: Bits 0 und 1 auf 1 setzen
        else:
            self._cflags(0x14, 0x03)  # Antenne AUS: Bits 0 und 1 auf 0 setzen

    # Nach Karten in der Nähe suchen
    #   mode = REGIDL (Reader sendet diesen Code per Funk & wartet ob eine Karte antwortet)
    def request(self, mode):

        self._wreg(0x0D, 0x07)  # Alle 7 Bits senden (REQA ist 7-Bit lang)
        (stat, recv, bits) = self._tocard(0x0C, [mode]) # Befehl schicken

        # Wenn keine gültige Antwort kam - Fehler
        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR

        return stat, bits  # Status zurückgeben

    # Die eindeutige ID der Karte auslesen
    def anticoll(self):

        ser_chk = 0
        ser = [0x93, 0x20]  # Befehl um ID anzufragen

        self._wreg(0x0D, 0x00)
        (stat, recv, bits) = self._tocard(0x0C, ser)

        if stat == self.OK:
            if len(recv) == 5:  # ID hat genau 5 Bytes
                # Prüfen ob die ID korrekt ist
                for i in range(4):
                    ser_chk = ser_chk ^ recv[i]
                if ser_chk != recv[4]: # wenn berechnetes Prüfbyte != empfangenes Prüfbyte -> Fehler
                    stat = self.ERR  # ID ist fehlerhaft
            else:
                stat = self.ERR  # Falsche Datenlänge

        return stat, recv  # Status und ID zurückgeben

    # Eine bestimmte Karte auswählen wenn mehrere in der Nähe sind
    def select_tag(self, ser):

        buf = [0x93, 0x70] + ser[:5] # Befehl + erste 5 Bytes der UID
        buf += self._crc(buf)  # Prüfsumme anhängen
        (stat, recv, bits) = self._tocard(0x0C, buf)
        return self.OK if (stat == self.OK) and (bits == 0x18) else self.ERR

    # Karte mit Passwort entsperren um geschützte Bereiche zu lesen
    # Um gesicherte Daten zu lesen braucht man Passwort ( sect = Schlüssel, 6 Bytes)
    # mode ist A oder B ( zwei verschiedene Schlüssel pro Block)
    def auth(self, mode, addr, sect, ser):
        return self._tocard(0x0E, [mode, addr] + sect + ser[:4])[0]

    # Verschlüsselung wieder ausschalten nach dem Lesen
    def stop_crypto1(self):
        self._cflags(0x08, 0x08)

    # Einen Block Daten von der Karte lesen
    # addr = welcher Block gelesen werden soll
    def read(self, addr):

        data = [0x30, addr]     # 0x30 = MIFARE Lese-Befehl
        data += self._crc(data) # Prüfsumme anhängen
        (stat, recv, _) = self._tocard(0x0C, data)
        return recv if stat == self.OK else None  # Daten oder None zurückgeben

    # Einen Block Daten auf die Karte schreiben
    # addr = welcher Block, data = was geschrieben werden soll
    def write(self, addr, data):

        buf = [0xA0, addr]      # 0xA= = MIFARE Schreib-Befehl
        buf += self._crc(buf)   # Prüfsumme anhängen
        (stat, recv, bits) = self._tocard(0x0C, buf)

        # Prüfen ob der Reader bereit zum Schreiben ist
        if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
            stat = self.ERR  # Reader nicht bereit
        else:
            buf = []
            for i in range(16):       # Genau 16 Bytes schreiben
                buf.append(data[i])
            buf += self._crc(buf)     # Prüfsumme anhängen
            (stat, recv, bits) = self._tocard(0x0C, buf)
            # Prüfen ob Schreiben erfolgreich war
            if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                stat = self.ERR

        return stat  # Erfolg oder Fehler zurückgeben