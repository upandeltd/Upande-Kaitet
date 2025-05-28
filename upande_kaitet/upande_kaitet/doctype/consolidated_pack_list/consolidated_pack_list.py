import frappe
from frappe import _
from frappe.model.document import Document


class ConsolidatedPackList(Document):

    # def on_cancel(self):
    #     transfer_stock_on_cpl_cancel(self)

    pass


# @frappe.whitelist()
# def transfer_stock_on_cpl_cancel(doc):
#     """Transfers stock from Delivery Truck back to Graded Sold when CPL is cancelled."""

#     if not doc.items:
#         frappe.throw("No items in Consolidated Pack List to transfer.")

#     dispatch_warehouses = [
#         "Burguret Graded Sold - TL", "Burguret Graded Sold - TL",
#         "Burguret Graded Sold - TL"
#     ]

#     # Map each sales order/customer to a default dispatch warehouse (if applicable)
#     # You can modify this logic based on business rules
#     default_dispatch_mapping = {
#         "Burguret": "Burguret Graded Sold - TL",
#         "Turaco": "Turaco Graded Sold - TL",
#         "Pendekeza": "Pendekeza Graded Sold - TL"
#     }

#     source_warehouse = "Delivery Truck - TL"  # Always moving stock FROM delivery truck

#     stock_entry = frappe.new_doc("Stock Entry")
#     stock_entry.stock_entry_type = "Material Transfer"
#     stock_entry.consolidated_pack_list = doc.name

#     for item in doc.items:
#         # Determine the target dispatch warehouse (defaulting based on logic)
#         target_warehouse = None
#         for key, warehouse in default_dispatch_mapping.items():
#             if key.lower() in item.customer_id.lower():
#                 target_warehouse = warehouse
#                 break

#         # If no matching mapping, default to one of the dispatch warehouses (fallback)
#         if not target_warehouse:
#             target_warehouse = dispatch_warehouses[
#                 0]  # Default to first in list

#         # Validate target warehouse
#         if target_warehouse not in dispatch_warehouses:
#             frappe.throw(
#                 f"Invalid or missing target warehouse '{target_warehouse}'. Allowed: "
#                 + ", ".join(dispatch_warehouses))

#         # Add items to the Stock Entry
#         stock_entry.append(
#             "items", {
#                 "s_warehouse": source_warehouse,
#                 "t_warehouse": target_warehouse,
#                 "item_code": item.item_code,
#                 "qty": item.bunch_qty,
#                 "uom": item.bunch_uom,
#                 "stock_uom": item.bunch_uom,
#             })

#     stock_entry.save(ignore_permissions=True)
#     stock_entry.submit()

#     frappe.msgprint(
#         f"Stock Transfer Created from {source_warehouse} to {target_warehouse} Successfully!",
#         alert=True,
#         indicator="red",
#         wide=True,
#     )
