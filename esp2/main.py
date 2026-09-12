from camera import Camera, PixelFormat, FrameSize
from machine import UART, Pin
import quirc

print("Kamera-ESP gestartet")

uart = UART(
    1,
    baudrate=115200,
    tx=Pin(43),
    rx=Pin(44)
)

print("UART initialisiert")

cam = Camera(
    data_pins=[41, 45, 46, 42, 40, 38, 15, 18],
    pclk_pin=39,
    vsync_pin=1,
    href_pin=2,
    sda_pin=48,
    scl_pin=47,
    xclk_pin=3,
    xclk_freq=20_000_000,
    powerdown_pin=8,
    reset_pin=-1,
    pixel_format=PixelFormat.GRAYSCALE,
    frame_size=FrameSize.VGA
)

print("Kamera initialisiert")
print("QR-Code vor die Kamera halten")

img = bytes(cam.capture())
cam.free_buffer()

print("Bildgroesse:", len(img))

count = quirc.count(img, 640, 480)
print("QR-Kandidaten:", count)

result = quirc.decode(img, 640, 480)

if result is not None:
    print("QR erkannt:")
    print(result)

    try:
        qr_text = result.decode("utf-8")

        print("QR Inhalt:")
        print(qr_text)

        uart.write("QR:" + qr_text + "\n")
        print("QR über UART gesendet")

    except:
        pass
else:
    print("Kein QR-Code decodiert")