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
		body { 
			font-family: Arial, sans-serif;
			margin: 2rem;
			background: #0f172a; /*blue grey*/
			color: #e5e7eb;
		}

		.card, .chart-card, table {
			background: #1e293b;
			border-radius: 12px;
			box-shadow: 0 2px 12px rgba(0,0,0,0.5);
		}
		
		.card, .chart-card {
			padding: 1rem 1.25rem;
			margin-bottom: 1rem;
			max-width: 600px;
		}

		h1, h2, h3 {
			margin-top: 0;
			color: #f1f5f9;
		}

		table {
			border-collapse: collapse;
			width: 100%;
			overflow: hidden;
		}

		th, td {
			padding: 0.75rem;
			border-bottom: 1px solid #334155;
			text-align: left;
		}

		th {
			background: #020617;
			color: #93c5fd;
		}

		tr:hover td {
			background: #334155;
		}

		.alert {
			color: #f87171;
			font-weight: bold;
		}

		.chart-column {
			width: 50%;
			min-width: 320px;
		}

		.chart-card canvas {
			width: 100% !important;
			height: 250px !important;
		}
	</style>
</head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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

	<h2>Charts</h2>

	<div class="chart-column">
		<div class="chart-card">
			<h3>Temperature (Last 50 Readings)</h3>
			<canvas id="tempChart"></canvas>
		</div>

		<div class="chart-card">
			<h3>Humidity (Last 50 Readings)</h3>
			<canvas id="humidityChart"></canvas>
		</div>
	</div>

	<script>
	const labels = {{ rows | map(attribute='ts') | list | tojson }};
	const temps = {{ rows | map(attribute='temp_f') | list | tojson }};
	const humidities = {{ rows | map(attribute='humidity') | list | tojson }};

	const reversedLabels = [...labels].reverse();
	const reversedTemps = [...temps].reverse();
	const reversedHumidities = [...humidities].reverse();

	const tempCtx = document.getElementById('tempChart').getContext('2d');

	new Chart(tempCtx, {
		type: 'line',
		data: {
			labels: reversedLabels,
			datasets: [{
				label: 'Temperature (F)',
				data: reversedTemps,
				borderColor: "#f97316", // orange
				backgroundColor: "#f97316",
				fill: false,
				tension: 0.3
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					labels: {
						color: "#e5e7eb"
					}
				}
			},
			scales: {
				x: {
					ticks: {
						maxTicksLimit: 6,
						color: "#94a3b8"
					},
					grid: {
						color: "#334155"
					}
				},
				y: {
					ticks: {
						color: "#94a3b8"
					},
					grid: {
						color: "#334155"
					}
				}
			}
		}
	});

	const humidityCtx = document.getElementById('humidityChart').getContext('2d');
	new Chart(humidityCtx, {
		type: 'line',
		data: {
			labels: reversedLabels,
			datasets: [{
				label: 'Humidity (%)',
				data: reversedHumidities,
				borderColor: "#22c55e", // green
				backgroundColor: "#22c55e",
				fill: false,
				tension: 0.3
			}]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					labels: {
						color: "#e5e7eb"
					}
				}
			},
			scales: {
				x: {
					ticks: {
						maxTicksLimit: 6,
						color: "#94a3b8"
					},
					grid: {
						color: "#334155"
					}
				},
				y: {
					ticks: {
						color: "#94a3b8"
					},
					grid: {
						color: "#334155"
					}
				}
			}
		}
	});
	</script>
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
		LIMIT 50
	""").fetchall()
	conn.close()

	return render_template_string(HTML, latest=latest, rows=rows)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=False)
