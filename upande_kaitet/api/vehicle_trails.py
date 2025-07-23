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


from frappe import frappe
from datetime import datetime, timedelta

@frappe.whitelist()
def get_latest_gps_readings():
    """Fetch the latest GPS reading for each vehicle (updated hourly)."""
    try:
        # Get readings from the last 1 hour (to ensure freshness)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        readings = frappe.get_all(
            "GPS Reading",
            filters={
                "date": [">", one_hour_ago],  # Only recent readings
                "latitude": ["!=", 0],
                "longitude": ["!=", 0],
            },
            fields=["imei", "latitude", "longitude", "date"],
            order_by="date DESC",
            group_by="imei",  # Get only the latest per vehicle
            limit=100,  # Max 100 vehicles
        )

        return {
            "success": True,
            "data": [{
                "imei": r["imei"],
                "latitude": float(r["latitude"]),
                "longitude": float(r["longitude"]),
                "timestamp": r["date"].strftime("%H:%M"),  # Local time (e.g., "14:30")
            } for r in readings]
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Hourly GPS Fetch Failed")
        return {"success": False, "error": str(e)}