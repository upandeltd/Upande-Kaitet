// frappe.ui.form.on("Sales Order Item", {
//     item_code: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         if (row.item_code) {
//             frappe.call({
//                 method: "frappe.client.get_list",
//                 args: {
//                     doctype: "Bin",
//                     filters: { item_code: row.item_code },
//                     fields: ["warehouse", "actual_qty"],
//                     order_by: "actual_qty desc"
//                 },
//                 callback: function(r) {
//                     if (r.message && r.message.length > 0) {
//                         let total_stock = 0;
//                         let stock_info = r.message.map(bin => {
//                             total_stock += bin.actual_qty;
//                             return `<b>${bin.warehouse}:</b> ${bin.actual_qty} units`;
//                         }).join("<br>");

//                         // ✅ Correct fieldname
//                         frm.set_value("custom_available_stock", total_stock);

//                         frappe.msgprint({
//                             title: __("Stock Availability"),
//                             message: `Available stock for <b>${row.item_code}</b>:<br><br> ${stock_info}`,
//                             indicator: "green"
//                         });
//                     } else {
//                         frm.set_value("custom_available_stock", 0);

//                         frappe.msgprint({
//                             title: __("No Stock Available"),
//                             message: `No stock found for <b>${row.item_code}</b> in any warehouse.`,
//                             indicator: "red"
//                         });
//                     }
//                 }
//             });
//         }
//     }
// });
