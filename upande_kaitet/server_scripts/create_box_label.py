import os

import frappe
import qrcode
from frappe.utils import get_site_path


def create_box_label(doc, method):
	pack_list_items = doc.pack_list_item
	sales_order_id = doc.custom_sales_order

	# Get the farm from the item table of the fpl
	farm_warehouse = pack_list_items[0].source_warehouse
	farm = farm_warehouse.split()[0]

	opl = frappe.db.sql(
		"""
        SELECT p.name
        FROM `tabOrder Pick List` p
        JOIN `tabPick List Item` i ON i.parent = p.name
        WHERE p.sales_order = %s
        AND i.warehouse = %s
        AND i.idx = 1
        LIMIT 1
    """,
		(sales_order_id, f"{farm} Available for Sale - KR"),
		as_dict=1,
	)

	sales_order_doc = frappe.get_doc("Sales Order", sales_order_id)

	if opl:
		opl_doc = frappe.get_doc("Order Pick List", opl[0].name)

		for _item in pack_list_items:
			# Check if a box label doc matching the opl used exists,
			existing_labels = frappe.get_list("Box Label", filters={"order_pick_list": opl_doc.name})

			if not existing_labels:
				total_stems = 0
				box_1_items = []

				for row in pack_list_items:
					if row.box_id == "1":
						box_1_items.append(
							{
								"item_code": row.item_code,
								"bunch_uom": row.bunch_uom,
								"bunch_qty": row.bunch_qty,
							}
						)
						total_stems = total_stems + row.custom_number_of_stems

				new_label = frappe.new_doc("Box Label")

				new_label.customer = doc.custom_customer
				new_label.box_number = 1
				new_label.order_pick_list = opl_doc.name
				new_label.pack_rate = total_stems
				new_label.date = opl_doc.date_created
				new_label.customer_purchase_order = sales_order_doc.po_no
				new_label.consignee = sales_order_doc.custom_consignee
				new_label.truck_details = sales_order_doc.custom_truck_details
				new_label.farm_pack_list_link = doc.name
				new_label.length = pack_list_items[0].stem_length

				new_label.insert()

				qr_code_data = new_label.name  # Now the name is available
				qr_code = qrcode.make(qr_code_data)

				# Save the QR code as an image
				file_path = get_site_path("public", "files", f"{new_label.name}_qrcode.png")
				qr_code.save(file_path)

				if os.path.exists(file_path):
					file = frappe.get_doc(
						{
							"doctype": "File",
							"file_name": f"{new_label.name}_qrcode.png",
							"attached_to_doctype": "Box Label",
							"attached_to_name": new_label.name,
							"file_url": f"/files/{new_label.name}_qrcode.png",
						}
					)
					file.save()

				for fpl_item in box_1_items:
					new_label.append(
						"box_item",
						{
							"variety": fpl_item["item_code"],
							"uom": fpl_item["bunch_uom"],
							"qty": fpl_item["bunch_qty"],
						},
					)

					new_label.qr_code = file.file_url

				new_label.save()

				file = frappe.get_doc(
					{
						"doctype": "File",
						"file_name": f"{new_label.name}_qrcode.png",
						"attached_to_doctype": "Box Label",
						"attached_to_name": new_label.name,
						"file_url": f"/files/{new_label.name}_qrcode.png",
					}
				)
				file.save()

				new_label.save()

			if existing_labels:
				# Check the number of box labels existing
				# Create the next box label (box number = number of existing box labels + 1 )
				# Filter that box number items in the fpl just like the box_1_items
				# Next add the details just like box_1 was added.
				# If there is no next box label, stop
				existing_box_count = len(existing_labels)
				box_number = existing_box_count + 1

				total_stems = 0
				box_items = []

				for row in pack_list_items:
					if row.box_id == f"{box_number}":
						box_items.append(
							{
								"item_code": row.item_code,
								"bunch_uom": row.bunch_uom,
								"bunch_qty": row.bunch_qty,
							}
						)
						total_stems = total_stems + row.custom_number_of_stems

				if len(box_items) > 0:
					new_label = frappe.new_doc("Box Label")

					new_label.customer = doc.custom_customer
					new_label.box_number = box_number
					new_label.order_pick_list = opl_doc.name
					new_label.pack_rate = total_stems
					new_label.date = opl_doc.date_created
					new_label.customer_purchase_order = sales_order_doc.po_no
					new_label.consignee = sales_order_doc.custom_consignee
					new_label.truck_details = sales_order_doc.custom_truck_details
					new_label.farm_pack_list_link = doc.name
					new_label.length = pack_list_items[0].stem_length

					for fpl_item in box_items:
						new_label.append(
							"box_item",
							{
								"variety": fpl_item["item_code"],
								"uom": fpl_item["bunch_uom"],
								"qty": fpl_item["bunch_qty"],
							},
						)

					# Save the new box label
					new_label.insert()
