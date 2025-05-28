# import frappe

# def bypass_negative_stock_validation(doc, method):

#     # For Sales Order
#     if doc.doctype == "Sales Order":
#         for item in doc.items:
#             if item.custom_source_warehouse:
#                 allow_negative = frappe.db.get_value("Warehouse",
#                                                      item.warehouse,
#                                                      "allow_negative_stock")
#                 if allow_negative:
#                     # Skip the stock validation for this item
#                     item.custom_allow_negative_stock = 1

#     # For Stock Entry
#     elif doc.doctype == "Stock Entry":
#         for item in doc.items:
#             if item.t_warehouse:  # Target warehouse
#                 allow_negative = frappe.db.get_value("Warehouse",
#                                                      item.t_warehouse,
#                                                      "allow_negative_stock")
#                 if allow_negative:
#                     # Skip the stock validation for this item
#                     item.custom_allow_negative_stock = 1
