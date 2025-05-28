
import frappe

@frappe.whitelist()
def save_farm_pack_list(farm_pack_list_id, customerId, item_code, uom, quantity, source_warehouse, box_id):
    pack_list_doc = frappe.get_doc("Farm Pack List", farm_pack_list_id)

    pack_list_row = pack_list_doc.add_child({
        "item_code": item_code,
        "uom": uom,
        "qty": quantity,
        "source_warehouse": source_warehouse,
        "box_id": box_id,
        "customer_id": customerId 
    })

    frappe.throw(pack_list_row.item_code)

    pack_list_row.save()

    frappe.db.commit()

    pack_list_row.reload()

    return {"success": True, "message": "Farm Pack List updated successfully!"}
