from datetime import datetime, timedelta
import frappe
from frappe.utils import now_datetime


@frappe.whitelist()
def get_sensor_chart_data(sensor_name=None, date_from=None, date_to=None, timespan=None, time_interval=None):
	if not sensor_name:
		return {"labels": [], "values": []}

	# SQL WHERE clause builder
	conditions = ["sensor_name = %s"]
	params = [sensor_name]

	# Handle single-date filtering (e.g., from date picker only)
	if date_from and not date_to:
		try:
			start_dt = datetime.strptime(date_from, "%Y-%m-%d")
			end_dt = start_dt + timedelta(days=1)
			date_from = start_dt.strftime("%Y-%m-%d %H:%M:%S")
			date_to = end_dt.strftime("%Y-%m-%d %H:%M:%S")
		except:
			pass  # fallback silently

	# ---- Special Handling: Last 24 Hours with HOURLY grouping ----
	if time_interval == "hourly" and timespan == "last_24h":
		now = now_datetime()
		start_time = now - timedelta(hours=24)

		conditions.append("timestamp >= %s")
		params.append(start_time)

		where_clause = " AND ".join(conditions)

		query = f"""
			SELECT
				DATE_FORMAT(timestamp, '%%H:00') as hour_label,
				AVG(value) as avg_value
			FROM `tabSensor Reading`
			WHERE {where_clause}
			GROUP BY hour_label
			ORDER BY hour_label
		"""
		data = frappe.db.sql(query, params, as_dict=True)

		data_map = {row["hour_label"]: round(row["avg_value"], 2) for row in data}

		labels = []
		values = []
		for i in range(24):
			hour_time = (now - timedelta(hours=23 - i)).replace(minute=0, second=0, microsecond=0)
			label = hour_time.strftime("%H:00")
			labels.append(label)
			values.append(data_map.get(label, 0))

		return {"labels": labels, "values": values}

	# ---- General HOURLY handling for specific dates ----
	if time_interval == "hourly":
		if date_from:
			conditions.append("timestamp >= %s")
			params.append(date_from)
		if date_to:
			conditions.append("timestamp <= %s")
			params.append(date_to)

		where_clause = " AND ".join(conditions)

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

		all_hours = [f"{str(h).zfill(2)}:00" for h in range(24)]
		data_map = {f"{str(row['hour']).zfill(2)}:00": round(row["avg_value"], 2) for row in data}

		return {"labels": all_hours, "values": [data_map.get(h, 0) for h in all_hours]}

	# ---- QUARTERLY grouping ----
	elif time_interval == "quarterly":
		if date_from:
			conditions.append("timestamp >= %s")
			params.append(date_from)
		if date_to:
			conditions.append("timestamp <= %s")
			params.append(date_to)

		where_clause = " AND ".join(conditions)

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

	# ---- All Other Intervals (daily, weekly, monthly, yearly) ----
	else:
		if date_from:
			conditions.append("timestamp >= %s")
			params.append(date_from)
		if date_to:
			conditions.append("timestamp <= %s")
			params.append(date_to)

		where_clause = " AND ".join(conditions)

		time_format_map = {
			"daily": "%Y-%m-%d",
			"weekly": "%Y-%u",
			"monthly": "%Y-%m",
			"yearly": "%Y"
		}
		# default to daily
		time_fmt = time_format_map.get(time_interval, "%Y-%m-%d")  

		query = f"""
			SELECT
				DATE_FORMAT(timestamp, %s) as label,
				AVG(value) as avg_value
			FROM `tabSensor Reading`
			WHERE {where_clause}
			GROUP BY label
			ORDER BY label
		"""
		params = [time_fmt, *params]
		data = frappe.db.sql(query, params, as_dict=True)

	# ---- Final Output ----
	if not data:
		return {"labels": [], "values": []}

	return {
		"labels": [row["label"] for row in data],
		"values": [round(row["avg_value"], 2) for row in data]
	}
