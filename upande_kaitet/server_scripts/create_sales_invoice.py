# Copyright (c) 2025, Upande Limited
# For license information, please see license.txt
import frappe
from frappe.utils import getdate, today

def create_sales_invoice_from_packlist(doc, method):
    """
    Function to create Sales Invoices from a Consolidated Pack List.
    - Handles multiple Sales Orders in one Pack List.
    - Implements error handling to prevent failures from stopping execution.
    """

    sales_order_ids = list(set([item.sales_order_id for item in doc.items if item.sales_order_id]))

    if not sales_order_ids:
        frappe.throw("No Sales Order linked to this Consolidated Pack List.")

    created_invoices = []
    failed_invoices = []

    for sales_order_id in sales_order_ids:
        try:
            
            sales_order = frappe.get_doc("Sales Order", sales_order_id)

            # Create New Sales Invoice
            sales_invoice = frappe.new_doc("Sales Invoice")
            sales_invoice.customer = sales_order.customer
            sales_invoice.currency = sales_order.currency
            sales_invoice.selling_price_list = sales_order.selling_price_list
            sales_invoice.custom_shipping_agent = sales_order.custom_shipping_agent
            sales_invoice.custom_destination = sales_order.custom_delivery_point
            sales_invoice.custom_consignee = sales_order.custom_consignee
            sales_invoice.custom_comment = sales_order.custom_comment
            sales_invoice.shipping_date = sales_order.delivery_date
            sales_invoice.custom_consolidated_packlist = doc.name
            sales_invoice.custom_so = doc.custom_sales_order_id_cpl
            sales_invoice.set_warehouse = doc.items[0].source_warehouse if doc.items else None  
            sales_invoice.posting_date = today()
            sales_invoice.update_stock = 1

            # Set Due Date
            delivery_date = sales_order.delivery_date if sales_order.delivery_date else sales_invoice.posting_date
            sales_invoice.due_date = max(getdate(delivery_date), getdate(sales_invoice.posting_date))

            sales_invoice.taxes_and_charges = sales_order.taxes_and_charges
            sales_invoice.taxes = sales_order.taxes

            # Process Items
            for dispatch_item in doc.items:
                if dispatch_item.sales_order_id != sales_order_id:
                    continue  # Skip items not in this Sales Order

                # Find corresponding Sales Order Item
                so_item = next((item for item in sales_order.items if item.item_code == dispatch_item.item_code), None)
                if not so_item:
                    failed_invoices.append(f"Item {dispatch_item.item_code} not found in Sales Order {sales_order_id}")
                    continue

                # Validate Quantity
                if not dispatch_item.bunch_qty or dispatch_item.bunch_qty <= 0:
                    failed_invoices.append(f"Invalid quantity for item {dispatch_item.item_code} in Consolidated Pack List {doc.name}")
                    continue

                sales_invoice.append("items", {
                    "item_code": dispatch_item.item_code,
                    "qty": dispatch_item.bunch_qty,
                    "uom": dispatch_item.bunch_uom,
                    "bunch_qty": dispatch_item.bunch_qty,
                    "bunch_uom": dispatch_item.bunch_uom,
                    "custom_number_of_stems": dispatch_item.custom_number_of_stems,
                    "rate": so_item.rate,
                    "custom_length": so_item.custom_length,
                    "discount_percentage": so_item.discount_percentage
                })

            if sales_invoice.items:
                
                sales_invoice.custom_cpl_status = "CPL Active"
                sales_invoice.flags.ignore_permissions = True
                sales_invoice.insert()
                # sales_invoice.submit()
                created_invoices.append(sales_invoice.name)
            else:
                failed_invoices.append(f"No valid items for Sales Order {sales_order_id}, invoice not created.")

        except Exception as e:
            failed_invoices.append(f"Sales Order {sales_order_id}: {str(e)}")

    # If there are failed invoices, prevent submission
    if failed_invoices:
        error_message = "<br>".join(failed_invoices)
        frappe.throw(f"Some invoices failed to generate:<br>{error_message}")

    if created_invoices:
        invoice_links = " | ".join(
            [f'<a href="/app/sales-invoice/{invoice}" target="_blank">{invoice}</a>' for invoice in created_invoices]
        )
        frappe.msgprint(f"Sales Invoice Created Successfully: {invoice_links}", title="Sales Invoice", indicator="green")
