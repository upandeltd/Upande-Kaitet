from datetime import datetime, timedelta
import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def get_sensor_chart_data(sensor_name=None, date_from=None, date_to=None, timespan=None, time_interval=None):
	if not sensor_name:
		return {"labels": [], "values": []}

	def format_label(label, interval):
		try:
			if interval == "hourly":
				dt = datetime.strptime(label, "%Y-%m-%d %H:00")
				return dt.strftime("%H:%M")
			elif interval == "daily":
				dt = datetime.strptime(label, "%Y-%m-%d")
				return dt.strftime("%d-%m-%Y")
			elif interval == "weekly":
				year, week = label.split("-")
				return f"Week {week}, {year}"
			elif interval == "monthly":
				dt = datetime.strptime(label, "%Y-%m")
				return dt.strftime("%b %Y")
			elif interval == "yearly":
				return label
			elif interval == "quarterly":
				return label.replace("-", " Q")
			else:
				return label
		except:
			return label

	# Build WHERE conditions
	conditions = ["sensor_name = %s"]
	params = [sensor_name]

	# Handle single-date input (e.g. from date picker)
	if date_from and not date_to:
		try:
			start_dt = datetime.strptime(date_from, "%Y-%m-%d")
			end_dt = start_dt + timedelta(days=1)
			date_from = start_dt.strftime("%Y-%m-%d %H:%M:%S")
			date_to = end_dt.strftime("%Y-%m-%d %H:%M:%S")
		except:
			pass

	# Default to timespan if no explicit date range provided
	now = now_datetime()
	if not date_from:
		if timespan == "last_year":
			start_dt = now - timedelta(days=365)
		elif timespan == "last_quarter":
			start_dt = now - timedelta(days=90)
		elif timespan == "last_month":
			start_dt = now - timedelta(days=30)
		elif timespan == "last_week":
			start_dt = now - timedelta(days=7)
		else:
			start_dt = now - timedelta(hours=24)
		date_from = start_dt.strftime("%Y-%m-%d %H:%M:%S")
	if not date_to:
		date_to = now.strftime("%Y-%m-%d %H:%M:%S")

	# Final WHERE clause
	conditions.append("timestamp >= %s")
	conditions.append("timestamp <= %s")
	params.extend([date_from, date_to])
	where_clause = " AND ".join(conditions)

	# Format mapping
	format_map = {
		"hourly": "%Y-%m-%d %H:00",
		"daily": "%Y-%m-%d",
		"weekly": "%Y-%U",
		"monthly": "%Y-%m",
		"yearly": "%Y"
	}

	# Default interval
	if not time_interval:
		time_interval = "daily"

	# Handle quarterly interval
	if time_interval == "quarterly":
		query = f"""
			SELECT
				CONCAT(YEAR(timestamp), '-Q', QUARTER(timestamp)) as label,
				AVG(value) as avg_value
			FROM `tabSensor Reading`
			WHERE {where_clause}
			GROUP BY label
			ORDER BY label
		"""
		data = frappe.db.sql(query, params, as_dict=True)
		data_map = {row["label"]: round(row["avg_value"], 2) for row in data}

		start_dt = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
		end_dt = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
		labels = []
		cursor = start_dt

		while cursor <= end_dt:
			q = (cursor.month - 1) // 3 + 1
			label = f"{cursor.year}-Q{q}"
			if label not in labels:
				labels.append(label)
			month = cursor.month + 3
			year = cursor.year + (month - 1) // 12
			month = (month - 1) % 12 + 1
			cursor = cursor.replace(year=year, month=month, day=1)

		values = [data_map.get(label, None) for label in labels]
		formatted_labels = [format_label(l, "quarterly") for l in labels]

		return {
			"labels": formatted_labels,
			"values": values,
			"label_format": "quarterly"
		}

	# For all other intervals
	sql_format = format_map.get(time_interval, "%Y-%m-%d")

	query = f"""
		SELECT
			DATE_FORMAT(timestamp, %s) as label,
			AVG(value) as avg_value
		FROM `tabSensor Reading`
		WHERE {where_clause}
		GROUP BY label
		ORDER BY label
	"""
	data = frappe.db.sql(query, [sql_format] + params, as_dict=True)
	data_map = {row["label"]: round(row["avg_value"], 2) for row in data}

	start_dt = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
	end_dt = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
	labels = []
	cursor = start_dt

	while cursor <= end_dt:
		if time_interval == "hourly":
			labels.append(cursor.strftime("%Y-%m-%d %H:00"))
			cursor += timedelta(hours=1)
		elif time_interval == "daily":
			labels.append(cursor.strftime("%Y-%m-%d"))
			cursor += timedelta(days=1)
		elif time_interval == "weekly":
			labels.append(cursor.strftime("%Y-%U"))
			cursor += timedelta(days=7)
		elif time_interval == "monthly":
			labels.append(cursor.strftime("%Y-%m"))
			month = cursor.month + 1
			year = cursor.year + (month - 1) // 12
			month = (month - 1) % 12 + 1
			cursor = cursor.replace(year=year, month=month, day=1)
		elif time_interval == "yearly":
			labels.append(cursor.strftime("%Y"))
			cursor = cursor.replace(year=cursor.year + 1)
		else:
			break

	values = [data_map.get(label, None) for label in labels]
	formatted_labels = [format_label(l, time_interval) for l in labels]

	# Set label format flag for front-end tooltip behavior
	label_format = (
		"time_only" if time_interval == "hourly" and (date_from or timespan == "last_24h") else time_interval
	)

	return {
		"labels": formatted_labels,
		"values": values,
		"label_format": label_format
	}

@frappe.whitelist()
def get_all_sensor_names():
    sensor_names = frappe.db.sql("""
        SELECT DISTINCT sensor_name
        FROM `tabSensor Reading`
        WHERE sensor_name IS NOT NULL AND sensor_name != ''
        ORDER BY sensor_name
    """, as_list=True)
    return [row[0] for row in sensor_names]
