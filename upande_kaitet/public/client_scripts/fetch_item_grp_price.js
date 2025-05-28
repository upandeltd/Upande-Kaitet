// // Copyright (c) 2025, Upande Limited
// // For license information, please see license.txt

// frappe.ui.form.on('Sales Order Item', {
//     custom_length(frm, cdt, cdn) {
//         const row = frappe.get_doc(cdt, cdn);

//         if (row.item_group && row.custom_length) {
//             frappe.call({
//                 method: 'upande_kaitet.api.fetch_item_grp_price.fetch_item_grp_price',
//                 args: {
//                     item_group: row.item_group,
//                     length: row.custom_length,
//                     currency: frm.doc.currency
//                 },
//                 callback: function(r) {
//                     const rate = r.message || 0;

//                     frappe.model.set_value(cdt, cdn, 'rate', rate);
//                     frappe.model.set_value(cdt, cdn, 'stock_uom_rate', rate);

//                     if (!r.message) {
//                         frappe.msgprint(__('No price found for this customer\'s currency or the selected item. Please set a price to proceed!'));
//                     }
//                 }
//             });
//         }
//     }
// });
