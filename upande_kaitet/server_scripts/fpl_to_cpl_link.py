import frappe
from frappe import _


def before_cancel(doc, method):
    if not doc.custom_sales_order:
        return

    # Get all related CPLs that are still Draft or Submitted
    cpl_links = frappe.db.sql("""
        SELECT DISTINCT parent 
        FROM `tabDispatch Form Item` 
        WHERE sales_order_id = %s
        AND parent IN (
            SELECT name FROM `tabConsolidated Pack List` WHERE docstatus IN (0, 1)
        )
    """, (doc.custom_sales_order, ),
                              as_dict=True)

    if cpl_links:
        unique_cpls = sorted(set(x.parent for x in cpl_links))

        linked_cpls_html = ", ".join(
            f'<a href="/app/consolidated-pack-list/{cpl}" target="_blank">{cpl}</a>'
            for cpl in unique_cpls)

        frappe.throw(_(
            f"""Cannot cancel this Farm Pack List because it is linked to the following Consolidated Pack List(s): 
            <br><br>{linked_cpls_html}<br><br>Please cancel them first."""),
                     title=_("Linked Consolidated Pack List(s)"))
