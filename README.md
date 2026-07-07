# Traceability-System

## Projektbeschreibung
Entwicklung eines digitalen Traceability-Systems zur lückenlosen Rückverfolgung von Bauteilen entlang einer Produktionskette. Ziel ist es, Produktionsschritte transparent darzustellen, Qualitätsdaten zu erfassen und den Weg jedes einzelnen Bauteils nachvollziehbar zu machen.

## Hauptfunktionen:
**Eindeutige Identifikation:** Generierung & Erfassung von Bauteil-IDs mittels QR-Code & RFID/NFC
**Prozessprotokollierung:** Speicherung der durchlaufenen Stationen im strukturierten JSON-Format
**Qualitätsüberwachung:** Simulation von Qualitätszuständen (i.O./n.i.O.) an den Stationen
**Industriekommunikation:** Bereitstellung & Übertragung der Historie via Modbus (TCP/IP) 

## Team
Rubiha Thiruchelvam 5018347
Lara Loebens        --
Salih Irmak         --

## Hardware
1x ESP32 Mikrocontroller: für Steuerungs- / Lese-Logik
4x RFID-RC522 Module: zur Verfolgung an den Stationen
1x ESP32-CAM Modul: zur kamerabasierten QR-Code-Erkennung
1x SD-Karten-Modul: zur lokalen Datenspeicherung

## Projektstruktur

traceability-system
|---- **code**
|       |--- mfrc522.py (RFID-Code)
|       |--- main.py (Hauptprogramm)
|       |--- **sd-karte**
|---- **dokumentation**
|       |--- verkabelung (Verkabelungspläne)
|       |--- flussdiagramm (Produktionsablauf)
|---- **README.md**

## Technologien
- *Programmiersprache:* MicroPython
- *Entwicklungsumgebung:* Visual Studio Code
- *Versionskontrolle:* GitHub
- *Projektmanagement:* Kanban 
- *Datenspeicherung:* JSON Format 

## Installation
...

## Nutzung
...