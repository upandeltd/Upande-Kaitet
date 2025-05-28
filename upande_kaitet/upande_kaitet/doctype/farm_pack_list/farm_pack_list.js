// frappe.ui.form.on('Farm Pack List', {
//     refresh: function(frm) {
//         // Keep the manual button for non-submitted documents or already closed documents
//         if(frm.doc.docstatus === 1 && frm.doc.custom_status !== 'Closed') {
//             frm.add_custom_button('Add to Consolidated Pack List', () => {
//                 addToConsolidatedPackList(frm);
//             });
//         }
//     },
    
//     // Add this new handler that triggers when document is submitted
//     on_submit: function(frm) {
//         // Automatically add to consolidated pack list on submission
//         addToConsolidatedPackList(frm);
//     }
// });

// // Moved the functionality to a separate function to avoid code duplication
// function addToConsolidatedPackList(frm) {
//     // First call to close the farm pack list
//     frappe.call({
//         method: 'upande_kaitet.upande_kaitet.doctype.farm_pack_list.farm_pack_list.close_farm_pack_list',
//         args: {
//             'farm_pack_list': frm.doc.name
//         },
//         callback: function(r) {
//             if(!r.exc) {
//                 // After closing, process the CPL
//                 frappe.call({
//                     method: 'upande_kaitet.upande_kaitet.doctype.farm_pack_list.farm_pack_list.process_consolidated_pack_list',
//                     args: {
//                         'farm_pack_list': frm.doc.name,
//                         'sales_order': frm.doc.sales_order_id
//                     },
//                     callback: function(r) {
//                         if(!r.exc) {
//                             // Update the status in the UI
//                             frm.set_value('custom_status', 'Closed');
//                             frm.save();
//                             frm.reload_doc();
                            
//                             frappe.show_alert({
//                                 message: 'Farm Pack List automatically added to Consolidated Pack List',
//                                 indicator: 'green'
//                             });
                            
//                             // Remove the manual button if it exists
//                             frm.remove_custom_button('Add to Consolidated Pack List');
//                         }
//                     }
//                 });
//             }
//         }
//     });
// }