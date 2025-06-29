import frappe
from datetime import timedelta
from collections import defaultdict

@frappe.whitelist()
def get_hourly_chart_data(chart):
    chart_doc = frappe.get_doc("Dashboard Chart", chart)
    filters = frappe.parse_json(chart_doc.filters_json or "{}")
    doctype = chart_doc.document_type
    label_field = chart_doc.timeseries or "timestamp"
    value_field = chart_doc.based_on or "value"

    start_time = frappe.utils.now_datetime() - timedelta(hours=24)
    filters[label_field] = [">=", start_time]

    records = frappe.get_all(
        doctype,
        filters=filters,
        fields=[label_field, value_field],
        order_by=f"{label_field} asc"
    )

    # group by hour
    hourly_data = defaultdict(list)
    for r in records:
        dt = frappe.utils.get_datetime(r[label_field])
        hour = dt.hour
        hourly_data[hour].append(r[value_field])

    # Always return 24 hours, zero if no data for that hour
    labels = [f"{h:02d}:00" for h in range(24)]
    values = [
        round(sum(hourly_data[h]) / len(hourly_data[h]), 2) if hourly_data[h] else 0
        for h in range(24)
    ]

    return {
        "labels": labels,
        "datasets": [{
            "name": chart_doc.chart_name,
            "values": values
        }],
        "type": "bar",            
        "colors": ["#00f836"],      
        "yMarkers": [],              
        "yRegions": []               
    }
