from PIL import Image

width = 640
height = 480

with open("test_gray.raw", "rb") as f:
    data = f.read()

print("Dateigröße:", len(data))

if len(data) != width * height:
    print("WARNUNG: Dateigröße passt nicht zu 640x480!")

img = Image.frombytes("L", (width, height), data)
img.save("test_gray.png")

print("PNG gespeichert: test_gray.png")