# main.py
# Testdatei für das Traceability-System
from mfrc522 import MFRC522
from machine import SPI, Pin

import time

print("Traceability-System gestartet")

sck = Pin(18)
mosi = Pin(17)
miso = Pin(16)

spi = SPI( baudrate=2500000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

cs1 = Pin(15, Pin.OUT, value=1)
cs2 = Pin(38, Pin.OUT, value=1)
cs3 = Pin(39, Pin.OUT, value=1)
cs4 = Pin(40, Pin.OUT, value=1)
rst = Pin(42, Pin.OUT)
rst.value(1)  # Reset auf 1 = Reader ist wach

rdr1 = MFRC522(spi, cs1)
rdr2 = MFRC522(spi, cs2)
rdr3 = MFRC522(spi, cs3)
rdr4 = MFRC522(spi, cs4)

print("RFID gestartet, Bauteil läuft ein, warten auf Scan...")
reader = [("Station 1: Wareneingang", rdr1), ("Station 2: Laserstation", rdr2), ("Station 3: Schweißstation", rdr3), ("Station 4: Qualitätskontrolle", rdr4)]
#print("RFID gestartet, Karte auflegen und warten auf Scan...")

# Erster Test für ein Bauteil
#bauteil = {
#    "id": "BT-001",
#    "station": "Station 1",
#    "status": "i.O."
#}

#print("Bauteil-ID:", bauteil["id"])
#print("Station:", bauteil["station"])
#print("Qualitätsstatus:", bauteil["status"])


# Ein Reader erstellen 
#reader1 = MFRC522(sck=18, mosi=17, miso=16, rst=21, cs=15)

#print("1.Reader bereit!")

while True:
    for name, rdr in reader:
        t0 = time.ticks_ms()  # Startzeit für die Messung der Scan-Dauer

    
        # Reader prüfen - Station 1
        (stat, tag_type) = rdr.request(rdr.REQALL)        # Prüfen, ob eine Karte in der Nähe ist
        dt = time.ticks_diff(time.ticks_ms(), t0)  # Dauer des Scans berechnen
        if stat == rdr.OK:                                  # Wenn eine Karte gefunden wurde
            (stat, uid) = rdr.anticoll()                      # UID der Karte auslesen   
            if stat == rdr.OK:   
                print(2)                           # Wenn die UID erfolgreich ausgelesen wurde
                print(f"{name} - Bauteil erkannt! UID: {uid} (Scan-Dauer: {dt}ms)")
    # 500 Millisekunden warten, bevor der nächste Scan durchgeführt wird
    # Dies verhindert, dass der Reader zu schnell scannt und möglicherweise mehrere Scans desselben Bauteils durchführt 
    time.sleep_ms(500)