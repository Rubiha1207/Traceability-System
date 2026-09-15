# Traceability-System – Schnellstartanleitung

Diese Anleitung beschreibt die Inbetriebnahme und Ausführung des Traceability-Systems für die Dual-ESP32-Architektur.

## Voraussetzung & Vorbereitung

1. Hardware-Verbindung: Beide ESP32-Boards jeweils mit einem USBC-Kabel an den Rechner anschließen.
2. Serielle Ports ermitteln: Prüfen, über welche Schnittstellen (COM-Ports unter Windows bzw. `/dev/tty*` unter macOS/Linux) die beiden ESP32 verbunden sind.
   - Windows: Gerätemanager öffnen, Anschlüsse (COM & LPT) prüfen (z. B. `COM3` und `COM7`).
   - macOS / Linux: Im Terminal `ls /dev/tty.*` oder `ls /dev/ttyUSB*` ausführen.

## Ausführung & Steuerung

Da zwei ESP32 parallel betrieben werden, benötigt man zwei separate Terminal-Fenster (eines pro ESP32).

1. In das Projektverzeichnis wechseln  
- In beiden Terminals das Projektverzeichnis öffnen:
cd /pfad/zum/Traceability-System

2. Verbindung herstellen  
- Terminal 1 und 2 (ESP1 & ESP2) seperat öffnen:  
".\\.venv\Scripts\python.exe -m mpremote connect COM<NR> repl" (NR ersetzen mit tatsächlichem Port, z.B: COM7 für ESP1 und COM3 für ESP2)

4. Programm bedienen & steuern  
Nachdem die Verbindung hergestellt wurde, befindet man sich in der MicroPython REPL-Umgebung.  
- Hauptprogramm (main.py) ausführen: exec(open("main.py").read())  
- Weitere Programme ausführen: exec(open("programmname.py").read())
