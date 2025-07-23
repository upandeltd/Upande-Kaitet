import frappe
from frappe.utils import today

def execute(filters=None):
    if not filters:
        filters = {}

    start_date = filters.get("from_date") or "2000-01-01"
    end_date = filters.get("to_date") or today()

    results = frappe.db.sql("""
        SELECT 
            custom_faulty_part as faulty_part,
            COUNT(*) as total_faults,
            COUNT(DISTINCT custom_assetequipment) as assets_affected
        FROM `tabIssue`
        WHERE custom_faulty_part IS NOT NULL 
            AND custom_faulty_part != ''
            AND creation BETWEEN %s AND %s
        GROUP BY custom_faulty_part
        ORDER BY total_faults DESC
        LIMIT 15
    """, (start_date, end_date), as_dict=True)

    columns = [
        {"label": "Faulty Part", "fieldname": "faulty_part", "fieldtype": "Data", "width": 250},
        {"label": "Total Faults", "fieldname": "total_faults", "fieldtype": "Int", "width": 120},
        {"label": "Assets Affected", "fieldname": "assets_affected", "fieldtype": "Int", "width": 140}
    ]

    data = []
    for row in results:
        data.append({
            "faulty_part": row.faulty_part,
            "total_faults": row.total_faults,
            "assets_affected": row.assets_affected
        })

    return columns, data
