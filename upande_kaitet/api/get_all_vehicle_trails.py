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
	R = 6371  # Earth radius in km
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

		base_dt = ke_tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))
		start_dt = base_dt.astimezone(UTC)
		end_dt = (base_dt + timedelta(days=1)).astimezone(UTC)

		if vehicle:
			vehicle_doc = frappe.get_doc("Vehicle", vehicle)
			vehicles = [{"name": vehicle_doc.name, "imei": vehicle_doc.imei}]
			imei_list = [vehicle_doc.imei]
		else:
			vehicles = frappe.get_all("Vehicle", fields=["name", "imei"], filters={"imei": ["!=", ""]})
			imei_list = [v["imei"] for v in vehicles]

		if not imei_list:
			return []

		readings = frappe.get_all(
			"GPS Reading",
			filters={
				"imei": ["in", imei_list],
				"latitude": ["not in", [None, "", 0]],
				"longitude": ["not in", [None, "", 0]],
				"creation": ["between", [start_dt, end_dt]],
			},
			fields=["imei", "latitude", "longitude", "creation"],
			order_by="creation asc",
		)

		if not readings:
			return []

		# Group all cleaned readings per IMEI
		all_readings = defaultdict(list)

		for r in readings:
			try:
				lat = float(r["latitude"])
				lon = float(r["longitude"])
				ts = get_datetime(r["creation"]).astimezone(ke_tz)
			except (ValueError, TypeError):
				continue

			if not is_valid_latlon(lat, lon):
				continue

			point = {"latitude": lat, "longitude": lon, "timestamp": ts}
			prev = all_readings[r["imei"]][-1] if all_readings[r["imei"]] else None
			if is_plausible_movement(prev, point):
				all_readings[r["imei"]].append(point)

		results = []

		for v in vehicles:
			imei = v["imei"]
			raw = all_readings.get(imei, [])
			if not raw:
				continue

			# Closest point to each hour (HH:00)
			hourly_points = {}
			for hour in range(24):
				target = base_dt.replace(hour=hour, minute=0, second=0, microsecond=0)
				best = None
				best_diff = float("inf")
				for p in raw:
					diff = abs((p["timestamp"] - target).total_seconds())
					if diff < best_diff:
						best = p
						best_diff = diff
				if best:
					hourly_points[hour] = {
						"latitude": best["latitude"],
						"longitude": best["longitude"],
						"timestamp": best["timestamp"].strftime("%H:%M"),
					}

			# Get latest point (closest to 23:59)
			latest_point = None
			target_latest = base_dt.replace(hour=23, minute=59, second=0, microsecond=0)
			best_diff = float("inf")
			for p in raw:
				diff = abs((p["timestamp"] - target_latest).total_seconds())
				if diff < best_diff:
					best_diff = diff
					latest_point = p
			if not latest_point:
				latest_point = raw[-1]

			formatted_ts = latest_point["timestamp"].strftime("%d-%m-%Y %H:%M")

			results.append({
				"name": v["name"],
				"imei": v["imei"],
				"timestamp": formatted_ts,
				"raw_trail": raw,
				"trail": list(hourly_points.values()),  # hourly average tooltips
				"latest_position": {
					"latitude": latest_point["latitude"],
					"longitude": latest_point["longitude"],
					"timestamp": formatted_ts,
				}
			})

		return results

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Vehicle Tracker: Failed to retrieve trails")
		frappe.throw(_("Could not retrieve GPS trails"))
