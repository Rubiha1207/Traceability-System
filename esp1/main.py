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

# Vier RFID-Reader
# GPIO43 und GPIO44 werden für UART verwendet und daher
# NICHT mehr für RFID-CS verwendet.

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

                # QR-Nachricht
                if "QR:" in message:
                    qr_data = message.split("QR:", 1)[1]
                    print("[QR] QR-Code von ESP2:", qr_data)
                    sd_logger.log_qr_scan(qr_data=qr_data)


        # ----------------------------------------------------
        # 2. RFID prüfen
        # ----------------------------------------------------

        for name, rdr in reader:

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

                    sd_logger.log_rfid_scan(
                        tag_id=uid,
                        status="i.O.",
                        station=name
                    )


        # kurze Pause
        time.sleep_ms(100)


except KeyboardInterrupt:

    print("Traceability-System ESP1 beendet")