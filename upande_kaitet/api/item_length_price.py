import frappe
from frappe import _

@frappe.whitelist()
def get_length_price(item_name, length, currency, price_list):
    """
    Get item price based on length for flower items
    """
    try:
        # Log the input parameters for debugging
        frappe.log_error(f"get_length_price called with: item_name={item_name}, length={length}, currency={currency}, price_list={price_list}", "DEBUG Price Fetch")
        
        # Get the item document to check item group
        item = frappe.get_doc("Item", item_name)
        flower_groups = ["Standard Roses", "Spray Roses", "Fillers", "Chrysanthemums"]
        
        is_flower = item.item_group and item.item_group.strip() in flower_groups
        frappe.log_error(f"Item group: {item.item_group}, is_flower: {is_flower}, length: {length}", "DEBUG Price Fetch")
        
        # For flower items, only proceed if length is provided
        if is_flower and not length:
            frappe.log_error(f"Flower item {item_name} has no length specified, returning 0", "DEBUG Price Fetch")
            return 0
        
        if is_flower and length:
            # Strategy 1: Direct query using custom_length field
            price_records = frappe.db.get_all(
                "Item Price",
                filters={
                    "item_code": item_name,
                    "price_list": price_list,
                    "currency": currency,
                    "custom_length": length
                },
                fields=["name", "price_list_rate", "custom_length"]
            )
            
            frappe.log_error(f"Found {len(price_records)} records with custom_length filter", "DEBUG Price Fetch")
            
            if price_records:
                frappe.log_error(f"Found price with custom_length: {price_records[0].name} = {price_records[0].price_list_rate}", "DEBUG Price Fetch")
                return price_records[0].price_list_rate
            
            # Strategy 2: Try with expected naming format
            expected_name = f"{item_name}-{currency}-{length}"
            
            price_record = frappe.db.get_value(
                "Item Price",
                {
                    "name": expected_name,
                    "item_code": item_name,
                    "price_list": price_list,
                    "currency": currency
                },
                "price_list_rate"
            )
            
            if price_record:
                frappe.log_error(f"Found price with expected naming: {expected_name} = {price_record}", "DEBUG Price Fetch")
                return price_record
            
            # Strategy 3: Get all price records for this item and debug
            all_price_records = frappe.db.get_all(
                "Item Price",
                filters={
                    "item_code": item_name,
                    "price_list": price_list,
                    "currency": currency
                },
                fields=["name", "price_list_rate", "custom_length"]
            )
            
            frappe.log_error(
    title="Error in get_length_price",
    message=f"All price records for {item_name}: {frappe.as_json(records)}"
)

            
            # Check each record manually
            for record in all_price_records:
                frappe.log_error(f"Checking record: {record.name}, custom_length: '{record.custom_length}', looking for: '{length}'", "DEBUG Price Fetch")
                if str(record.custom_length) == str(length):
                    frappe.log_error(f"Found matching length: {record.name} = {record.price_list_rate}", "DEBUG Price Fetch")
                    return record.price_list_rate
        
        # For flower items, if no length is provided or no length-specific price found, return 0
        if is_flower:
            frappe.log_error(f"No length-specific price found for flower item: {item_name}", "DEBUG Price Fetch")
            return 0
        
        # Fallback: For non-flower items, try to get any price without length consideration
        price_record = frappe.db.get_value(
            "Item Price",
            {
                "item_code": item_name,
                "price_list": price_list,
                "currency": currency
            },
            "price_list_rate"
        )
        
        if price_record:
            frappe.log_error(f"Found fallback price for non-flower item: {price_record}", "DEBUG Price Fetch")
            return price_record
            
        frappe.log_error(f"No price found for item: {item_name}, length: {length}, currency: {currency}, price_list: {price_list}", "DEBUG Price Fetch")
        return None
        
    except Exception as e:
        frappe.log_error(f"Error in get_length_price: {str(e)}", "DEBUG Price Fetch Error")
        return None