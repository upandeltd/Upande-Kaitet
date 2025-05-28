frappe.ui.form.on('Dispatch Form', {
    custom_date: function(frm) {
        console.log('Date changed event triggered');
        console.log('Current date value:', frm.doc.custom_date);
        
        if (frm.doc.custom_date) {
            // Convert the date string to a Date object
            let currentDate = frappe.datetime.str_to_obj(frm.doc.custom_date);
            console.log('Converted date object:', currentDate);
            
            // Calculate the week number
            let startOfYear = new Date(currentDate.getFullYear(), 0, 1);
            console.log('Start of year:', startOfYear);
            
            let days = Math.floor((currentDate - startOfYear) / (24 * 60 * 60 * 1000));
            console.log('Days since start of year:', days);
            
            let weekNumber = Math.ceil((days + startOfYear.getDay() + 1) / 7);
            console.log('Calculated week number:', weekNumber);
            
            // Set the week field value using the correct fieldname
            frm.set_value('custom_week_', weekNumber);
            
            // Refresh the field
            frm.refresh_field('custom_week_');
        }
    },
    
    refresh: function(frm) {
        console.log('Form refreshed');
        console.log('Current date:', frm.doc.custom_date);
        console.log('Current week:', frm.doc.custom_week_);
    }
});