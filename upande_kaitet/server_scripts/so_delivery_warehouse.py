import frappe
from frappe import _


def handle_sales_order_approval(doc, method):
    warehouse_mapping = {
        "Turaco Available for Sale - TL": "Turaco Graded Sold - TL",
        "Pendekeza Available for Sale - TL": "Pendekeza Graded Sold - TL",
        "Burguret Available for Sale - TL": "Burguret Graded Sold - TL",
        "TUR Grading Forecast - TL": "Turaco Graded Sold - TL",
        "PNDK Grading Forecast - TL": "Pendekeza Graded Sold - TL",
        "BUR Grading Forecast - TL": "Burguret Graded Sold - TL",
    }

    updated = False
    for item in doc.items:
        if item.custom_source_warehouse:
            mapped_warehouse = warehouse_mapping.get(
                item.custom_source_warehouse, "")
            if mapped_warehouse and item.warehouse != mapped_warehouse:
                item.warehouse = mapped_warehouse
                updated = True

    if updated:
        doc.save()
        frappe.msgprint(
            "Delivery warehouse updated based on Source Warehouse.")

    # Create Stock Entry for Transfer
    if doc.docstatus == 1:
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.sales_order = doc.name

        items_details = []

        for item in doc.items:
            if item.custom_source_warehouse and item.warehouse:
                stock_entry.append(
                    "items",
                    {
                        "item_code": item.item_code,
                        "qty": item.qty,
                        "uom": item.uom,
                        "stock_uom": item.stock_uom,
                        "s_warehouse": item.custom_source_warehouse,
                        "t_warehouse": item.warehouse,
                        "stock_qty": item.stock_qty,
                    },
                )

                # Store item details for message
                items_details.append({
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "from_warehouse": item.custom_source_warehouse,
                    "to_warehouse": item.warehouse
                })

        if stock_entry.items:
            stock_entry.insert()
            stock_entry.submit()

            # Create formatted table message
            table_html = """
            <div style="margin-bottom: 10px;">Stock Transfer Created Successfully!</div>
            <table class="table table-bordered" style="width: 100%;">
                <thead>
                    <tr>
                        <th style="text-align: left;">Item Code</th>
                        <th style="text-align: right;">Quantity</th>
                        <th style="text-align: left;">From Warehouse</th>
                        <th style="text-align: left;">To Warehouse</th>
                    </tr>
                </thead>
                <tbody>
            """

            for item in items_details:
                table_html += f"""
                    <tr>
                        <td>{item["item_code"]}</td>
                        <td style="text-align: right;">{item["qty"]} {item["uom"]}</td>
                        <td>{item["from_warehouse"]}</td>
                        <td>{item["to_warehouse"]}</td>
                    </tr>
                """

            table_html += """
                </tbody>
            </table>
            """

            frappe.msgprint(table_html,
                            title="Stock Transfer Details",
                            indicator="green")


def handle_sales_order_cancellation(doc, method):
    items_details = []

    if doc.docstatus == 2:
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.sales_order = doc.name

        for item in doc.items:
            source_warehouse = item.warehouse
            custom_source_warehouse = item.get("custom_source_warehouse")

            if not source_warehouse or not custom_source_warehouse:
                continue

            stock_entry.append(
                "items",
                {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "stock_uom": item.stock_uom,
                    "s_warehouse": source_warehouse,
                    "t_warehouse": custom_source_warehouse,
                    "stock_qty": item.stock_qty,
                },
            )

            items_details.append({
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "from_warehouse": source_warehouse,
                "to_warehouse": custom_source_warehouse
            })

        if stock_entry.items:
            stock_entry.insert()
            stock_entry.submit()

            table_html = """
            <div style="margin-bottom: 10px;">Stock Reversal Transfer Created Successfully!</div>
            <table class="table table-bordered" style="width: 100%;">
                <thead>
                    <tr>
                        <th style="text-align: left;">Item Code</th>
                        <th style="text-align: right;">Quantity</th>
                        <th style="text-align: left;">From Warehouse</th>
                        <th style="text-align: left;">To Warehouse</th>
                    </tr>
                </thead>
                <tbody>
            """

            for item in items_details:
                table_html += f"""
                    <tr>
                        <td>{item["item_code"]}</td>
                        <td style="text-align: right;">{item["qty"]} {item["uom"]}</td>
                        <td>{item["from_warehouse"]}</td>
                        <td>{item["to_warehouse"]}</td>
                    </tr>
                """

            table_html += "</tbody></table>"

            frappe.msgprint(
                table_html,
                title="Stock Transfer Reversed After Sales Order is Cancelled",
                indicator="blue"
            )
        else:
            frappe.msgprint("No valid stock transfer items found for reversal.")