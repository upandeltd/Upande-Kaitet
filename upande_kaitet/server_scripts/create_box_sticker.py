import frappe

import frappe.utils

@frappe.whitelist()
def create_box_sticker(variety, uom, customer, length, box_number, customer_purchase_order, order_pick_list, truck_details, consignee):
    date = frappe.utils.today()

    boxStickerDoc = frappe.new_doc("Box Label")

    boxStickerDoc.customer = customer
    boxStickerDoc.length = length
    boxStickerDoc.box_number = box_number
    boxStickerDoc.date = date
    boxStickerDoc.customer_purchase_order = customer_purchase_order
    boxStickerDoc.order_pick_list = order_pick_list
    boxStickerDoc.truck_details = truck_details
    boxStickerDoc.consignee = consignee
    packrate = 0

    # One bunch per scan
    quantity = 1

    boxStickerDoc.append("box_item", {
        "variety": variety,
        "qty": quantity,
        "uom": uom,
    })

    uom_conversion_factor = {
        "Bunch (5)": 5,
        "Bunch (6)": 6,
        "Bunch (10)": 10,
        "Bunch (12)": 12,
        "Bunch (25)": 25
    }

    packrate = uom_conversion_factor.get(uom) * int(quantity)

    boxStickerDoc.pack_rate = packrate

    boxStickerDoc.insert()

    return {
        "docname": boxStickerDoc.name
    }


