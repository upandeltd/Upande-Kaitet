import frappe

@frappe.whitelist()
def create_farm_pack_list_entry(bunch_label_data, box_label_data, farm):
    try:
        parsed_box_data = frappe.parse_json(box_label_data)
        order_id = parsed_box_data.get("order_id")
        stock_entry_id = get_stock_entry_id_from_url(bunch_label_data)
        
        order_pick_list = frappe.get_doc("Order Pick List", order_id)
        stock_entry = frappe.get_doc("Stock Entry", stock_entry_id)

        source_warehouse = f"{farm} Dispatch Cold Store - TL"
        
        item_code = stock_entry.items[0].item_code
        uom = stock_entry.items[0].uom

        # Quantity scanned should always be 1 
        quantity = 1
        customer_id = order_pick_list.customer
        sales_order_id = order_pick_list.sales_order
        box_id = parsed_box_data.get("box_id")

        pack_list_doc = frappe.new_doc("Farm Pack List")
        pack_list_doc.custom_farm = farm 
        pack_list_doc.append("pack_list_item", {
            "item_code": item_code,
            "bunch_uom": uom,
            "bunch_qty": quantity,
            "source_warehouse": source_warehouse,
            "sales_order_id": sales_order_id,
            "customer_id": customer_id,
            "box_id": box_id,
        })
        
        pack_list_doc.insert()

        return {
            "message": "Farm Pack List entry created successfully!",
            "docname": pack_list_doc.name
        }

    except Exception as e:
        frappe.throw(f"Error saving Farm Pack List: {str(e)}")


def get_stock_entry_id_from_url(stock_entry_url):
    stock_entry_url_arr = stock_entry_url.split("/")
    return stock_entry_url_arr[-1]
