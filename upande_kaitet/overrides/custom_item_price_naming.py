import frappe
from erpnext.stock.doctype.item_price.item_price import ItemPrice as ERPNextItemPrice

class CustomItemPrice(ERPNextItemPrice):
    def autoname(self):
        frappe.log_error("Custom autoname triggered", "DEBUG Item Price")

        item = frappe.get_doc("Item", self.item_code)
        flower_groups = ["Standard Roses", "Spray Roses", "Fillers", "Chrysanthemums"]

        if item.item_group and item.item_group.strip() in flower_groups and self.custom_length:
            self.name = f"{self.item_code}-{self.currency}-{self.custom_length}"
        else:
            self.name = f"{self.item_code}"
