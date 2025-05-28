import frappe
from frappe.utils import now
from datetime import datetime

@frappe.whitelist()
def get_current_timestamp():
    current_timestamp = now()

    # current_datetime = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S.%f" )

    # formatted_datetime = current_datetime.strftime("%d/%m/%Y %H:%M:%S")

    return current_timestamp
