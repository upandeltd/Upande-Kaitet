# import frappe

# def validate_completion_percentage(doc, method):
#     # Calculate packed stems
#     packed_stems = float(doc.custom_total_stems or 0)

#     # Total stems from sales orders
#     total_required_stems = 0
#     seen_sales_orders = set()

#     for item in doc.items:
#         sales_order_id = item.sales_order_id
#         if sales_order_id and sales_order_id not in seen_sales_orders:
#             sales_order = frappe.get_doc("Sales Order", sales_order_id)
#             total_required_stems += float(sales_order.custom_total_stock_qty
#                                           or 0)
#             seen_sales_orders.add(sales_order_id)

#     # Calculate completion percentage
#     if total_required_stems > 0:
#         completion_percentage = (packed_stems / total_required_stems) * 100
#     else:
#         completion_percentage = 0

#     # Update the field on the form
#     doc.completion_percentage = completion_percentage

#     if doc.workflow_state == "Approved" and completion_percentage < 100:
#         frappe.throw(f"""
#             You cannot approve this Consolidated Pack List (CPL) because it is incomplete.<br><br>
#             Packed Stems: <b>{packed_stems}</b><br>
#             Required Stems(from Sales Order): <b>{total_required_stems}</b><br>
#             Completion: <b>{round(completion_percentage, 2)}%</b><br><br>
#             Please ensure all required stems are packed before approval.
#         """)
