import frappe
from frappe import _
from erpnext.stock.doctype.item_price.item_price import ItemPrice

def custom_check_duplicates(self, *args, **kwargs):
    filters = {
        "item_code": self.item_code,
        "price_list": self.price_list,
        "currency": self.currency,
        "selling": self.selling,
        "buying": self.buying,
        "uom": self.uom,
        "length": self.length, 
    }

    if self.name:
        filters["name"] = ["!=", self.name]

    duplicate = frappe.db.exists("Item Price", filters)

    if duplicate:
        frappe.throw(
            _("Item Price appears multiple times for this combination of Item, Price List, Currency, UOM, Qty, and Length."),
            exc=ItemPrice.ItemPriceDuplicateItem,
        )


ItemPrice.check_duplicates = custom_check_duplicates
