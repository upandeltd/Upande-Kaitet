import frappe
from frappe.utils import now, nowdate, nowtime


@frappe.whitelist()
def create_dnote(vehicle, box_name, farm):
	try:
		box_doc = frappe.get_doc("Box Label", box_name)
		farm_doc = frappe.get_doc("Farm", farm)
		fpl_doc = frappe.get_doc("Farm Pack List", box_doc.farm_pack_list_link)

		so_items = frappe.db.get_all(
			"Sales Order Item",
			filters={"parent": fpl_doc.custom_sales_order},
			fields=["item_code", "uom", "qty", "rate", "warehouse"],
		)

		warehouse = ""

		if farm == "Karen":
			warehouse = "Karen Graded Sold - KR"
		else:
			warehouse = "Ravine Graded Sold - KR"

		dnote = frappe.new_doc("Delivery Note")
		dnote.customer = box_doc.customer
		dnote.custom_farm = farm
		# By default box label is used for roses
		dnote.custom_business_unit = "Roses"
		dnote.custom_location = farm_doc.custom_location
		dnote.custom_delivery_type = "Roses Dispatch"
		dnote.custom_departing_vehicle = vehicle
		dnote.custom_departing_time = now()
		dnote.company = "Karen Roses"

		so_items_lookup = {}
		for so_item in so_items:
			key = f"{so_item.item_code}_{so_item.uom}_{so_item.qty}"
			so_items_lookup[key] = {
				"rate": so_item.rate,
				# 'warehouse': so_item.
			}

		for item in box_doc.box_item:
			lookup_key = f"{item.variety}_{item.uom}_{item.qty}"

			rate = 0.0

			if lookup_key in so_items_lookup:
				rate = so_items_lookup[lookup_key]["rate"]
			else:
				frappe.log_error(
					f"No matching SO item found for {lookup_key} in {fpl_doc.custom_sales_order}"
				)

			dnote.append(
				"items",
				{
					"item_code": item.variety,
					"item_name": item.variety,
					"custom_box_name": box_name,
					"uom": item.uom,
					"qty": item.qty,
					"custom_length": box_doc.length,
					"rate": rate,
					"warehouse": warehouse,
				},
			)

		dnote.insert()

	except Exception as e:
		frappe.log_error(f"Error creating delivery note: {e!s}")
