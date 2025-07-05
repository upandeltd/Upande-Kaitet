import frappe
from datetime import datetime, timedelta

@frappe.whitelist()
def transfer_holding_to_cold_store():
    """
    Transfer all harvesting entries from holding store to cold store
    Runs at midnight for entries from the last 24 hours
    """
    try:
        # Calculate 24 hours ago from now
        now = datetime.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        # Get all stock entries from the last 24 hours that need transfer
        stock_entries = frappe.db.sql("""
            SELECT DISTINCT 
                se.name,
                se.custom_farm,
                sed.t_warehouse as current_warehouse,
                sed.item_code,
                sed.qty,
                sed.s_warehouse,
                sed.uom,
            FROM `tabStock Entry` se
            INNER JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
            WHERE se.stock_entry_type IN ('Receiving', 'Receiving Quarantined')
            AND se.creation >= %s
            AND sed.t_warehouse LIKE %s
            AND se.docstatus = 1
        """, (twenty_four_hours_ago, '%Holding Store - KR'), as_dict=True)
        
        if not stock_entries:
            frappe.log_error("No entries found for midnight transfer", "Midnight Transfer Job")
            return
            
        # Group entries by farm for processing
        farms_data = {}
        for entry in stock_entries:
            farm = entry.custom_farm
            if farm not in farms_data:
                farms_data[farm] = []
            farms_data[farm].append(entry)
        
        # Process each farm's entries
        for farm, entries in farms_data.items():
            create_transfer_entry(farm, entries)
            
        frappe.db.commit()
        frappe.log_error(f"Successfully processed midnight transfer for {len(farms_data)} farms", "Midnight Transfer Job")
        
    except Exception as e:
        frappe.log_error(f"Error in midnight transfer: {str(e)}", "Midnight Transfer Job Error")
        frappe.db.rollback()

def create_transfer_entry(farm, entries):
    """
    Create a material transfer entry from holding store to cold store
    """
    try:
        # Get company from farm
        farm_doc = frappe.get_doc("Farm", farm)
        company = farm_doc.company
        
        # Create new Stock Entry for transfer
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Midnight Material Transfer"
        stock_entry.company = company
        stock_entry.custom_farm = farm
        stock_entry.custom_business_unit = "Roses"
        stock_entry.posting_date = frappe.utils.today()
        stock_entry.posting_time = frappe.utils.nowtime()
        
        # Add items to transfer
        for entry in entries:
            source_warehouse = f"{farm} Holding Store - KR"
            target_warehouse = f"{farm} Receiving Cold Store - KR"
            
            stock_entry.append("items", {
                "item_code": entry.item_code,
                "qty": entry.qty,
                "s_warehouse": source_warehouse,
                "t_warehouse": target_warehouse,
                "transfer_qty": entry.qty
            })
        
        # Save and submit the transfer entry
        stock_entry.save()
        stock_entry.submit()
        
        frappe.log_error(f"Created transfer entry {stock_entry.name} for farm {farm}", "Midnight Transfer Success")
        
    except Exception as e:
        frappe.log_error(f"Error creating transfer for farm {farm}: {str(e)}", "Midnight Transfer Farm Error")
