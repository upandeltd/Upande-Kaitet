import frappe

@frappe.whitelist()
def update_latest_vehicle_locations():
    """
    Fetch the most recent Vehicle Location for each vehicle and update the Vehicle DocType.
    Updates: latest_latitude, latest_longitude, latitude, longitude
    """
    vehicle_names = frappe.get_all("Vehicle", pluck="name")

    for vehicle_name in vehicle_names:
        latest_location = frappe.get_all(
            "Vehicle Location",
            filters={"vehicle": vehicle_name},
            fields=["latitude", "longitude", "creation"],
            order_by="creation desc",
            limit=1
        )

        if latest_location:
            lat = latest_location[0].latitude
            lon = latest_location[0].longitude

            frappe.db.set_value("Vehicle", vehicle_name, {
                "latest_latitude": lat,
                "latest_longitude": lon,
                "latitude": lat,
                "longitude": lon
            })

    frappe.db.commit()

import frappe
@frappe.whitelist()
def get_tph_readings():
    return frappe.get_all(
        "TPH Reading",
        fields=["temperature", "pressure", "humidity", "timestamp"],
        order_by="timestamp desc",
        limit=50
    )

@frappe.whitelist()
def get_all_vehicle_locations():
    return frappe.get_all(
        "Vehicle",
        filters={"latest_latitude": ["!=", 0], "latest_longitude": ["!=", 0]},
        fields=["name", "make", "plates", "latest_latitude as latitude", "latest_longitude as longitude"]
    )
