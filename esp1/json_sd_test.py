import json
import os
import time
from machine import SPI, Pin
import sdcard

# 1. SD-Karte initialisieren & mounten
SD_SCK = 7
SD_MOSI = 6
SD_MISO = 5
SD_CS = 4

spi = SPI(1, baudrate=10000000, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO))

try:
    sd = sdcard.SDCard(spi, Pin(SD_CS))
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    print("SD-Karte erfolgreich gemountet!")
except Exception as e:
    print("Fehler beim Mounten der SD-Karte:", e)

# 2. Beispieldaten struktuID-Scan)
log_entry = {
    "timestamp": time.time(),  # Sekundenzähler / Zeitstempel
    "tag_id": "13524678",  # Gemessene RFID UID
    "status": "OK",  # Status / Prüfergebnis
    "station": "Station_01",  # Fertigungsstson_file_path = "/sd/log_data.json"
}

# Dateipfad festlegen
json_file_path = "/sd/log_data.json"

# 3. Funktion zum Anhängen von JSON-Daten (JSON Lines Format)
def save_json_log(data, filepath):
    try:
        # Im "a" (Append) Modus öffnen, um neue Einträge unten anzuhängen
        with open(filepath, "a") as file:
            # json.dumps wandelt das Python-Dictionary in einen JSON-String um
            file.write(json.dumps(data) + "\n")
        print("-> Daten erfolgreich als JSON gespeichert!")
    except Exception as e:
        print("-> Fehler beim Schreiben:", e)


# 4. Daten speichern
save_json_log(log_entry, json_file_path)

# 5. Inhalt der JSON-Datei zur Kontrolle auslesen
print("\n--- Aktueller Inhalt von log_data.json ---")
try:
    with open(json_file_path, "r") as file:
        for line in file:
            # Zeile für Zeile wieder in ein Python-Dictionary umwandeln
            parsed_data = json.loads(line.strip())
            print("Gelesen:", parsed_data)
except Exception as e:
    print("Fehler beim Lesen:", e)

# Sauber unmounten
os.umount("/sd")
print("\nSD-Karte unmounted. Fertig!")