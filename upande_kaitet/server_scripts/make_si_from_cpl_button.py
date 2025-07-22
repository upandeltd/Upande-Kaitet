import frappe
from erpnext.accounts.party import get_party_account
from erpnext.selling.doctype.sales_order.sales_order import get_item_defaults, get_item_group_defaults
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, today


@frappe.whitelist()
def make_sales_invoice_from_pack_list(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		target.flags.ignore_permissions = True
		target.custom_consolidated_packlist = source.name
		target.update_stock = 0
		target.custom_business_unit = "Roses"

		if source.pack_list_item:
			target.set_warehouse = source.pack_list_item[0].source_warehouse

		# Get first linked Sales Order from items
		sales_orders = list({item.sales_order_id for item in source.pack_list_item if item.sales_order_id})
		if sales_orders:
			so = frappe.get_doc("Sales Order", sales_orders[0])
			target.taxes_and_charges = so.taxes_and_charges
			target.taxes = so.taxes
			target.customer = so.customer
			target.custom_shipping_agent = so.custom_shipping_agent
			target.custom_destination = so.custom_delivery_point
			target.custom_consignee = so.custom_consignee
			target.custom_comment = so.custom_comment
			target.debit_to = get_party_account("Customer", so.customer, so.company)

		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		if not source.sales_order_id:
			frappe.throw(f"Missing Sales Order for item {source.item_code} in {source_parent.name}")

		so = frappe.get_doc("Sales Order", source.sales_order_id)
		so_item = next((i for i in so.items if i.item_code == source.item_code), None)

		if not so_item:
			frappe.throw(f"Item {source.item_code} not found in Sales Order {source.sales_order_id}")

		target.qty = source.bunch_qty
		target.uom = source.bunch_uom
		target.rate = so_item.rate
		target.custom_number_of_stems = source.custom_number_of_stems
		target.custom_length = so_item.custom_length
		target.discount_percentage = so_item.discount_percentage
		target.so_detail = so_item.name
		target.sales_order = so.name

		# Set cost center
		if so.project:
			target.cost_center = frappe.db.get_value("Project", so.project, "cost_center")

		item_defaults = get_item_defaults(source.item_code, so.company)
		item_group_defaults = get_item_group_defaults(source.item_code, so.company)
		cost_center = item_defaults.get("selling_cost_center") or item_group_defaults.get(
			"selling_cost_center"
		)
		if cost_center:
			target.cost_center = cost_center

	doc = get_mapped_doc(
		"Farm Pack List",  # parent Doctype
		source_name,
		{
			"Farm Pack List": {
				"doctype": "Sales Invoice",
			},
			"Dispatch Form Item": {  # correct child table Doctype
				"doctype": "Sales Invoice Item",
				"field_map": {
					"item_code": "item_code",
				},
				"postprocess": update_item,
				"condition": lambda d: d.sales_order_id and d.bunch_qty > 0,
			},
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)

	return doc
