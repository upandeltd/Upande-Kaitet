from datetime import datetime, timedelta
import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def get_all_sensor_names():
	sensor_names = frappe.db.sql("""
		SELECT DISTINCT sensor_name
		FROM `tabSensor Reading`
		WHERE sensor_name IS NOT NULL AND sensor_name != ''
		ORDER BY sensor_name
	""", as_list=True)
	return [row[0] for row in sensor_names]

@frappe.whitelist()
def get_sensor_chart_data(sensor_name=None, date_from=None, date_to=None, timespan=None, time_interval=None):
	if not sensor_name:
		return {"labels": [], "values": [], "unit": ""}

	def format_label(label, interval):
		try:
			if interval == "hourly":
				dt = datetime.strptime(label, "%Y-%m-%d %H:00")
				if timespan == "last_week":
					return dt.strftime("%d %b %H:%M")
				else:
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

	sum_sensors = ["energy", "precipitation", "level"]

	conditions = ["sensor_name = %s"]
	params = [sensor_name]

	now = now_datetime()

	if date_from and not date_to:
		try:
			start_dt = datetime.strptime(date_from, "%Y-%m-%d")
			end_dt = start_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
			date_from = start_dt.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
			date_to = end_dt.strftime("%Y-%m-%d %H:%M:%S")
		except:
			pass

	if not date_from:
		if timespan == "last_year":
			start_dt = now - timedelta(days=365)
		elif timespan == "last_quarter":
			start_dt = now - timedelta(days=90)
		elif timespan == "last_month":
			start_dt = now - timedelta(days=30)
		elif timespan == "last_week":
			start_dt = now - timedelta(days=6)
		else:
			start_dt = now - timedelta(hours=23)
		date_from = start_dt.replace(minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

	if not date_to:
		end_dt = now.replace(minute=59, second=59, microsecond=999999)
		date_to = end_dt.strftime("%Y-%m-%d %H:%M:%S")

	conditions.append("timestamp >= %s")
	conditions.append("timestamp < %s")
	params.extend([date_from, date_to])
	where_clause = " AND ".join(conditions)

	format_map = {
		"hourly": "%Y-%m-%d %H:00",
		"daily": "%Y-%m-%d",
		"weekly": "%Y-%U",
		"monthly": "%Y-%m",
		"yearly": "%Y"
	}

	if not time_interval:
		time_interval = "daily"

	agg_func = "SUM" if sensor_name in sum_sensors else "AVG"

	if time_interval == "quarterly":
		query = f"""
			SELECT
				CONCAT(YEAR(timestamp), '-Q', QUARTER(timestamp)) as label,
				{agg_func}(value) as agg_value
			FROM `tabSensor Reading`
			WHERE {where_clause}
			GROUP BY label
			ORDER BY label
		"""
		data = frappe.db.sql(query, params, as_dict=True)
		data_map = {row["label"]: round(row["agg_value"], 2) for row in data}

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
		valid_values = [v for v in values if v is not None]
		min_value = min(valid_values) if valid_values else None
		max_value = max(valid_values) if valid_values else None

		return {
			"labels": formatted_labels,
			"values": values,
			"label_format": "quarterly",
			"unit": "",
			"min_value": min_value,
			"max_value": max_value
		}

	sql_format = format_map.get(time_interval, "%Y-%m-%d")
	query = f"""
		SELECT
			DATE_FORMAT(timestamp, %s) as label,
			{agg_func}(value) as agg_value
		FROM `tabSensor Reading`
		WHERE {where_clause}
		GROUP BY label
		ORDER BY label
	"""
	data = frappe.db.sql(query, [sql_format] + params, as_dict=True)
	data_map = {row["label"]: round(row["agg_value"], 2) for row in data}

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
	valid_values = [v for v in values if v is not None]
	min_value = min(valid_values) if valid_values else None
	max_value = max(valid_values) if valid_values else None

	label_format = "time_only" if time_interval == "hourly" and (date_from or timespan == "last_24h") else time_interval

	return {
		"labels": formatted_labels,
		"values": values,
		"label_format": label_format,
		"unit": "",
		"min_value": min_value,
		"max_value": max_value
	}
