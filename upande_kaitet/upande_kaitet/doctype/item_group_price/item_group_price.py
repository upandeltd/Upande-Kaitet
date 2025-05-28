# Copyright (c) 2025, Upande Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _, bold
from frappe.model.document import Document
from frappe.query_builder import Criterion
from frappe.query_builder.functions import Cast_

class ItemGroupPriceDuplicateItem(frappe.ValidationError):
    pass

class ItemGroupPrice(Document):
    def validate(self):
        self.validate_price_list_details()
        self.check_duplicates()
        
    def validate_price_list_details(self):
        if self.price_list:
            price_list_details = frappe.db.get_value(
                "Price List", {"name": self.price_list, "enabled": 1}, ["buying", "selling", "currency"]
            )
            
            if not price_list_details:
                link = frappe.utils.get_link_to_form("Price List", self.price_list)
                frappe.throw(f"The price list {link} does not exist or is disabled")

            self.buying, self.selling, self.currency = price_list_details

    def check_duplicates(self):
        item_group_price = frappe.qb.DocType("Item Group Price")

        query = (
            frappe.qb.from_(item_group_price)
            .select(item_group_price.price_list_rate)
            .where(
                (item_group_price.item_group == self.item_group)
                & (item_group_price.price_list == self.price_list)
                & (item_group_price.length == self.length)
                & (item_group_price.name != self.name)
            )
        )
        
        # Optional field checks
        optional_fields = ["customer", "supplier", "valid_from", "valid_upto"]
        
        for field in optional_fields:
            if self.get(field):
                query = query.where(item_group_price[field] == self.get(field))
            else:
                query = query.where(
                    Criterion.any([
                        item_group_price[field].isnull(),
                        Cast_(item_group_price[field], "varchar") == ""
                    ])
                )

        price_list_rate = query.run(as_dict=True)

        if price_list_rate:
            frappe.throw(
                _(
                    "Item Group Price appears multiple times based on Price List, Item Group, Length, and other criteria."
                ),
                ItemGroupPriceDuplicateItem,
            )

    def before_save(self):
        if self.selling:
            self.reference = self.customer
        if self.buying:
            self.reference = self.supplier

        if self.selling and not self.buying:
            # if only selling then remove supplier
            self.supplier = None
        if self.buying and not self.selling:
            # if only buying then remove customer
            self.customer = None
