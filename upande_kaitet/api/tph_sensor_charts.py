import frappe
from frappe.utils import getdate
from datetime import datetime

@frappe.whitelist()
def get_sensor_chart_data(sensor_name=None, date_from=None, date_to=None, timespan=None, time_interval=None):
	if not sensor_name:
		return {"labels": [], "values": []}

	# SQL WHERE clause builder
	conditions = ["sensor_name = %s"]
	params = [sensor_name]

	if date_from:
		conditions.append("timestamp >= %s")
		params.append(date_from)

	if date_to:
		conditions.append("timestamp <= %s")
		params.append(date_to)

	where_clause = " AND ".join(conditions)

	# ---- HOURLY HANDLING ----
	if time_interval == "hourly":
		query = f"""
			SELECT
				HOUR(timestamp) as hour,
				AVG(value) as avg_value
			FROM `tabSensor Reading`
			WHERE {where_clause}
			GROUP BY hour
			ORDER BY hour
		"""
		data = frappe.db.sql(query, params, as_dict=True)

		# Prepare 24-hour timeline: 00:00 → 23:00
		all_hours = [f"{str(h).zfill(2)}:00" for h in range(24)]
		data_map = {f"{str(row['hour']).zfill(2)}:00": round(row["avg_value"], 2) for row in data}

		return {
			"labels": all_hours,
			"values": [data_map.get(h, 0) for h in all_hours]
		}

	# ---- QUARTERLY HANDLING ----
	elif time_interval == "quarterly":
		query = f"""
			SELECT
				CONCAT(YEAR(timestamp), '-Q', QUARTER(timestamp)) as label,
				AVG(value) as avg_value
			FROM `tabSensor Reading`
			WHERE {where_clause}
			GROUP BY YEAR(timestamp), QUARTER(timestamp)
			ORDER BY YEAR(timestamp), QUARTER(timestamp)
		"""
		data = frappe.db.sql(query, params, as_dict=True)

	# ---- OTHER INTERVALS ----
	else:
		time_format_map = {
			"daily": "%Y-%m-%d",
			"weekly": "%Y-%u",
			"monthly": "%Y-%m",
			"yearly": "%Y"
		}
		time_fmt = time_format_map.get(time_interval, "%Y-%m-%d")  # default: daily

		query = f"""
			SELECT
				DATE_FORMAT(timestamp, %s) as label,
				AVG(value) as avg_value
			FROM `tabSensor Reading`
			WHERE {where_clause}
			GROUP BY label
			ORDER BY label
		"""
		params = [time_fmt] + params
		data = frappe.db.sql(query, params, as_dict=True)

	# Fallback in case no data
	if not data:
		return {
			"labels": [],
			"values": []
		}

	return {
		"labels": [row['label'] for row in data],
		"values": [round(row['avg_value'], 2) for row in data]
	}
