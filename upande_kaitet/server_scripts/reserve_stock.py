# import frappe
# from frappe import _

# @frappe.whitelist()
# def reserve_stems(item_code,
#                   custom_source_warehouse,
#                   stems_requested,
#                   sales_order_item=None):
#     """
#     Reserve stock for an item by creating a Stock Entry
#     and updating the reserved_qty in Bin.
#     """
#     stems_requested = int(stems_requested)

#     # Skip if the sales_order_item is a temporary ID (starts with "new-")
#     if sales_order_item and sales_order_item.startswith("new-"):
#         return {
#             "reserved_qty":
#             0,
#             "status":
#             "Not Reserved",
#             "message":
#             "Cannot reserve for temporary items. Save the document first."
#         }

#     # Determine destination: Graded Reserve warehouse
#     farm = custom_source_warehouse.split(" ")[0]
#     graded_reserve_warehouse = f"{farm} Graded Reserve - TL"

#     # Check if there's sufficient stock available
#     bin_data = frappe.get_value("Bin", {
#         "item_code": item_code,
#         "warehouse": custom_source_warehouse
#     }, ["actual_qty", "reserved_qty"],
#                                 as_dict=True)

#     if not bin_data:
#         return {
#             "reserved_qty":
#             0,
#             "status":
#             "Not Found",
#             "message":
#             f"No stock found for {item_code} in {custom_source_warehouse}."
#         }

#     available_stems = max(0, bin_data.actual_qty - bin_data.reserved_qty)
#     stems_to_reserve = min(available_stems, stems_requested)

#     if stems_to_reserve <= 0:
#         return {
#             "reserved_qty":
#             0,
#             "status":
#             "Insufficient Stock",
#             "message":
#             f"Could not reserve stems for {item_code} from {custom_source_warehouse}. Available: {available_stems}, Requested: {stems_requested}"
#         }

#     # Create and submit a stock entry to transfer items to reserve warehouse
#     try:
#         stock_entry = create_reserve_stock_entry(
#             item_code=item_code,
#             source_warehouse=custom_source_warehouse,
#             target_warehouse=graded_reserve_warehouse,
#             qty=stems_to_reserve,
#             sales_order_item=
#             sales_order_item  # Pass the sales_order_item if provided
#         )
#     except Exception as e:
#         frappe.log_error(f"Failed to create stock entry: {str(e)}",
#                          "Reserve Stock Error")
#         return {
#             "reserved_qty": 0,
#             "status": "Error",
#             "message": f"Failed to create stock entry: {str(e)}"
#         }

#     # Update reserved qty in bin
#     frappe.db.set_value("Bin", {
#         "item_code": item_code,
#         "warehouse": custom_source_warehouse
#     }, "reserved_qty", bin_data.reserved_qty + stems_to_reserve)

#     return {
#         "reserved_qty": stems_to_reserve,
#         "status": "Reserved",
#         "message":
#         f"Reserved {stems_to_reserve} stems for {item_code} from {custom_source_warehouse}.",
#         "stock_entry": stock_entry.name
#     }

# @frappe.whitelist()
# def unreserve_stems(item_code,
#                     warehouse,
#                     stems_to_unreserve,
#                     sales_order_item=None):
#     """
#     Unreserve stock by canceling the stock entry and updating the Bin.
#     """
#     stems_to_unreserve = int(stems_to_unreserve)

#     # Find and cancel the stock entry for this sales order item
#     if sales_order_item:
#         stock_entries = frappe.get_all(
#             "Stock Entry",
#             filters={
#                 "docstatus": 1,  # Submitted
#                 "custom_sales_order_item": sales_order_item
#             },
#             fields=["name"])

#         for entry in stock_entries:
#             stock_entry_doc = frappe.get_doc("Stock Entry", entry.name)
#             stock_entry_doc.cancel()
#             frappe.msgprint(
#                 f"Cancelled stock entry {entry.name} for {item_code}")

#     # Update bin data
#     bin_data = frappe.get_value("Bin", {
#         "item_code": item_code,
#         "warehouse": warehouse
#     }, ["actual_qty", "reserved_qty"],
#                                 as_dict=True)

#     if not bin_data:
#         return {
#             "unreserved_qty": 0,
#             "status": "Not Found",
#             "message": f"No bin found for {item_code} in {warehouse}."
#         }

#     updated_reserved = max(0, bin_data.reserved_qty - stems_to_unreserve)

#     frappe.db.set_value("Bin", {
#         "item_code": item_code,
#         "warehouse": warehouse
#     }, "reserved_qty", updated_reserved)

#     return {
#         "unreserved_qty":
#         stems_to_unreserve,
#         "status":
#         "Unreserved",
#         "message":
#         f"Unreserved {stems_to_unreserve} stems of {item_code} from {warehouse} back to Available for Sale."
#     }

# @frappe.whitelist()
# def update_reservation(sales_order_item, item_code, custom_source_warehouse,
#                        qty_requested):
#     """
#     Update an existing reservation by canceling the old stock entry
#     and creating a new one with updated quantities.
#     """
#     # First unreserve the existing stock
#     existing_stock_entries = frappe.get_all(
#         "Stock Entry",
#         filters={
#             "docstatus": 1,  # Submitted
#             "custom_sales_order_item": sales_order_item
#         },
#         fields=["name"])

#     if existing_stock_entries:
#         # Get the old reserved quantity from the stock entry
#         old_entry = frappe.get_doc("Stock Entry",
#                                    existing_stock_entries[0].name)
#         old_qty = 0
#         for item in old_entry.items:
#             if item.item_code == item_code and item.s_warehouse == custom_source_warehouse:
#                 old_qty = item.qty
#                 break

#         # Unreserve the old quantity
#         unreserve_stems(item_code=item_code,
#                         warehouse=custom_source_warehouse,
#                         stems_to_unreserve=old_qty,
#                         sales_order_item=sales_order_item)

#     # Now create a new reservation
#     return reserve_stems(item_code=item_code,
#                          custom_source_warehouse=custom_source_warehouse,
#                          stems_requested=qty_requested)

# def create_reserve_stock_entry(item_code,
#                                source_warehouse,
#                                target_warehouse,
#                                qty,
#                                sales_order_item=None):
#     """
#     Create and submit a stock entry to transfer items from source to reserve warehouse
#     """
#     stock_entry = frappe.new_doc("Stock Entry")
#     stock_entry.stock_entry_type = "Material Transfer"
#     stock_entry.purpose = "Material Transfer"
#     stock_entry.from_warehouse = source_warehouse
#     stock_entry.to_warehouse = target_warehouse

#     # Link this stock entry to the sales order item
#     if sales_order_item:
#         stock_entry.custom_sales_order_item = sales_order_item

#     stock_entry.append(
#         "items", {
#             "item_code":
#             item_code,
#             "qty":
#             qty,
#             "s_warehouse":
#             source_warehouse,
#             "t_warehouse":
#             target_warehouse,
#             "basic_rate":
#             frappe.get_value("Item", item_code, "valuation_rate") or 0
#         })

#     stock_entry.save()
#     stock_entry.submit()

#     return stock_entry

# def on_sales_order_item_delete(doc, method):
#     """
#     Handle unreserving when a Sales Order Item is deleted
#     """
#     try:
#         if doc.item_code and hasattr(doc, 'custom_source_warehouse') and \
#            hasattr(doc, 'custom_reserved_qty') and doc.custom_source_warehouse and doc.custom_reserved_qty:

#             # Unreserve the stems
#             result = unreserve_stems(
#                 item_code=doc.item_code,
#                 warehouse=doc.custom_source_warehouse,
#                 stems_to_unreserve=doc.custom_reserved_qty,
#                 sales_order_item=doc.name)

#             # Log the action
#             frappe.logger().info(
#                 f"Unreserved {doc.custom_reserved_qty} of {doc.item_code} from {doc.custom_source_warehouse}"
#             )
#             frappe.logger().info(f"Result: {result}")

#             frappe.msgprint(
#                 f"Unreserved {doc.custom_reserved_qty} of {doc.item_code} from {doc.custom_source_warehouse}"
#             )
#     except Exception as e:
#         frappe.logger().error(f"Error in unreserve on delete: {str(e)}")
