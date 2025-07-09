import frappe

@frappe.whitelist()
def get_length_price(item_name, length, currency):
    filters = {
        "item_name": item_name,
        "length": length,
        "currency": currency
    }

    match = frappe.get_all(
        "Item Price",
        filters=filters,
        fields=["price_list_rate"],
        limit_page_length=1
    )

    if match:
        return match[0]["price_list_rate"]
    else:
        frappe.msgprint(f"No matching price found for item{ item_name}, length {length}, and currency {currency}. defaulting to 0.")
        return 0
