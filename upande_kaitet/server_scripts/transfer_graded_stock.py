import frappe

@frappe.whitelist()
def transfer_stock(stock_entries):

    if isinstance(stock_entries, str):
        stock_entries = eval(stock_entries) 

    for entry in stock_entries:

        try:

            stock_entry = frappe.get_doc("Stock Entry", entry)
            farm_name = stock_entry.custom_farm
            
            from_warehouse = f"{farm_name} Graded General - TL"
            to_warehouse = f"{farm_name} Available for Sale - TL"
            
            new_stock_entry = frappe.new_doc("Stock Entry")
            new_stock_entry.stock_entry_type = "Material Transfer"
            
            new_stock_entry.from_warehouse = from_warehouse
            new_stock_entry.to_warehouse = to_warehouse
            
            for item in stock_entry.items:
                new_stock_entry.append("items", {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "s_warehouse": from_warehouse,
                    "t_warehouse": to_warehouse
                })
                
            new_stock_entry.save()
            new_stock_entry.submit()
            frappe.db.commit()
            frappe.response["message"] = "Graded stock transfered"

        except Exception as e:
            frappe.log_error(f"❌ Error processing Stock Entry {entry}: {str(e)}")
    