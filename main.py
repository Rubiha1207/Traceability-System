# main.py
# Testdatei für das Traceability-System

print("Traceability-System gestartet")

# Erster Test für ein Bauteil
bauteil = {
    "id": "BT-001",
    "station": "Station 1",
    "status": "i.O."
}

print("Bauteil-ID:", bauteil["id"])
print("Station:", bauteil["station"])
print("Qualitätsstatus:", bauteil["status"])