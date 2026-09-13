# ESP1 - RFID + SD + UART

from mfrc522 import MFRC522
from machine import SoftSPI, Pin, UART
import time
import sd_logger as sd_logger

print("Traceability-System ESP1 gestartet")

# ============================================================
# RFID
# ============================================================

sck = Pin(21)
mosi = Pin(17)
miso = Pin(16)

spi = SoftSPI(
    baudrate=2500000,
    polarity=0,
    phase=0,
    sck=sck,
    mosi=mosi,
    miso=miso
)

cs1 = Pin(15, Pin.OUT, value=1)
cs2 = Pin(38, Pin.OUT, value=1)
cs3 = Pin(18, Pin.OUT, value=1)
cs4 = Pin(47, Pin.OUT, value=1)

rdr1 = MFRC522(spi, cs1)
rdr2 = MFRC522(spi, cs2)
rdr3 = MFRC522(spi, cs3)
rdr4 = MFRC522(spi, cs4)

for rdr in (rdr1, rdr2, rdr3, rdr4):
    rdr.init()

reader = [
    ("Station 1: Wareneingang", rdr1),
    ("Station 2: Laserstation", rdr2),
    ("Station 3: Schweißstation", rdr3),
    ("Station 4: Qualitätskontrolle", rdr4)
]

# ============================================================
# UART
# ============================================================

uart = UART(
    1,
    baudrate=115200,
    tx=Pin(43),
    rx=Pin(44)
)

print("UART gestartet")
print("RFID gestartet")
print("Warte auf RFID- und QR-Daten...")

# ============================================================
# Hilfsfunktion
# ============================================================

def uid_to_id(uid):
    return ",".join(str(x) for x in uid)

# Merkt sich den zuletzt erkannten Tag pro Reader
last_uid = [None, None, None, None]

# ============================================================
# Hauptschleife
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # 1. UART prüfen
        # ----------------------------------------------------

        if uart.any():

            data = uart.readline()

            if data:

                try:
                    message = data.decode("utf-8").strip()
                except:
                    message = str(data)

                print("[UART] Empfangen:", message)

                if "QR:" in message:

                    qr_data = message.split("QR:", 1)[1]

                    print(
                        "[QR] QR-Code von ESP2:",
                        qr_data
                    )

                    sd_logger.log_qr_scan(
                        qr_data=qr_data
                    )

        # ----------------------------------------------------
        # 2. RFID prüfen
        # ----------------------------------------------------

        for index, (name, rdr) in enumerate(reader):

            t0 = time.ticks_ms()

            stat, tag_type = rdr.request(rdr.REQALL)

            dt = time.ticks_diff(
                time.ticks_ms(),
                t0
            )

            if stat == rdr.OK:

                stat, uid = rdr.anticoll()

                if stat == rdr.OK:

                    print(
                        f"{name} - Bauteil erkannt! "
                        f"Seriennummer: {uid} "
                        f"(Scan-Dauer: {dt}ms) "
                        f"(Status: i.O.)"
                    )

                    # Nur einmal senden, solange derselbe
                    # RFID-Tag auf dem Reader liegt
                    if uid != last_uid[index]:

                        last_uid[index] = uid

                        component_id = uid_to_id(uid)

                        station = index + 1
                        quality = 1
			status = 1

			quality_text = "i.O." if quality == 1 else "n.i.O."

			message = (
    				"ID:" + str(component_id) +
    				";STATION:" + str(station) +
    				";QUALITY:" + quality_text +
    				";STATUS:" + str(status) +
    				"\n"
			)

                        uart.write(message)

                        print(
                            "[UART] Gesendet:",
                            message.strip()
                        )

                    # RFID-Daten weiterhin auf SD speichern
                    sd_logger.log_rfid_scan(
                        tag_id=uid,
                        status="i.O.",
                        station=name
                    )

            else:

                # Kein Tag mehr vorhanden:
                # Beim nächsten Auftauchen wieder senden
                last_uid[index] = None

        time.sleep_ms(100)

except KeyboardInterrupt:

    print("Traceability-System ESP1 beendet")
