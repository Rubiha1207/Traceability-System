print("TESTDATEI WIRD GELADEN")
import sys
import types

# Fake-Modul "machine" für Tests unter Windows
machine = types.ModuleType("machine")

class Pin:
    OUT = 0
    IN = 1

    def __init__(self, *args, **kwargs):
        pass

class SPI:
    def __init__(self, *args, **kwargs):
        pass

machine.Pin = Pin
machine.SPI = SPI

sys.modules["machine"] = machine

import pytest
from mfrc522 import MFRC522

# Objekt ohne Hardware erstellen
def create_reader():
    reader = MFRC522.__new__(MFRC522)
    reader.OK = 0
    reader.ERR = 2
    reader.NOTAGERR = 1
    reader.REQIDL = 0x26
    return reader


# -------------------------
# TEST 1: berechnet CRC-Prüfcode
# -------------------------
def test_crc_returns_two_bytes():
    reader = create_reader()

    reader._wreg = lambda *args: None   # Schreibzugriff ignorieren
    reader._rreg = lambda *args: 0      # immer 0 zurückgeben

    result = reader._crc([0x01, 0x02, 0x03])

    assert isinstance(result, list)     # Ergebnis ist eine Liste
    assert len(result) == 2             # Ergebnis besteht aus 2 Bytes (High Byte & Low Byte)


# -------------------------
# TEST 2: _sflags (Bits setzen/einschalten)
# -------------------------
# Intern passiert 00000001 OR 00000010 = 00000011
def test_sflags_sets_bits():
    reader = create_reader()

    reader._rreg = lambda reg: 0b00000001
    written = {}

    reader._wreg = lambda reg, val: written.update({reg: val})

    reader._sflags(0x10, 0b00000010)

    assert written[0x10] == 0b00000011


# -------------------------
# TEST 3: _cflags (Bits löschen/ausschalten)
# -------------------------
def test_cflags_clears_bits():
    reader = create_reader()

    reader._rreg = lambda reg: 0b00000111   # im Register steht 00000111
    written = {}

    reader._wreg = lambda reg, val: written.update({reg: val})

    reader._cflags(0x10, 0b00000101)        # gelöscht werden sollen die Bits 00000101

    assert written[0x10] == 0b00000010      # im Register steht nachher 00000010


# -------------------------
# TEST 4: request erfolgreich(wird getestet, ob Karte in der Nähe ist)
# -------------------------
def test_request_success():
    reader = create_reader()

    reader._wreg = lambda *args: None
    reader._tocard = lambda cmd, data: (reader.OK, [], 0x10)    # setzen Status auf OK & Bits auf 0x10

    stat, bits = reader.request(reader.REQIDL)

    assert stat == reader.OK
    assert bits == 0x10
# -------------------------
# TEST 5: request Fehler (Karte nicht in der Nähe)
# -------------------------
def test_request_fail():
    reader = create_reader()

    reader._wreg = lambda *args: None
    reader._tocard = lambda cmd, data: (reader.ERR, [], 0)   # setzen Status auf ERR & Bits auf 0
    
    stat, bits = reader.request(reader.REQIDL)

    assert stat == reader.ERR


# -------------------------
# TEST 6: anticoll gültig (Auslesen der UID einer Karte)
# -------------------------
# im Originalcode wird gerechnet:
#  1 XOR 2 = 3; 3 XOR 3 = 0; 0 XOR 4 = 4
# Also Prüfbyte = 4, deshalb letzte Zahl in der UID = 4
def test_anticoll_valid():
    reader = create_reader()

    uid = [0x01, 0x02, 0x03, 0x04, 0x04]
    reader._wreg = lambda *args: None
    reader._tocard = lambda *args: (reader.OK, uid, 0)
    
    stat, result = reader.anticoll()

    assert stat == reader.OK
    assert result == uid


# -------------------------
# TEST 7: anticoll Fehler (testet, ob Funktion bei falscher Länge, mit Fehler abbricht)
# -------------------------
# eine UID muss 5 Bytes lang sein, sonst Fehler
def test_anticoll_wrong_length():
    reader = create_reader()

    reader._wreg = lambda *args: None
    reader._tocard = lambda *args: (reader.OK, [1, 2, 3], 0)

    stat, result = reader.anticoll()

    assert stat == reader.ERR