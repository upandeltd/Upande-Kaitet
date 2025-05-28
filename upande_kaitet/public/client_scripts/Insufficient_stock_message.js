
// frappe.ui.form.on("Sales Order", {
//     before_save: function(frm) {
     
//         $.each(frm.doc.items || [], function(i, item) {
            
//             let warehouse = item.custom_source_warehouse || "";
//             let warehouse_display_name = "";
            
            
//             frappe.call({
//                 method: "frappe.client.get_value",
//                 args: {
//                     doctype: "Bin",
//                     filters: {
//                         item_code: item.item_code,
//                         warehouse: warehouse
//                     },
//                     fieldname: ["actual_qty", "warehouse"]
//                 },
//                 async: false,
//                 callback: function(r) {
//                     if (r.message) {
//                         let actual_qty = r.message.actual_qty || 0;
//                         warehouse_display_name = r.message.warehouse;
                        
//                         // Check if stock is sufficient
//                         if (actual_qty < item.qty) {
//                             // Get the warehouse display name with company suffix
//                             frappe.call({
//                                 method: "frappe.client.get_value",
//                                 args: {
//                                     doctype: "Warehouse",
//                                     filters: {
//                                         name: warehouse
//                                     },
//                                     fieldname: ["warehouse_name", "company"]
//                                 },
//                                 async: false,
//                                 callback: function(w) {
//                                     if (w.message) {
//                                         warehouse_display_name = w.message.warehouse_name + " - " + 
//                                             frappe.get_abbr(w.message.company);
//                                     }
//                                 }
//                             });
                            
                         
//                             frappe.validated = false;
                          
//                             let dialog = new frappe.ui.Dialog({
//                                 title: "Insufficient Stock",
//                                 indicator: "red",
//                                 fields: [{
//                                     fieldtype: "HTML",
//                                     options: `<div style="margin: 10px 0px;">
//                                         ${item.stock_qty} units of <strong>${item.item_code}</strong> needed in 
//                                         <strong>${warehouse_display_name}</strong> to complete this transaction.
//                                     </div>`
//                                 }]
//                             });
                            
//                             dialog.show();
//                             return false;
//                         }
//                     }
//                 }
//             });
//         });
//     }
// });frappe.ui.form.on("Sales Order", {
//     before_save: function(frm) {
//         // Check each item in the Sales Order
//         $.each(frm.doc.items || [], function(i, item) {
//             // Get the warehouse for this item
//             let warehouse = item.custom_source_warehouse || "";
//             let warehouse_display_name = "";
            
//             // Get total actual stock for this item in the specified warehouse
//             frappe.call({
//                 method: "frappe.client.get_value",
//                 args: {
//                     doctype: "Bin",
//                     filters: {
//                         item_code: item.item_code,
//                         warehouse: warehouse
//                     },
//                     fieldname: ["actual_qty", "warehouse"]
//                 },
//                 async: false,
//                 callback: function(r) {
//                     if (r.message) {
//                         let actual_qty = r.message.actual_qty || 0;
//                         warehouse_display_name = r.message.warehouse;
                        
//                         // Check if stock is sufficient
//                         if (actual_qty < item.qty) {
//                             // Get the warehouse display name with company suffix
//                             frappe.call({
//                                 method: "frappe.client.get_value",
//                                 args: {
//                                     doctype: "Warehouse",
//                                     filters: {
//                                         name: warehouse
//                                     },
//                                     fieldname: ["warehouse_name", "company"]
//                                 },
//                                 async: false,
//                                 callback: function(w) {
//                                     if (w.message) {
//                                         warehouse_display_name = w.message.warehouse_name + " - " + 
//                                             frappe.get_abbr(w.message.company);
//                                     }
//                                 }
//                             });
                            
//                             // Format the error message like the native ERPNext message
//                             frappe.validated = false;
                            
//                             // Create a dialog that looks like the native insufficient stock message
//                             let dialog = new frappe.ui.Dialog({
//                                 title: "Insufficient Stock",
//                                 indicator: "red",
//                                 fields: [{
//                                     fieldtype: "HTML",
//                                     options: `<div style="margin: 10px 0px;">
//                                         ${item.stock_qty} units of <strong>${item.item_code}</strong> needed in 
//                                         <strong>${warehouse_display_name}</strong> to complete this transaction.
//                                     </div>`
//                                 }]
//                             });
                            
//                             dialog.show();
//                             return false;frappe.ui.form.on("Sales Order", {
//                                 validate: function(frm) {
//                                     // Check each item in the Sales Order
//                                     $.each(frm.doc.items || [], function(i, item) {
//                                         // Check if item exists and has stock
//                                         frappe.call({
//                                             method: "frappe.client.get_value",
//                                             args: {
//                                                 doctype: "Bin",
//                                                 filters: {
//                                                     item_code: item.item_code
//                                                 },
//                                                 fieldname: ["sum(actual_qty) as total_stock"]
//                                             },
//                                             async: false,
//                                             callback: function(r) {
//                                                 if (!r.message || !r.message.total_stock || r.message.total_stock <= 0) {
//                                                     frappe.validated = false;
//                                                     frappe.throw(__("Item {0} is not available in stock. Cannot save Sales Order even as draft.", [item.item_code]));
//                                                 } else if (r.message.total_stock < item.qty) {
//                                                     frappe.validated = false;
//                                                     frappe.throw(__("Insufficient stock for Item {0}. Available: {1}, Required: {2}. Cannot save Sales Order even as draft.", 
//                                                         [item.item_code, r.message.total_stock, item.qty]));
//                                                 }
//                                             }
//                                         });
//                                     });
//                                 }
//                             });
//                         }
//                     }
//                 }
//             });
//         });
//     }
// });