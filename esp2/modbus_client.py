import socket
import struct
from machine import UART, Pin

HOST = "0.0.0.0"
PORT = 502

# UART von ESP1

uart = UART(
    1,
    baudrate=115200,
    tx=Pin(43),
    rx=Pin(44)
)

print("UART gestartet")


# Traceability-Daten

REGISTER_0 = 0      # Bauteil-ID
REGISTER_1 = 0      # aktuelle Station
REGISTER_2 = 0      # QualitÃ¤t
REGISTER_3 = 0      # Produktionsstatus


# UART-Daten verarbeiten

def process_uart():

    global REGISTER_0
    global REGISTER_1
    global REGISTER_2
    global REGISTER_3

    if uart.any():

        data = uart.readline()

        if data:

            try:
                message = data.decode("utf-8").strip()
            except:
                return

            print("[UART] Empfangen:", message)

            if message.startswith("ID:"):

                try:

                    parts = message.split(";")

                    REGISTER_0 = int(
                        parts[0].split(":")[1]
                    )

                    REGISTER_1 = int(
                        parts[1].split(":")[1]
                    )

                    REGISTER_2 = int(
                        parts[2].split(":")[1]
                    )

                    REGISTER_3 = int(
                        parts[3].split(":")[1]
                    )

                    print("Modbus-Daten aktualisiert:")
                    print("Bauteil-ID:", REGISTER_0)
                    print("Station:", REGISTER_1)
                    print("QualitÃ¤t:", REGISTER_2)
                    print("Status:", REGISTER_3)

                except Exception as e:

                    print(
                        "Fehler beim Verarbeiten:",
                        e
                    )


# Modbus Register

def read_register(address):

    if address == 0:
        return REGISTER_0

    elif address == 1:
        return REGISTER_1

    elif address == 2:
        return REGISTER_2

    elif address == 3:
        return REGISTER_3

    else:
        return 0


# Modbus TCP Server

server = socket.socket()

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(
    (HOST, PORT)
)

server.listen(1)

print("Modbus-TCP-Server gestartet")
print("Port:", PORT)


# Hauptschleife

while True:

    process_uart()

    server.settimeout(0.1)

    try:

        client, addr = server.accept()

    except:

        continue

    print("Verbindung von:", addr)

    try:

        client.settimeout(1)

        while True:

            process_uart()

            request = client.recv(12)

            if not request:
                break

            transaction_id = request[0:2]

            unit_id = request[6]

            function_code = request[7]

            if function_code == 3:

                start_address = struct.unpack(
                    ">H",
                    request[8:10]
                )[0]

                quantity = struct.unpack(
                    ">H",
                    request[10:12]
                )[0]

                if quantity <= 4:

                    response_data = b""

                    for i in range(quantity):

                        value = read_register(
                            start_address + i
                        )

                        response_data += struct.pack(
                            ">H",
                            value
                        )

                    response_pdu = bytes([
                        3,
                        len(response_data)
                    ]) + response_data

                    length = len(response_pdu) + 1

                    response = (
                        transaction_id +
                        b"\x00\x00" +
                        struct.pack(">H", length) +
                        bytes([unit_id]) +
                        response_pdu
                    )

                    client.send(response)

            else:

                print(
                    "Nicht unterstÃ¼tzter Function Code:",
                    function_code
                )

    except Exception as e:

        print("Fehler:", e)

    finally:

        client.close()

        print("Verbindung geschlossen")
