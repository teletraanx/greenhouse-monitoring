import sqlite3
from flask import Flask, render_template_string

DB_PATH = "greenhouse.db"

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
	<meta charset="utf-8">
	<title>Greenhouse Dashboard</title>
	<meta http-equiv="refresh" content="10">
	<style>
		body { font-family: Arial, sans-serif; margin: 2rem; background: #f7f7f7; color: #222; }
		.card { background: white; padding: 1rem 1.25rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem; max-width: 600px; }
		h1, h2 { margin-top: 0; }
		table { border-collapse: collapse; width: 100%; background: white; border-radius: 12px; overflow: hidden; }
		th, td { padding: 0.75rem; border-bottom: 1px solid #ddd; text-align: left; }
		th { background: #eee; }
		.alert { color: #b00020; font-weight: bold; }
	</style>
</head>
<body>
	<h1>Greenhouse Dashboard</h1>

	{% if latest %}
	<div class="card">
		<h2>Latest Reading</h2>
		<p><strong>Node:</strong> {{ latest["node_id"] }}</p>
		<p><strong>Timestamp:</strong> {{ latest["ts"] }}</p>
		<p><strong>Temperature:</strong> {{ latest["temp_f"] }} F</p>
		<p><strong>Humidity:</strong> {{ latest["humidity"] }} %</p>
		<p><strong>RSSI:</strong> {{ latest["rssi"] }}</p>

		{% if latest["temp_f"] > 90 %}
		<p class="alert">Alert: Temperature is above 90F</p>
		{% elif latest["temp_f"] < 40 %}
		<p class="alert">Alert: Temperature is below 40F</p>
		{% else %}
		<p>No temperature alerts.</p>
		{% endif %}
	</div>
	{% else %}
	<div class="card">
		<p>No readings yet.</p>
	</div>
	{% endif %}

	<h2>Recent Readings</h2>
	<table>
		<tr>
			<th>Time</th>
			<th>Node</th>
			<th>Temp (F)</th>
			<th>Humidity (%)</th>
			<th>RSSI</th>
		</tr>
		{% for row in rows %}
		<tr>
			<td>{{ row["ts"] }}</td>
			<td>{{ row["node_id"] }}</td>
			<td>{{ row["temp_f"] }}</td>
			<td>{{ row["humidity"] }}</td>
			<td>{{ row["rssi"] }}</td>
		</tr>
		{% endfor %}
	</table>
</body>
</html>
"""

def get_db():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn

@app.route("/")
def dashboard():
	conn = get_db()
	latest = conn.execute("""
		SELECT ts, node_id, temp_f, humidity, rssi
		FROM readings
		ORDER BY id DESC
		LIMIT 1
	""").fetchone()

	rows = conn.execute("""
		SELECT ts, node_id, temp_f, humidity, rssi
		FROM readings
		ORDER BY id DESC
		LIMIT 20
	""").fetchall()
	conn.close()

	return render_template_string(HTML, latest=latest, rows=rows)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=False)
