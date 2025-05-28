frappe.ui.form.on('Sales Order', {
    currency: function(frm) {
        console.log("Script triggered: Currency field changed");

        if (frm.doc.currency) {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Price List',
                    filters: {
                        currency: frm.doc.currency,
                        selling: 1
                    },
                    fields: ['name']
                },
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        console.log("Price list fetched successfully: " + r.message[0].name);
                        frm.set_value('selling_price_list', r.message[0].name);
                    }
                }
            });
        }
    }
});
