import frappe
from frappe import _

from frappe.utils import get_datetime
from datetime import datetime, timedelta

@frappe.whitelist()
def get_all_vehicle_trails(start_date=None, end_date=None, interval="hour", vehicle=None):
    try:
        filters = {
            "latitude": ["not in", [None, "", 0]],
            "longitude": ["not in", [None, "", 0]]
        }

        if start_date:
            filters["creation"] = [">=", get_datetime(start_date)]
        if end_date:
            filters["creation"] = filters.get("creation", []) + ["<=", get_datetime(end_date) + timedelta(days=1)]

        if vehicle:
            vehicle_doc = frappe.get_doc("Vehicle", vehicle)
            filters["imei"] = vehicle_doc.imei

        readings = frappe.get_all("GPS Reading", filters=filters, fields=["imei", "latitude", "longitude", "creation"], order_by="creation asc")

        if not readings:
            return []

        # Group by IMEI
        from collections import defaultdict
        vehicle_trails = defaultdict(list)

        for r in readings:
            vehicle_trails[r["imei"]].append({
                "latitude": float(r["latitude"]),
                "longitude": float(r["longitude"]),
                "timestamp": r["creation"]
            })

        # Resolve IMEI to vehicle name
        results = []
        for v in frappe.get_all("Vehicle", filters={"imei": ["in", list(vehicle_trails.keys())]}, fields=["name", "imei"]):
            results.append({
                "name": v.name,
                "imei": v.imei,
                "timestamp": vehicle_trails[v.imei][-1]["timestamp"],  # latest
                "trail": vehicle_trails[v.imei]
            })

        return results

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to get vehicle trails")
        frappe.throw(_("Could not retrieve GPS trails"))
