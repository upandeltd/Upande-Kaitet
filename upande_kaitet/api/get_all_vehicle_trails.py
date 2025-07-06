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
def get_all_vehicle_trails(start_date=None, end_date=None, interval="hour", vehicle=None):
	try:
		filters = {"latitude": ["not in", [None, "", 0]], "longitude": ["not in", [None, "", 0]]}

		if start_date and end_date:
			filters["creation"] = [
				"between",
				[get_datetime(start_date), get_datetime(end_date) + timedelta(days=1)],
			]
		elif start_date:
			filters["creation"] = [">=", get_datetime(start_date)]
		elif end_date:
			filters["creation"] = ["<=", get_datetime(end_date) + timedelta(days=1)]

		if vehicle:
			vehicle_doc = frappe.get_doc("Vehicle", vehicle)
			filters["imei"] = vehicle_doc.imei

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

		# Get latest raw readings by IMEI (regardless of plausibility)
		imei_list = list(vehicle_trails.keys())
		latest_by_imei = {}
		if imei_list:
			for r in frappe.get_all(
				"GPS Reading",
				filters={
					"imei": ["in", imei_list],
					"latitude": ["not in", [None, "", 0]],
					"longitude": ["not in", [None, "", 0]],
				},
				fields=["imei", "latitude", "longitude", "creation"],
				order_by="creation desc",
			):
				if r["imei"] not in latest_by_imei:
					latest_by_imei[r["imei"]] = r  # only first (latest) per imei

		results = []

		for v in frappe.get_all("Vehicle", filters={"imei": ["in", imei_list]}, fields=["name", "imei"]):
			trail = vehicle_trails[v.imei]
			latest = latest_by_imei.get(v.imei)

			if not latest:
				continue

			latest_lat = float(latest["latitude"])
			latest_lon = float(latest["longitude"])
			latest_time = latest["creation"].replace(tzinfo=UTC).astimezone(ke_tz)
			formatted_ts = latest_time.strftime("%d-%m-%Y %H:%M")

			results.append(
				{
					"name": v.name,
					"imei": v.imei,
					"timestamp": formatted_ts,  # Used for 'Last Seen'
					"trail": trail,  # For drawing the polyline
					"latest_position": {
						"latitude": latest_lat,
						"longitude": latest_lon,
						"timestamp": formatted_ts,
					},
				}
			)

		return results

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Failed to get vehicle trails")
		frappe.throw(_("Could not retrieve GPS trails"))
