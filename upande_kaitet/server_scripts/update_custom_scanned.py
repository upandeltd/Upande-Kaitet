import frappe

# Custom scanned
@frappe.whitelist()
def update_custom_scanned(stock_entry_name, action, oplName = None):
    stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)

    if stock_entry.docstatus == 1 and action == "Receiving":
        stock_entry.db_set("custom_scanned", 1)
        frappe.db.commit()

    if stock_entry.docstatus == 1 and action == "Packing":
        stock_entry.db_set("custom_scanned_packing", 1)
        stock_entry.db_set("custom_opl_scanned", oplName)
        frappe.db.commit()