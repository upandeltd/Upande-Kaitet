import frappe


@frappe.whitelist()
def gen_spec_items_for_so(specification, bunches_quantity, target_wh):
	spec_doc = frappe.get_doc("Specifications", specification)
	items = []

	# Create items for each variety/color specified
	if spec_doc.varieties_in_bunch:
		for variety in spec_doc.varieties_in_bunch:
			items.append(
				{
					"item_code": variety.variety,
					"qty": variety.total_stems * int(bunches_quantity),
					"rate": frappe.get_value("Item", variety.variety, "standard_rate") or 0,
					"description": f"As per specification {specification}",
					"custom_length": spec_doc.stem_length,
					"target_warehouse": target_wh,
				}
			)

	return items
