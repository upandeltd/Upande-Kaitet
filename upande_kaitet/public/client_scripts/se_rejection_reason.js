// Last last
frappe.ui.form.on('Stock Entry', {
    stock_entry_type: function(frm) {
        console.log("Stock Entry Type:", frm.doc.stock_entry_type);

        frm.fields_dict.items.grid.update_docfield_property(
            "custom_reason", "hidden", frm.doc.stock_entry_type !== "Field Rejects"
        );

        frm.fields_dict.items.grid.update_docfield_property(
            "custom_reason", "reqd", frm.doc.stock_entry_type === "Field Rejects"
        );

        frm.refresh_field("items");  
    }
});
