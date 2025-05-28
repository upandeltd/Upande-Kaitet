import frappe
from frappe.utils import flt
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals


class CustomTaxesAndTotals(calculate_taxes_and_totals):
    def calculate_item_values(self):
        """Override only the amount calculation to use stock_qty instead of qty"""
        frappe.logger().info("CustomTaxesAndTotals: calculate_item_values() is being executed")
        print("DEBUG: CustomTaxesAndTotals - calculate_item_values() called")  # Check logs & console

        if self.doc.get("is_consolidated"):
            frappe.logger().info("CustomTaxesAndTotals: Document is consolidated, skipping calculations")
            print("DEBUG: Document is consolidated, skipping calculations")
            return

        if not self.discount_amount_applied:
            for item in self.doc.items:
                frappe.logger().info(f"Processing item: {item.item_code}")
                print(f"DEBUG: Processing item: {item.item_code}")

                self.doc.round_floats_in(item)

                if item.discount_percentage == 100:
                    item.rate = 0.0
                    frappe.logger().info(f"Item {item.item_code}: 100% discount applied, rate set to 0")
                    print(f"DEBUG: Item {item.item_code} - 100% discount applied")

                elif item.price_list_rate:
                    if not item.rate or (item.pricing_rules and item.discount_percentage > 0):
                        item.rate = flt(
                            item.price_list_rate * (1.0 - (item.discount_percentage / 100.0)),
                            item.precision("rate"),
                        )
                        item.discount_amount = item.price_list_rate * (item.discount_percentage / 100.0)

                    elif item.discount_amount and item.pricing_rules:
                        item.rate = item.price_list_rate - item.discount_amount

                if item.doctype in [
                    "Quotation Item",
                    "Sales Order Item",
                    "Delivery Note Item",
                    "Sales Invoice Item",
                ]:
                    item.rate_with_margin, item.base_rate_with_margin = self.calculate_margin(item)
                    if flt(item.rate_with_margin) > 0:
                        item.rate = flt(
                            item.rate_with_margin * (1.0 - (item.discount_percentage / 100.0)),
                            item.precision("rate"),
                        )

                        if item.discount_amount and not item.discount_percentage:
                            item.rate = item.rate_with_margin - item.discount_amount
                        else:
                            item.discount_amount = item.rate_with_margin - item.rate

                    elif flt(item.price_list_rate) > 0:
                        item.discount_amount = item.price_list_rate - item.rate
                elif flt(item.price_list_rate) > 0 and not item.discount_amount:
                    item.discount_amount = item.price_list_rate - item.rate

                item.net_rate = item.rate

                # Overridden calculation: Use `stock_qty` instead of `qty`
                frappe.logger().info(f"Item {item.item_code}: Calculating amount using stock_qty")
                print(f"DEBUG: Item {item.item_code} - Overriding calculation with stock_qty")

                item.amount = flt(item.rate * item.stock_qty, item.precision("amount"))
                item.net_amount = item.amount

                self._set_in_company_currency(
                    item, ["price_list_rate", "rate", "net_rate", "amount", "net_amount"]
                )

                item.item_tax_amount = 0.0

        frappe.logger().info("CustomTaxesAndTotals: Completed calculations for all items")
        print("DEBUG: Completed calculations for all items")
