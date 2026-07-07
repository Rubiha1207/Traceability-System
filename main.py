# main.py
# Testdatei für das Traceability-System
from mfrc522 import MFRC522
import utime

print("Traceability-System gestartet")

# Erster Test für ein Bauteil
bauteil = {
    "id": "BT-001",
    "station": "Station 1",
    "status": "i.O."
}

print("Bauteil-ID:", bauteil["id"])
print("Station:", bauteil["station"])
print("Qualitätsstatus:", bauteil["status"])


# Ein Reader erstellen 
reader1 = MFRC522(sck=18, mosi=17, miso=16, rst=21, cs=15)

print("1.Reader bereit!")

while True:

    # Reader 1 prüfen - Station 1
    stat, tag_type = reader1.request(reader1.REQIDL)        # Prüfen, ob eine Karte in der Nähe ist
    if stat == reader1.OK:                                  # Wenn eine Karte gefunden wurde
        stat, uid = reader1.anticoll()                      # UID der Karte auslesen   
        if stat == reader1.OK:                              # Wenn die UID erfolgreich ausgelesen wurde
            print("Station 1 - Karte erkannt! UID:", uid)   # Ausgabe der UID der erkannten Karte

    # 500 Millisekunden warten, bevor der nächste Scan durchgeführt wird
    # Dies verhindert, dass der Reader zu schnell scannt und möglicherweise mehrere Scans desselben Bauteils durchführt 
    utime.sleep_ms(500)