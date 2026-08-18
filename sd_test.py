from machine import SPI, Pin
import os
import sdcard

print("SD-Karten-Test gestartet")

# Pins des SD-Kartenmoduls
SD_SCK = 7
SD_MOSI = 6
SD_MISO = 5
SD_CS = 4

#SPI für SD-Karte
spi = SPI( baudrate=1000000, polarity=0, phase=0, sck=Pin(SD_SCK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO))

#SD-Karte initialisieren
sd = sdcard.SDCard(spi, Pin(SD_CS))

#SD-Karte in das Dateisystem einbinden
os.mount(sd, "/sd")

print("SD-Karte erfolgreich eingebunden!")

#Inhalt der SD-Karte anzeigen
print("Dateien auf der SD-Karte:")
print(os.listdir("/sd"))

# Testdatei schreiben
with open("/sd/test.txt", "w") as file:
    file.write("Hallo von unserem Traceability-System!\n")
print("test.txt wurde geschrieben.")

#Testdatei wieder lesen
with open("/sd/test.txt", "r") as file:
    inhalt = file.read()
print("Inhalt von test.txt:")
print(inhalt)

print("SD-Karten-Test erfolgreich!")