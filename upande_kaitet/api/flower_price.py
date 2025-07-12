import frappe
from upande_kaitet.api.item_length_price import get_length_price 

@frappe.whitelist(allow_guest=True)
def get_price_for_shopify(item_code, length, price_list="USD", currency="USD"):
    price_list_map = {
        "USD": "USD Price List",
    }
    
    price_list = price_list_map.get(price_list, price_list)

    price = get_length_price(
        item_name=item_code,
        length=length,
        currency=currency,
        price_list=price_list
    )

    if not price:
        frappe.throw("No price found for the selected item and length in this price list.")

    return {
        "price": price
    }
