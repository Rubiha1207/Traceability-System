import socket
import struct

HOST = "0.0.0.0"
PORT = 502
REGISTER_0 = 1234

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print("Modbus-TCP-Server gestartet")
print("Port:", PORT)

while True:
    client, addr = server.accept()
    print("Verbindung von:", addr)

    try:
        while True:
            request = client.recv(12)

            if not request:
                break

            transaction_id = request[0:2]
            unit_id = request[6]
            function_code = request[7]

            if function_code == 3:
                start_address = struct.unpack(">H", request[8:10])[0]
                quantity = struct.unpack(">H", request[10:12])[0]

                if start_address == 0 and quantity == 1:
                    response_pdu = bytes([
                        3,
                        2
                    ]) + struct.pack(">H", REGISTER_0)

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
                print("Nicht unterstützter Function Code:", function_code)

    except Exception as e:
        print("Fehler:", e)

    finally:
        client.close()
        print("Verbindung geschlossen")
