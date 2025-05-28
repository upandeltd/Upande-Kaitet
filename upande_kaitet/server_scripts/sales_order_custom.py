# sales_order_custom.py
# Copyright (c) 2025, Upande Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def validate_customer_check_limit(doc, method):
    custom_check_limit = frappe.db.get_value("Customer", doc.customer, "custom_check_limit")

    if custom_check_limit:
        frappe.throw(_("Sales Order cannot proceed; Customer credit limit locked by Credit Controller!"))

