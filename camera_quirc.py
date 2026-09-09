from camera import Camera, PixelFormat, FrameSize
import quirc

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
print("Graustufenmodus aktiviert")

img = bytes(cam.capture())
cam.free_buffer()

print("Bildgroesse:", len(img), "Bytes")

# QR-Code dekodieren
try:
    result = quirc.decode(img, 640, 480)
    print("QR-Code erkannt:", result)
except Exception as e:
    print("Fehler beim Dekodieren des QR-Codes:", e)