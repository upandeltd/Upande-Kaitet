import json
import frappe

@frappe.whitelist()
def create_stock_entry(stock_entry_data):
    stock_entry_data = json.loads(stock_entry_data)

    stock_entry = frappe.new_doc("Stock Entry")

    stock_entry_type = stock_entry_data.get("stock entry type")
    variety = stock_entry_data.get("variety")
    quantity = stock_entry_data.get("quantity")
    grower = stock_entry_data.get("grower")
    location_data = stock_entry_data.get("location data")
    uom = stock_entry_data.get("uom")
    harvester = stock_entry_data.get("harvester")
    greenhouse = stock_entry_data.get("greenhouse")
    block__bed_number = stock_entry_data.get("block__bed_number")
    bucket_id = stock_entry_data.get("bucket_id")
 
    stock_entry.stock_entry_type = stock_entry_type 

    stock_entry.custom_greenhouse = greenhouse
    stock_entry.custom_harvester = harvester
    stock_entry.custom_grower = grower
    stock_entry.custom_block__bed_number = block__bed_number
    stock_entry.custom_received_bucket_id = bucket_id

    stock_entry.append("items", {
        "item_code": variety,
        "qty": quantity,
        "s_warehouse": location_data["source"],
        "t_warehouse": location_data["target"],
        "uom": uom
    })
    
    stock_entry.insert()
    
    # Submit the stock entry
    stock_entry.submit()
    print(f'stock entry object: {stock_entry.name}')

    response_data = {
        "name": stock_entry.name
    }

    return json.dumps(response_data)
