#   Creation of sales invoice from dispatch form

# import frappe
# from frappe.utils import nowdate, getdate

# def create_sales_invoice(doc, method):
#     print(f"Processing Dispatch Form: {doc.name}")

#     sales_order_ids = list(set([item.sales_order_id for item in doc.custom_sku_summary if item.sales_order_id]))

#     if not sales_order_ids:
#         frappe.throw("No Sales Order linked to this Dispatch Form.")

#     for sales_order_id in sales_order_ids:
#         print(f"Processing Sales Order ID: {sales_order_id}")
#         sales_order = frappe.get_doc("Sales Order", sales_order_id)

#         # Create new Sales Invoice
#         sales_invoice = frappe.new_doc("Sales Invoice")
#         sales_invoice.customer = sales_order.customer
#         sales_invoice.custom_dispatch_form = doc.name  # Link Dispatch Form

#         # Ensure posting date and due date are valid
#         sales_invoice.posting_date = nowdate()
#         delivery_date = getdate(sales_order.delivery_date) if sales_order.delivery_date else getdate(nowdate())
#         sales_invoice.due_date = max(delivery_date, getdate(sales_invoice.posting_date))

#         # Copy taxes and discounts
#         sales_invoice.taxes_and_charges = sales_order.taxes_and_charges
#         sales_invoice.taxes = sales_order.taxes

#         print(f"Creating Sales Invoice for Customer: {sales_order.customer}")

#         # Process Dispatch Form Items
#         for dispatch_item in doc.custom_sku_summary:
#             if dispatch_item.sales_order_id != sales_order_id:
#                 continue  # Skip items not linked to this Sales Order

#             print(f"Processing Dispatch Item: {dispatch_item.item_code}")

#             # Find matching item from Sales Order
#             so_item = next((item for item in sales_order.items if item.item_code == dispatch_item.item_code), None)
#             if not so_item:
#                 frappe.throw(f"Item {dispatch_item.item_code} not found in Sales Order {sales_order_id}")

#             # Validate item quantity
#             item_qty = dispatch_item.bunch_qty
#             if not item_qty or item_qty <= 0:
#                 frappe.throw(f"Invalid quantity for item {dispatch_item.item_code} in Dispatch Form {doc.name}")

#             print(f"Appending Item: {dispatch_item.item_code}, Qty: {item_qty}, Warehouse: {dispatch_item.source_warehouse}")

#             # Append item to Sales Invoice
#             sales_invoice.append("items", {
#                 "item_code": dispatch_item.item_code,
#                 "qty": dispatch_item.bunch_qty,
#                 "bunch_qty": dispatch_item.bunch_qty,
#                 "bunch_uom": dispatch_item.bunch_uom,
#                 "no_of_stems": dispatch_item.no_of_stems,
#                 "rate": so_item.rate,
#                 "custom_length": so_item.custom_length,
#                 "discount_percentage": so_item.discount_percentage,
#                 "set_warehouse": dispatch_item.source_warehouse  # Ensure warehouse is correctly assigned
#             })

#         # Save Sales Invoice
#         sales_invoice.flags.ignore_permissions = True
#         sales_invoice.insert()

#         print(f"Sales Invoice {sales_invoice.name} created successfully with Warehouse set.")
#         frappe.msgprint(f"Sales Invoice {sales_invoice.name} created from Dispatch Form {doc.name}")
