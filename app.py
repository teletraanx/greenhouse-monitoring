import sqlite3
from flask import Flask, render_template_string

DB_PATH = "greenhouse.db"

app = Flask(__name__)

def classify_temp_alert(temp_f):
	if temp_f is None:
		return None

	if temp_f < 32:
		return {
			"severity": "critical",
			"label": "Critical",
			"message": f"Critical low temperature: {temp_f:.1f} F"
		}
	if temp_f > 100:
		return {
			"severity": "critical",
			"label": "Critical",
			"message": f"Critical high temperature: {temp_f:.1f} F"
		}
	if temp_f < 45:
		return {
			"severity": "warning",
			"label": "Warning",
			"message": f"Warning low temperature: {temp_f:.1f} F"
		}
	if temp_f > 95:
		return {
			"severity": "warning",
			"label": "Warning",
			"message": f"Warning high temperature: {temp_f:.1f} F"
		}

	return {
		"severity": "ok",
		"label": "Normal",
		"message": f"Temperature normal: {temp_f:.1f} F"
	}

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
			--critical: #fb7185;
			--critical-soft: rgba(251,113,133,0.14);
			--warning: #fbbf24;
			--warning-soft: rgba(251,191,36,0.12);
			--ok: #4ade80;
			--ok-soft: rgba(74,222,128,0.10);
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
		.chart-card {
			background: var(--panel);
			border-radius: 14px;
			box-shadow: 0 2px 12px rgba(255,255,255,0.03);
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

		.status-banner {
			margin-top: 0.9rem;
			padding: 0.85rem 1rem;
			border-radius: 12px;
			font-weight: bold;
			border: 1px solid transparent;
		}

		.status-banner.ok {
			color: var(--ok);
			background: rgba(74,222,128,0.08);
			border-color: rgba(74,222,128,0.18);
		}

		.status-banner.warning {
			color: var(--warning);
			background: rgba(251,191,36,0.08);
			border-color: rgba(251,191,36,0.18);
		}

		.status-banner.critical {
			color: var(--critical);
			background: rgba(251,113,133,0.08);
			border-color: rgba(251,113,133,0.18);
		}

		.alert-log-list {
			display: flex;
			flex-direction: column;
			gap: 0.75rem;
			margin-top: 0.75rem;
		}

		.alert-item {
			border: 1px solid var(--border);
			border-radius: 12px;
			padding: 0.85rem 0.9rem;
			background: rgba(255,255,255,0.02);
		}

		.alert-item.warning {
			border-color: rgba(251,191,36,0.25);
			background: rgba(215,191,36,0.06);
		}

		.alert-item.critical {
			border-color: rgba(251,113,133,0.25);
			background: rgba(251,113,133,0.06);
		}

		.alert-topline {
			display: flex;
			justify-content: space-between;
			align-items: center;
			gap: 0.75rem;
			margin-bottom: 0.35rem;
			flex-wrap: wrap;
		}

		.severity-pill {
			display: inline-block;
			padding: 0.2rem 0.55rem;
			border-radius: 999px;
			font-size: 0.82rem;
			font-weight: bold;
		}

		.severity-pill.warning {
			color: #111827;
			background: var(--warning);
		}

		.severity-pill.critical {
			color: white;
			background: var(--critical);
		}

		.alert-meta {
			color: var(--muted)
			font-size: 0.92rem;
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

		.muted {
			color: var(--muted);
		}

		@media (min-width: 700px) {
			.page {
				padding: 1.5rem;
			}

			.top-grid {
				grid-template-columns: minmax(320px, 520px) minmax(320px, 1fr);
				align-items: start;
			}

			.chart-grid {
				grid-template-columns: minmax(320px, 700px);
			}
		}

		@media (min-width: 1024px) {
			.page {
				padding: 2rem;
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

			{% if latest_alert %}
				<div class="status-banner {{ latest_alert['severity'] }}">
					{{ latest_alert['label'] }}: {{ latest_alert['message'] }}
				</div>
			{% endif %}
		</div>
		{% else %}
		<div class="card">
			<p>No readings yet.</p>
		</div>
		{% endif %}

		<div class="card">
			<h2>Alert Log</h2>
			{% if alerts %}
			<div class="alert-log-list">
				{% for alert in alerts %}
				<div class="alert-item {{ alert['severity'] }}">
					<div class="alert-topline">
						<span class="severity-pill {{ alert['severity'] }}">{{ alert['label'] }}</span>
						<span class="alert-meta">{{ alert['ts'] }}</span>
					</div>
					<div><strong>{{ alert['node_id'] }}</strong></div>
					<div>{{ alert['message'] }}</div>
				</div>
				{% endfor %}
			</div>
			{% else %}
			<p class="muted">No recent alerts.</p>
			{% endif %}
		</div>
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

	const tempZonesPlugin = {
		id: 'tempZones',
		beforeDatasetsDraw(chart, args, pluginOptions) {
			if (!pluginOptions || !pluginOptions.enabled) return;

			const { ctx, chartArea, scales } = chart;
			const y = scales.y;
			if (!chartArea || !y) return;

			const zones = pluginOptions.zones || [];

			ctx.save();

			zones.forEach(zone => {
				const topVal = Math.min(zone.max, y.max);
				const bottomVal = Math.max(zone.min, y.min);

				if (topVal <= bottomVal) return;

				const yTop = y.getPixelForValue(topVal);
				const yBottom = y.getPixelForValue(bottomVal);

				ctx.fillStyle = zone.color;
				ctx.fillRect(
					chartArea.left,
					yTop,
					chartArea.right - chartArea.left,
					yBottom - yTop
				);
			});

			ctx.restore();
		}
	};

	Chart.register(tempZonesPlugin);

	const baseOptions = {
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
			}
		}
	};

	const tempOptions = {
		...baseOptions,
		plugins: {
			...baseOptions.plugins,
			tempZones: {
				enabled: true,
				zones: [
					{ min: 30, max: 32, color: 'rgba(251,113,133,0.16)' },
					{ min: 32, max: 45, color: 'rgba(251,191,36,0.12)' },
					{ min: 45, max: 95, color: 'rgba(74,222,128,0.10)' },
					{ min: 95, max: 100, color: 'rgba(251,191,36,0.12)' },
					{ min: 100, max: 120, color: 'rgba(251,113,133,0.16)' }
				]
			}
		},
		scales: {
			...baseOptions.scales,
			y: {
				min: 30,
				max: 120,
				ticks: {
					color: "#94a3b8",
					stepSize: 10
				},
				grid: {
					color: "#334155"
				}
			}
		}
	};

	const humidityOptions = {
		...baseOptions,
		scales: {
			...baseOptions.scales,
			y: {
				min: 0,
				max: 100,
				ticks: {
					color: "#94a3b8",
					stepSize: 10
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
				tension: 0.3,
				pointRadius: 3,
				pointHoverRadius: 4
			}]
		},
		options: tempOptions
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
				tension: 0.3,
				pointRadius: 3,
				pointHoverRadius: 4
			}]
		},
		options: humidityOptions
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

	alert_rows = conn.execute("""
		SELECT ts, node_id, temp_f
		FROM readings
		WHERE temp_f < 45 OR temp_f > 95
		ORDER BY id DESC
		LIMIT 12
	""").fetchall()

	conn.close()

	latest_alert = classify_temp_alert(latest["temp_f"]) if latest else None

	alerts = []
	for row in alert_rows:
		alert = classify_temp_alert(row["temp_f"])
		if alert and alert["severity"] in ("warning", "critical"):
			alerts.append({
				"ts": row["ts"],
				"node_id": row["node_id"],
				"temp_f": row["temp_f"],
				"severity": alert["severity"],
				"label": alert["label"],
				"message": alert["message"]
			})

	return render_template_string(HTML, latest=latest, rows=rows, latest_alert=latest_alert, alerts=alerts)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=False)
