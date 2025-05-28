frappe.ui.form.on('Sales Order Item', {
    custom_source_warehouse: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let warehouse_mapping = {
            "Turaco Graded General - TL": "Turaco Graded Sold - TL",
            "Pendekeza Graded General - TL": "Pendekeza Graded Sold - TL",
            "Burguret Graded General - TL": "Burguret Graded Sold - TL"
        };

        if (row.custom_source_warehouse) {
            let mapped_warehouse = warehouse_mapping[row.custom_source_warehouse] || "";
            frappe.model.set_value(cdt, cdn, "warehouse", mapped_warehouse);
        }
    }
});
