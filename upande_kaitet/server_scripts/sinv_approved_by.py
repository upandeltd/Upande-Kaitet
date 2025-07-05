import frappe

def set_approved_by(doc, method):
    """Set the approved_by field to the logged-in user's full name"""
    user = frappe.session.user
    full_name = frappe.db.get_value("User", user, "full_name")
    
    if not doc.custom_approved_by:  
        doc.custom_approved_by = full_name
        doc.db_set("custom_approved_by", full_name) 
