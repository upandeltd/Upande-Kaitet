import frappe
from upande_kaitet.api.item_length_price import get_length_price 

@frappe.whitelist(allow_guest=True)
def get_price_for_shopify(item_code, length, price_list="EUR", currency="EUR"):
    # Handle CORS
    frappe.local.response["Access-Control-Allow-Origin"] = "https://karen-roses.myshopify.com"
    frappe.local.response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    frappe.local.response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"


    if not item_code or not length:
        frappe.local.response.http_status_code = 400
        return {"error": "Missing item_code or length"}
    
    price_list_map = {
        "EUR": "EUR Price List",
    }
    
    price_list = price_list_map.get(price_list, price_list)
    try:

        price = get_length_price(
            item_name=item_code,
            length=length,
            currency=currency,
            price_list=price_list
        )

        if not price:
            frappe.local.response.http_status_code = 404
            return {"error": "No price found for the selected item and length"}
        
        frappe.local.response.http_status_code = 200

        return {
            "price": price
        }
        
    except Exception as e:
        frappe.local.response.http_status_code = 500
        return {"error": f"An error occurred while fetching the price: {str(e)}"}
