import re
import sqlite3
import serial
from datetime import datetime

SERIAL_PORT = "/dev/ttyUSB0" # change port here if needed
BAUD_RATE = 115200
DB_PATH = "greenhouse.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS readings (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ts TEXT NOT NULL,
	node_id TEXT NOT NULL,
	temp_f REAL NOT NULL,
	humidity REAL NOT NULL,
	rssi INTEGER
)
""")
conn.commit()

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

pattern = re.compile(
	r"Receiving from (GH\d+):\s*(GH\d+),([0-9.]+),([0-9.]+)\s*\|\s*RSSI:\s*(-?\d+)"
)

print("Listening for greenhouse packets...")

while True: 
	line = ser.readline().decode("utf-8", errors="ignore").strip()
	if not line:
		continue

	print(line)

	match = pattern.search(line)
	if not match:
		continue

	recv_node = match.group(1)
	packet_node = match.group(2)
	temp_f = float(match.group(3))
	humidity = float(match.group(4))
	rssi = int(match.group(5))

	ts = datetime.now().isoformat(timespec="seconds")

	cur.execute("""
		INSERT INTO readings (ts, node_id, temp_f, humidity, rssi)
		VALUES (?, ?, ?, ?, ?)
	""", (ts, packet_node, temp_f, humidity, rssi))
	conn.commit()

	print(f"Stored -> {ts} | {packet_node} | Temp {temp_f} F | Humidity {humidity}% | RSSI {rssi}")

