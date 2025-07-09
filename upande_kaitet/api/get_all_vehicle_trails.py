from collections import defaultdict
from datetime import datetime, timedelta
from math import atan2, cos, radians, sin, sqrt

import frappe
from frappe import _
from frappe.utils import get_datetime
from pytz import UTC, timezone

ke_tz = timezone("Africa/Nairobi")

def is_valid_latlon(lat, lon):
	return -5.0 <= lat <= 5.0 and 33.5 <= lon <= 42.5

def haversine(lat1, lon1, lat2, lon2):
	R = 6371
	dlat = radians(lat2 - lat1)
	dlon = radians(lon2 - lon1)
	a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
	return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def is_plausible_movement(prev, curr, min_distance_m=10, max_speed_kmph=80):
	if not prev:
		return True
	dist_km = haversine(prev["latitude"], prev["longitude"], curr["latitude"], curr["longitude"])
	dist_m = dist_km * 1000
	if dist_m < min_distance_m:
		return False
	time_diff_hr = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 3600.0
	if time_diff_hr == 0:
		return False
	speed_kmph = dist_km / time_diff_hr
	return speed_kmph <= max_speed_kmph

@frappe.whitelist()
def get_all_vehicle_trails(start_date=None, vehicle=None):
	try:
		if not start_date:
			frappe.throw(_("Start date is required"))

		filters = {
			"latitude": ["not in", [None, "", 0]],
			"longitude": ["not in", [None, "", 0]]
		}
		imei_list = []

		# Get datetime range for the selected day in Kenya timezone
		base_dt = ke_tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))
		start_dt = base_dt
		end_dt = base_dt + timedelta(days=1)

		# Filter by date range (in UTC)
		filters["creation"] = ["between", [start_dt.astimezone(UTC), end_dt.astimezone(UTC)]]

		if vehicle:
			vehicle_doc = frappe.get_doc("Vehicle", vehicle)
			imei = vehicle_doc.imei
			filters["imei"] = imei
			imei_list = [imei]
		else:
			imei_list = list({
				d["imei"]
				for d in frappe.get_all("Vehicle", fields=["imei"])
				if d["imei"]
			})

		# Get all GPS readings for that day
		readings = frappe.get_all(
			"GPS Reading",
			filters=filters,
			fields=["imei", "latitude", "longitude", "creation"],
			order_by="creation asc",
		)

		if not readings:
			return []

		vehicle_trails = defaultdict(list)

		for r in readings:
			try:
				lat = float(r["latitude"])
				lon = float(r["longitude"])
				timestamp = r["creation"]
			except (ValueError, TypeError):
				continue

			if not is_valid_latlon(lat, lon):
				continue

			point = {"latitude": lat, "longitude": lon, "timestamp": timestamp}
			prev = vehicle_trails[r["imei"]][-1] if vehicle_trails[r["imei"]] else None

			if is_plausible_movement(prev, point):
				vehicle_trails[r["imei"]].append(point)

		# Prepare final results: use last point from the trail for that date
		results = []

		for v in frappe.get_all("Vehicle", filters={"imei": ["in", imei_list]}, fields=["name", "imei"]):
			trail = vehicle_trails[v.imei]

			if not trail:
				continue

			last = trail[-1]  # last point of the day

			formatted_ts = last["timestamp"].replace(tzinfo=UTC).astimezone(ke_tz).strftime("%d-%m-%Y %H:%M")

			results.append({
				"name": v.name,
				"imei": v.imei,
				"timestamp": formatted_ts,
				"trail": trail,
				"latest_position": {
					"latitude": last["latitude"],
					"longitude": last["longitude"],
					"timestamp": formatted_ts,
				}
			})

		return results

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to get vehicle trails")
		frappe.throw(_("Could not retrieve GPS trails"))
