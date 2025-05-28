// item-group_price.js
// Copyright (c) 2025, Upande Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Group Price", {
    setup(frm) {
        frm.set_query("item_group", function () {
            return {
                filters: {
                    is_group: 0
                }
            };
        });

        frm.set_query("length", function () {
            return {}; 
        });
    },

    onload(frm) {
        // Fetch currency and company details
        frm.add_fetch("default_currency", "currency");

        frm.set_df_property(
            "bulk_import_help",
            "options",
            '<a href="/app/data-import-tool/Item Group Price">' + __("Import in Bulk") + "</a>"
        );

        // Hide fields by default until a price list is selected
        frm.set_df_property("buying", "hidden", true);
        frm.set_df_property("selling", "hidden", true);
        frm.set_df_property("supplier", "hidden", true);
        frm.set_df_property("customer", "hidden", true);
        frm.set_df_property("currency", "hidden", true);
    },

    price_list(frm) {
        // Show or hide fields based on the selected price list
        if (frm.doc.price_list) {
            frappe.db.get_doc("Price List", frm.doc.price_list)
                .then(price_list => {
                    frm.set_df_property("buying", "hidden", !price_list.buying);
                    frm.set_df_property("selling", "hidden", !price_list.selling);
                    frm.set_df_property("supplier", "hidden", !price_list.buying);
                    frm.set_df_property("customer", "hidden", !price_list.selling);
                    frm.set_df_property("currency", "hidden", false);

                    // Set field values based on price list
                    frm.set_value("buying", price_list.buying);
                    frm.set_value("selling", price_list.selling);
                    frm.set_value("currency", price_list.currency || "");
                });
        } else {
            // Hide all fields again if no price list is selected
            frm.set_df_property("buying", "hidden", true);
            frm.set_df_property("selling", "hidden", true);
            frm.set_df_property("supplier", "hidden", true);
            frm.set_df_property("customer", "hidden", true);
            frm.set_df_property("currency", "hidden", true);
        }
    },
});
