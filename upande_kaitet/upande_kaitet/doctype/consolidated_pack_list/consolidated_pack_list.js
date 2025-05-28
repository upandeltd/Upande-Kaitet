frappe.listview_settings["Consolidated Pack List"] = {
    onload: function (listview) {
        listview.page.add_inner_button("Create to Dispatch Form", function () {
            let selected_docs = listview.get_checked_items();

            if (!selected_docs.length) {
                frappe.msgprint(__("Please select at least one Consolidated Pack List"));
                return;
            }

            validate_and_process_cpls(selected_docs);
        });
    }
};

function validate_and_process_cpls(selected_docs) {
    let validation_promises = selected_docs.map(cpl => {
        return new Promise(resolve => {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Consolidated Pack List",
                    name: cpl.name,
                    fields: ["name", "custom_dispatched", "docstatus", "custom_dispatch_status", "workflow_state"]
                },
                callback: function (response) {
                    if (response.message) {
                        resolve({ 
                            is_dispatched: response.message.custom_dispatched, 
                            is_submitted: response.message.docstatus === 1,
                            workflow_state: response.message.workflow_state,
                            dispatch_status: response.message.custom_dispatch_status,
                            cpl_id: cpl.name 
                        });
                    } else {
                        resolve({ 
                            is_dispatched: false, 
                            is_submitted: false, 
                            workflow_state: "", 
                            dispatch_status: "",
                            cpl_id: cpl.name 
                        });
                    }
                }
            });
        });
    });

    Promise.all(validation_promises).then(results => {
        // Filter out CPLs that are already dispatched, submitted, or don't meet criteria
        let invalid_cpls = results.filter(result => 
            result.is_dispatched || 
            (result.workflow_state !== "Approved") || 
            (result.dispatch_status !== "Pending")
        );

        if (invalid_cpls.length > 0) {
            let cpl_list = invalid_cpls.map(cpl => cpl.cpl_id).join(", ");
            frappe.msgprint(__(`Cannot process these CPLs: ${cpl_list}. 
                CPLs must be in 'Approved' state with 'Pending' dispatch status.`));
            return;
        }

        process_bulk_cpl_assignment(selected_docs);
    });
}

function process_bulk_cpl_assignment(selected_docs) {
    let grouped_items = {};

    let fetch_cpl_data = selected_docs.map(cpl => {
        return new Promise(resolve => {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Consolidated Pack List",
                    name: cpl.name
                },
                callback: function (response) {
                    if (response.message) {
                        let cpl_doc = response.message;

                        if (cpl_doc.items && cpl_doc.items.length) {
                            cpl_doc.items.forEach(item => {
                                let key = `${item.item_group}_${cpl_doc.name}`;
                                if (!grouped_items[key]) {
                                    grouped_items[key] = [];
                                }
                                grouped_items[key].push({
                                    customer_id: item.customer_id,
                                    bunch_uom: item.bunch_uom,
                                    bunch_qty: item.bunch_qty,
                                    box_id: item.box_id,
                                    stem_length: item.stem_length,
                                    item_group: item.item_group,
                                    s_number: item.s_number,
                                    delivery_point: item.delivery_point,
                                    sales_order_id: item.sales_order_id || "N/A",
                                    consolidated_pack_list_id: cpl_doc.name,
                                    item_code: item.item_code,
                                    source_warehouse: item.source_warehouse,
                                    no_of_stems: item.no_of_stems || 0
                                });
                            });
                        }
                    }
                    resolve();
                }
            });
        });
    });

    Promise.all(fetch_cpl_data).then(() => {
        create_new_dispatch_form(selected_docs, grouped_items);
    });
}

function create_new_dispatch_form(selected_docs, grouped_items) {
    frappe.model.with_doctype("Dispatch Form", function () {
        let dispatch_form = frappe.model.get_new_doc("Dispatch Form");

        Object.keys(grouped_items).forEach(group_key => {
            let items = grouped_items[group_key];
            let new_row = frappe.model.add_child(dispatch_form, "dispatch_form_item");
            new_row.item_group = items[0].item_group;
            new_row.consolidated_pack_list_id = items[0].consolidated_pack_list_id;
            new_row.no_of_boxes = items.length;
            new_row.customer_id = items[0].customer_id;
            new_row.s_number = items[0].s_number;
            new_row.delivery_point = items[0].delivery_point;
            new_row.sales_order_id = items[0].sales_order_id;
        });

        Object.keys(grouped_items).forEach(group_key => {
            let items = grouped_items[group_key];
            items.forEach(item => {
                let new_row = frappe.model.add_child(dispatch_form, "custom_sku_summary");
                new_row.item_code = item.item_code;
                new_row.item_group = item.item_group;
                new_row.no_of_stems = item.no_of_stems;
                new_row.consolidated_pack_list_id = item.consolidated_pack_list_id;
                new_row.sales_order_id = item.sales_order_id;
                new_row.stem_length = item.stem_length;
                new_row.bunch_uom = item.bunch_uom;
                new_row.bunch_qty = item.bunch_qty;
                new_row.source_warehouse = item.source_warehouse;
            });
        });

        dispatch_form.no_of_boxes = Object.keys(grouped_items).length;

        frappe.call({
            method: "frappe.client.insert",
            args: { doc: dispatch_form },
            callback: function (save_result) {
                if (save_result.message) {
                    let new_dispatch_id = save_result.message.name;
                    frappe.show_alert({
                        message: __(`CPLs successfully assigned to new Dispatch Form ${new_dispatch_id}`),
                        indicator: 'green'
                    }, 15);

                    let update_promises = selected_docs.map(cpl => {
                        return new Promise(resolve => {
                            frappe.call({
                                method: "frappe.client.set_value",
                                args: {
                                    doctype: "Consolidated Pack List",
                                    name: cpl.name,
                                    fieldname: { 
                                        "custom_dispatched": 1, 
                                        "custom_dispatch_status": "Dispatched", 
                                        "docstatus": 1 
                                    }
                                },
                                callback: function () { resolve(); }
                            });
                        });
                    });

                    Promise.all(update_promises).then(() => {
                        frappe.show_alert({
                            message: __("All selected CPLs have been marked as dispatched and submitted"),
                            indicator: 'green'
                        }, 15);
                        cur_list.refresh();
                    });
                } else {
                    frappe.msgprint(__("Error creating Dispatch Form: ") + save_result.exc);
                }
            }
        });
    });
}