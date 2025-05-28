import frappe
from frappe import _
from frappe.utils import get_link_to_form

def on_cpl_cancel(doc, method):
    """
    Triggered when a Consolidated Pack List is cancelled:
    - Marks draft and cancelled linked Sales Invoices as 'CPL Cancelled'
    """
    sales_invoices = frappe.get_all(
        "Sales Invoice",
        filters={"custom_consolidated_packlist": doc.name},
        fields=["name", "docstatus"]
    )

    for inv in sales_invoices:
        try:
            invoice = frappe.get_doc("Sales Invoice", inv.name)
            if invoice.docstatus == 0:
                invoice.db_set("custom_cpl_status", "CPL Cancelled")
                frappe.logger().info(f"[CPL Cancel] Draft Sales Invoice {invoice.name} marked as CPL Cancelled.")
            elif invoice.docstatus == 2:
                # Invoice already cancelled — make sure CPL status reflects that
                invoice.db_set("custom_cpl_status", "CPL Cancelled")
                frappe.logger().info(f"[CPL Cancel] Already cancelled Sales Invoice {invoice.name} updated with CPL Cancelled status.")
        except Exception as e:
            frappe.log_error(f"Error updating Sales Invoice {inv.name}: {str(e)}", "CPL Cancel Event")


def on_sales_invoice_cancel(doc, method):
    """
    Triggered when a Sales Invoice is cancelled.
    - Updates CPL status field if the invoice is linked to a CPL.
    - But only updates if the CPL is actually cancelled.
    - Shows message if CPL is still active.
    """
    if doc.custom_consolidated_packlist:
        try:
            cpl = frappe.get_doc("Consolidated Pack List", doc.custom_consolidated_packlist)

            if cpl.docstatus == 2:  # Cancelled
                frappe.db.set_value("Sales Invoice", doc.name, "custom_cpl_status", "CPL Cancelled")
                frappe.logger().info(f"[SI Cancel] Sales Invoice {doc.name} was cancelled and CPL {cpl.name} is cancelled too. CPL status updated.")
            else:
                cpl_link = get_link_to_form("Consolidated Pack List", cpl.name)
                frappe.msgprint(
                    _(f"Sales Invoice {doc.name} is cancelled, but Consolidated Pack List {cpl_link} is still active. CPL status not updated."),
                    title=_("Warning"),
                    indicator="orange"
                )
                frappe.logger().warn(f"[SI Cancel] Sales Invoice {doc.name} was cancelled, but CPL {cpl.name} is still active. Status not updated.")

        except Exception as e:
            frappe.log_error(f"Error checking CPL cancellation status for {doc.name}: {str(e)}", "SI Cancel Event")