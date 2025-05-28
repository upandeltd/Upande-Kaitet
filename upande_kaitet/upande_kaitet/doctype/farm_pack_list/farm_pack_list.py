import frappe
from frappe import _
from frappe.model.document import Document


class FarmPackList(Document):

    def validate(self):
        # """Hook to check workflow state changes + Completion Check"""
        # # Completion check
        # packed_stems = self.custom_total_stems or 0
        # required_stems = self.custom_picked_total_stems or 0
        # completion_percentage = 0

        # if required_stems > 0:
        #     completion_percentage = (packed_stems / required_stems) * 100
        #     self.custom_completion_percentage = completion_percentage

        # if completion_percentage < 100:
        #     message = f"""
        #         <b>You cannot approve this Farm Pack List because it is incomplete.</b><br><br>
        #         Packed Stems: <b>{packed_stems}</b><br>
        #         Required Stems (from Order Pick List): <b>{required_stems}</b><br>
        #         Completion: <b>{round(completion_percentage, 2)}%</b><br><br>
        #         Please ensure all required stems are packed before approval.
        #         """
        #     frappe.throw(message)
        # elif completion_percentage > 100:
        #     frappe.throw("you have over packed!")

        # Workflow trigger
        if self.workflow_state == "Reviewed" and not self.is_new():
            transfer_stock_on_submit(self)
            process_consolidated_pack_list(self.name)

    def on_cancel(self):
        transfer_stock_on_cancel(self)


@frappe.whitelist()
def transfer_stock_on_submit(doc):
    """Transfers stock when Farm Pack List workflow state is Reviewed"""

    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    source_warehouses = [
        "Burguret Graded Sold - TL", "Turaco Graded Sold - TL",
        "Pendekeza Graded Sold - TL"
    ]

    source_warehouse = None
    for item in doc.pack_list_item:
        if item.source_warehouse in source_warehouses:
            source_warehouse = item.source_warehouse
            break

    if not source_warehouse:
        frappe.throw(
            "Invalid or missing source warehouse. Allowed warehouses: " +
            ", ".join(source_warehouses))

    target_warehouse = "Delivery Truck - TL"

    if not frappe.db.exists("Warehouse", source_warehouse):
        frappe.throw(f"Source Warehouse '{source_warehouse}' does not exist.")

    if not frappe.db.exists("Warehouse", target_warehouse):
        frappe.throw(f"Target Warehouse '{target_warehouse}' does not exist.")

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.farm_pack_list = doc.name

    for item in doc.pack_list_item:
        stock_entry.append(
            "items", {
                "s_warehouse": source_warehouse,
                "t_warehouse": target_warehouse,
                "item_code": item.item_code,
                "qty": item.bunch_qty,
                "uom": item.bunch_uom,
                "stock_uom": item.bunch_uom,
            })

    stock_entry.save(ignore_permissions=True)
    stock_entry.submit()

    frappe.msgprint(
        f"Stock Transfer Created from {source_warehouse} to {target_warehouse} Successfully!",
        alert=True,
        indicator="green",
        wide=True,
    )


@frappe.whitelist()
def transfer_stock_on_cancel(doc):
    """Transfers stock from Delivery Truck back to source warehouse when Farm Pack List is cancelled."""

    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    target_warehouses = [
        "Burguret Graded Sold - TL", "Turaco Graded Sold - TL",
        "Pendekeza Graded Sold - TL"
    ]

    source_warehouse = "Delivery Truck - TL"

    if not frappe.db.exists("Warehouse", source_warehouse):
        frappe.throw(f"Source Warehouse '{source_warehouse}' does not exist.")

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.farm_pack_list = doc.name

    for item in doc.pack_list_item:
        target_warehouse = item.source_warehouse

        # Validate if target warehouse is one of the allowed warehouses
        if target_warehouse not in target_warehouses:
            frappe.throw(
                f"Invalid target warehouse '{target_warehouse}'. Expected: " +
                ", ".join(target_warehouses))

        if not frappe.db.exists("Warehouse", target_warehouse):
            frappe.throw(
                f"Target Warehouse '{target_warehouse}' does not exist.")

        # Add items to the Stock Entry
        stock_entry.append(
            "items", {
                "s_warehouse": source_warehouse,
                "t_warehouse": target_warehouse,
                "item_code": item.item_code,
                "qty": item.bunch_qty,
                "uom": item.bunch_uom,
                "stock_uom": item.bunch_uom,
            })

    stock_entry.save(ignore_permissions=True)
    stock_entry.submit()

    frappe.msgprint(
        f"Stock Transfer Created from {source_warehouse} to {target_warehouse} Successfully!",
        alert=True,
        indicator="red",
        wide=True,
    )


@frappe.whitelist()
def process_consolidated_pack_list(farm_pack_list, sales_order_id=None):
    """Creates or updates Consolidated Pack List when Farm Pack List workflow status is Reviewed"""

    if not frappe.has_permission("Farm Pack List", "read"):
        frappe.throw("Not permitted to read Farm Pack List")
    if not frappe.has_permission("Consolidated Pack List", "write"):
        frappe.throw("Not permitted to create/modify Consolidated Pack List")

    farm_pack_doc = frappe.get_doc("Farm Pack List", farm_pack_list)

    # Fetch sales_order_id from the first Pack List Item if not provided
    if not sales_order_id and farm_pack_doc.pack_list_item:
        sales_order_id = farm_pack_doc.pack_list_item[0].sales_order_id

    if not sales_order_id:
        frappe.throw("Sales Order ID is required to process the CPL.")

    # Check for an existing Consolidated Pack List (CPL)
    existing_cpl = frappe.get_all("Consolidated Pack List",
                                  filters={"sales_order_id": sales_order_id},
                                  fields=["name"],
                                  limit=1)

    # Fetch Box Labels from Sales Order Items
    box_labels = frappe.get_all("Sales Order Item",
                                filters={"parent": sales_order_id},
                                fields=["item_code", "custom_box_label"])

    # Create a mapping of item_code to box label for quick lookup
    box_label_mapping = {
        item["item_code"]: item["custom_box_label"]
        for item in box_labels if item["custom_box_label"]
    }

    try:
        if existing_cpl:
            cpl = frappe.get_doc("Consolidated Pack List",
                                 existing_cpl[0]["name"])
            if not cpl.has_permission("write"):
                frappe.throw("Not permitted to modify this CPL")
            message = f"Farm Pack List updated CPL: {cpl.name}"
        else:
            cpl = frappe.new_doc("Consolidated Pack List")
            cpl.sales_order_id = sales_order_id
            cpl.customer_id = farm_pack_doc.pack_list_item[0].customer_id
            message = "New CPL is created in draft status"

        # **Fetch required fields from Farm Pack List**
        cpl.custom_customer = farm_pack_doc.custom_customer
        cpl.custom_currency = farm_pack_doc.custom_currency
        cpl.custom_customer_address = farm_pack_doc.custom_customer_address
        #cpl.custom_sales_order = farm_pack_doc.custom_sales_order

        if "items" not in cpl.as_dict():
            frappe.throw("Field 'items' does not exist in CPL")

        # Store existing items for total stems calculation
        total_stems = sum(item.custom_number_of_stems for item in cpl.items)

        for item in farm_pack_doc.pack_list_item:
            # Get the Box Label from Sales Order based on item_code
            box_label = box_label_mapping.get(item.item_code,
                                              item.custom_box_label)

            cpl.append(
                "items", {
                    "source_warehouse": "Delivery Truck - TL",
                    "customer_id": item.customer_id,
                    "sales_order_id": item.sales_order_id,
                    "box_id": item.box_id,
                    "item_code": item.item_code,
                    "bunch_uom": item.bunch_uom,
                    "bunch_qty": item.bunch_qty,
                    "stem_length": item.stem_length,
                    "consolidated_pack_list_id":
                    item.consolidated_pack_list_id,
                    "custom_number_of_stems": item.custom_number_of_stems,
                    "custom_box_label": box_label
                })

            # Update total stems count
            total_stems += item.custom_number_of_stems

        # Update total stems in CPL
        cpl.custom_total_stems = total_stems

        cpl.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.msgprint(
            message,
            alert=True,
            indicator="green",
            wide=True,
        )

        return cpl.name

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(f"Error processing CPL: {str(e)}")


@frappe.whitelist()
def close_farm_pack_list(farm_pack_list):
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to close Farm Pack List"))

    doc = frappe.get_doc("Farm Pack List", farm_pack_list)
    if doc.custom_status == "Closed":
        frappe.throw(_("Farm Pack List is already closed"))

    doc.db_set('custom_status', 'Closed', update_modified=False)
