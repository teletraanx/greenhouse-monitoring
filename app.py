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
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta http-equiv="refresh" content="30">
	<style>
		:root {
			--bg: #0f172a;
			--panel: #1e293b;
			--panel-2: #111827;
			--text: #e5e7eb;
			--muted: #94a3b8;
			--border: #334155;
			--accent-blue: #93c5fd;
			--temp: #f97316;
			--humidity: #22c55e;
			--alert: #f87171;
			--ok: #86efac;
		}

		* {
			box-sizing: border-box;
		}

		body { 
			font-family: Arial, sans-serif;
			margin: 0;
			background: var(--bg);
			color: var(--text);
		}

		.page {
			width: 100%;
			max-width: 1200px;
			margin: 0 auto;
			padding: 1rem;
		}

		h1, h2, h3 {
			margin-top: 0;
			color: #f8fafc;
		}

		h1 {
			font-size: 1.9rem;
			margin-bottom: 1rem;
		}

		h2 {
			font-size: 1.2rem;
			margin-bottom: 0.75rem;
		}

		h3 {
			font-size: 1rem;
			margin-bottom: 0.75rem;
		}

		.card,
		.chart-card,
		.table-card {
			background: var(--panel);
			border-radius: 14px;
			box-shadow: 0 2px 12px rgba(255,255,255,0.03);
		}

		.card,
		.chart-card,
		.table-card {
			padding: 1rem 1.1rem;
		}

		.top-grid {
			display: grid;
			grid-template-columns: 1fr;
			gap: 1rem;
			margin-bottom: 1rem;
		}

		.stats-grid {
			display: grid;
			grid-template-columns: 1fr;
			gap: 0.5rem;
			margin-top: 0.75rem;
		}

		.stat-row {
			display: flex;
			justify-content: space-between;
			gap: 1rem;
			padding: 0.55rem 0;
			border-bottom: 1px solid var(--border);
		}

		.stat-row:last-child {
			border-bottom: none;
		}

		.label {
			color: var(--muted);
		}

		.value {
			font-weight: bold;
			text-align: right;
		}

		.alert {
			color: var(--alert);
			font-weight: bold;
			margin-top: 0.75rem;
		}

		.ok {
			color: var(--ok);
			font-weight: bold;
			margin-top: 0.75rem;
		}

		.charts-section {
			margin-bottom: 1rem;
		}

		.chart-grid {
			display: grid;
			grid-template-columns: 1fr;
			gap: 1rem;
			align-items: start;
		}

		.chart-card {
			width: 100%;
		}

		.chart-wrap {
			position: relative;
			width: 100%;
			height: 260px;
		}

		.table-card {
			overflow: hidden;
		}

		.table-scroll {
			overflow-x: auto;
			-webkit-overflow-scrolling: touch;
		}

		table {
			border-collapse: collapse;
			width: 100%;
			min-width: 560px;
			color: var(--text);
		}

		th, td {
			padding: 0.75rem;
			border-bottom: 1px solid var(--border);
			text-align: left;
			white-space: nowrap;
		}

		th {
			background: var(--panel-2);
			color: var(--accent-blue);
			position: sticky;
			top: 0;
		}

		tr:hover td {
			background: rgba(255,255,255,0.03);
		}

		.muted {
			color: var(--muted);
		}

		@media (min-width: 700px) {
			.page {
				padding: 1.5rem;
			}

			.top-grid {
				grid-template-columns: minmax(320px, 520px);
			}

			.chart-grid {
				grid-template-columns: minmax(320px, 650px);
			}
		}

		@media (min-width: 1024px) {
			.page {
				padding: 2rem;
			}

			.top-grid {
				grid-template-columns: minmax(340px, 480px);
			}

			.chart-grid {
				grid-template-columns: minmax(340px, 700px);
			}

			.chart-wrap {
				height: 300px;
			}
		}
	</style>
</head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<body>
	<div class="page">
		<h1>Greenhouse Dashboard</h1>
		
		<div class="top-grid">
		{% if latest %}
		<div class="card">
			<h2>Latest Reading</h2>

			<div class="stats-grid">
				<div class="stat-row">
					<span class="label">Node</span>
					<span class="value">{{ latest["node_id"] }}</span>
				</div>
				<div class="stat-row">
					<span class="label">Timestamp</span>
					<span class="value">{{ latest["ts"] }}</span>
				</div>
				<div class="stat-row">
					<span class="label">Temperature</span>
					<span class="value">{{ latest["temp_f"] }} F</span>
				</div>
				<div class="stat-row">
					<span class="label">Humidity</span>
					<span class="value">{{ latest["humidity"] }} %</span>
				</div>
				<div class="stat-row">
					<span class="label">RSSI</span>
					<span class="value">{{ latest["rssi"] }}</span>
				</div>
			</div>

			{% if latest["temp_f"] > 90 %}
			<p class="alert">Alert: Temperature is above 90F</p>
			{% elif latest["temp_f"] < 40 %}
			<p class="alert">Alert: Temperature is below 40F</p>
			{% else %}
			<p class="ok">No temperature alerts.</p>
			{% endif %}
		</div>
		{% else %}
		<div class="card">
			<p>No readings yet.</p>
		</div>
		{% endif %}
	</div>

	<div class="charts-section">
		<h2>Charts</h2>

		<div class="chart-grid">
			<div class="chart-card">
				<h3>Temperature (Last 24 Hours)</h3>
				<div class="chart-wrap">
					<canvas id="tempChart"></canvas>
				</div>
			</div>

			<div class="chart-card">
				<h3>Humidity (Last 24 Hours)</h3>
				<div class="chart-wrap">
					<canvas id="humidityChart"></canvas>
				</div>
			</div>
		</div>
	</div>

	<script>
	const labels = {{ rows | map(attribute='ts') | list | tojson }};
	const temps = {{ rows | map(attribute='temp_f') | list | tojson }};
	const humidities = {{ rows | map(attribute='humidity') | list | tojson }};

	const sharedOptions = {
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
	};

	const tempCtx = document.getElementById('tempChart').getContext('2d');

	new Chart(tempCtx, {
		type: 'line',
		data: {
			labels: labels,
			datasets: [{
				label: 'Temperature (F)',
				data: temps,
				borderColor: "#f97316", // orange
				backgroundColor: "#f97316",
				fill: false,
				tension: 0.3
			}]
		},
		options: sharedOptions
	});

	const humidityCtx = document.getElementById('humidityChart').getContext('2d');
	new Chart(humidityCtx, {
		type: 'line',
		data: {
			labels: labels,
			datasets: [{
				label: 'Humidity (%)',
				data: humidities,
				borderColor: "#22c55e", // green
				backgroundColor: "#22c55e",
				fill: false,
				tension: 0.3
			}]
		},
		options: sharedOptions
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
		WITH latest_time AS (
			SELECT MAX(ts) AS max_ts FROM readings
		)
		SELECT
			strftime('%m-%d %H:00', r.ts) AS ts,
			ROUND(AVG(r.temp_f), 1) AS temp_f,
			ROUND(AVG(r.humidity), 1) AS humidity
		FROM readings r, latest_time
		WHERE r.ts >= datetime(latest_time.max_ts, '-24 hours')
		GROUP BY strftime('%Y-%m-%d %H:00:00', r.ts)
		ORDER BY MIN(r.ts) ASC
	""").fetchall()
	conn.close()

	return render_template_string(HTML, latest=latest, rows=rows)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=False)
