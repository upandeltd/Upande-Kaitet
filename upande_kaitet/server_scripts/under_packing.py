import frappe
from frappe import _
#from frappe.model.document import Document
from upande_kaitet.upande_kaitet.doctype.farm_pack_list.farm_pack_list import transfer_stock_on_submit, process_consolidated_pack_list


@frappe.whitelist()
def request_under_pack_authorization(doc_name):
    """Request authorization for under packed FPL"""
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to request under pack authorization"))

    doc = frappe.get_doc("Farm Pack List", doc_name)

    # Check if completion is less than 100%
    packed_stems = doc.custom_total_stems or 0
    required_stems = doc.custom_picked_total_stems or 0
    completion_percentage = 0

    if required_stems > 0:
        completion_percentage = (packed_stems / required_stems) * 100

    if completion_percentage >= 100:
        frappe.throw(_("This Farm Pack List is already fully packed"))

    # Check if reason is provided
    if not doc.custom_under_pack_reason:
        frappe.throw(_("Please provide a reason for under packing"))

    # Update workflow state to send for review
    doc.db_set('workflow_state', 'Pending Order Review', update_modified=True)

    return True


@frappe.whitelist()
def approve_under_pack(doc_name):
    """Approve under packed FPL by Sales Manager"""
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to approve under pack authorization"))

    if 'Sales Manager' not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Only Sales Managers can approve under packed FPLs"))

    doc = frappe.get_doc("Farm Pack List", doc_name)

    # Set workflow state to Reviewed
    doc.db_set('workflow_state', 'Reviewed', update_modified=True)

    # Add a comment for audit trail
    frappe.get_doc({
        "doctype":
        "Comment",
        "comment_type":
        "Info",
        "reference_doctype":
        "Farm Pack List",
        "reference_name":
        doc_name,
        "content":
        f"Under Pack approved by {frappe.session.user}. Reason: {doc.custom_under_pack_reason}"
    }).insert(ignore_permissions=True)

    # Trigger stock transfer and CPL update
    transfer_stock_on_submit(doc)
    process_consolidated_pack_list(doc.name)

    return True


@frappe.whitelist()
def reject_under_pack(doc_name):
    """Reject under packed FPL by Sales Manager"""
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to reject under pack authorization"))

    # Check if user has Sales Manager role
    if 'Sales Manager' not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Only Sales Managers can approve under packed FPLs"))

    doc = frappe.get_doc("Farm Pack List", doc_name)

    doc.db_set('workflow_state', 'Draft', update_modified=True)

    return True


# Added Under Pack Cancel Button - Here's the function for the api call
@frappe.whitelist()
def transfer_stock_on_cancel(docname):
    """Transfers stock from Delivery Truck back to source warehouse when Farm Pack List is cancelled."""

    # Get the document from the name
    doc = frappe.get_doc("Farm Pack List", docname)

    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    target_warehouses = [
        "Burguret Graded Sold - TL", "Turaco Graded Sold - TL",
        "Pendekeza Graded Sold - TL"
    ]

    source_warehouse = "Delivery Truck - TL"

    if not frappe.db.exists("Warehouse", source_warehouse):
        frappe.throw(f"Source Warehouse '{source_warehouse}' does not exist.")

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.farm_pack_list = doc.name

    for item in doc.pack_list_item:
        target_warehouse = item.source_warehouse

        # Validate if target warehouse is one of the allowed warehouses
        if target_warehouse not in target_warehouses:
            frappe.throw(
                f"Invalid target warehouse '{target_warehouse}'. Expected: " +
                ", ".join(target_warehouses))

        if not frappe.db.exists("Warehouse", target_warehouse):
            frappe.throw(
                f"Target Warehouse '{target_warehouse}' does not exist.")

        # Add items to the Stock Entry
        stock_entry.append(
            "items", {
                "s_warehouse": source_warehouse,
                "t_warehouse": target_warehouse,
                "item_code": item.item_code,
                "qty": item.bunch_qty,
                "uom": item.bunch_uom,
                "stock_uom": item.bunch_uom,
            })

    stock_entry.save(ignore_permissions=True)
    stock_entry.submit()

    # Update workflow state to "Cancelled" instead of changing docstatus directly
    doc.db_set('workflow_state', 'Cancelled', update_modified=True)

    # Add a comment for audit trail
    frappe.get_doc({
        "doctype":
        "Comment",
        "comment_type":
        "Info",
        "reference_doctype":
        "Farm Pack List",
        "reference_name":
        docname,
        "content":
        f"Farm Pack List is cancelled via the 'Under Pack Cancel button' by {frappe.session.user}"
    }).insert(ignore_permissions=True)

    frappe.msgprint(
        f"Stock Transfer Created from {source_warehouse} to {target_warehouse} Successfully!",
        alert=True,
        indicator="green",
        wide=True,
    )

    return True
