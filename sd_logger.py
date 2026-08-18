import json
import os
import time
from machine import SPI, Pin
import sdcard

# Globale Variablen für den Logger
_sd_mounted = False
_log_file = "/sd/log_data.json"


def init_sd():
    """Initialisiert und mountet die SD-Karte einmalig."""
    global _sd_mounted
    if _sd_mounted:
        return True

    # Pins für Waveshare ESP32-S3-ETH
    SD_SCK = 7
    SD_MOSI = 6
    SD_MISO = 5
    SD_CS = 4

    try:
        spi = SPI(
            1,
            baudrate=10000000,
            sck=Pin(SD_SCK),
            mosi=Pin(SD_MOSI),
            miso=Pin(SD_MISO),
        )
        sd = sdcard.SDCard(spi, Pin(SD_CS))
        vfs = os.VfsFat(sd)
        os.mount(vfs, "/sd")
        _sd_mounted = True
        print("[SD] Karte erfolgreich initialisiert und gemountet.")
        return True
    except Exception as e:
        print("[SD FEHLER] Mounten fehlgeschlagen:", e)
        return False


def log_rfid_scan(tag_id, status="OK", station="Station_01"):
    """Schreibt einen neuen RFID-Scan im JSON-Format auf die SD-Karte."""
    if not _sd_mounted:
        if not init_sd():
            print("[SD FEHLER] Kann nicht schreiben, SD-Karte nicht bereit.")
            return False

    # JSON-Datensatz aufbauen
    data = {
        "timestamp": time.time(),
        "tag_id": str(tag_id),
        "status": status,
        "station": station,
    }

    try:
        # Datensatz als neue Zeile anhängen (JSON Lines)
        with open(_log_file, "a") as f:
            f.write(json.dumps(data) + "\n")
        print(f"[SD LOG] Gespeichert: {data['tag_id']}")
        return True
    except Exception as e:
        print("[SD FEHLER] Schreiben fehlgeschlagen:", e)
        return False