from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("192.168.188.160", port=502)

print("Verbinde mit ESP2...")

if client.connect():
    print("Verbindung erfolgreich")

    result = client.read_holding_registers(
        address=0,
        count=4
    )

    if result.isError():
        print("Modbus-Fehler:", result)
    else:
        print()
        print("Traceability-Daten:")
        print("Bauteil-ID:       ", result.registers[0])
        print("Aktuelle Station: ", result.registers[1])
        print("Qualität:          ", result.registers[2])
        print("Produktionsstatus: ", result.registers[3])

    client.close()
else:
    print("Verbindung fehlgeschlagen")
