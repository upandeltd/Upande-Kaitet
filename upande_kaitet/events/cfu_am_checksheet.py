import frappe

def create_support_issues(doc, method):
    for item in doc.inspection_items:
        if item.status == "X Faulty":
            subject = f"[{doc.name}] Faulty: {item.equipment or ''} > {item.part_name or ''}"

            description = (
                f"⚠️ Issue reported from CFU AM CHECKLIST:\n\n"
                f"• Equipment: {item.equipment or 'N/A'}\n"
                f"• Part: {item.part_name or 'N/A'}\n"
                f"• Parameter Checked: {item.parameter_checked or 'N/A'}\n"
                f"• Notes: {item.notes or 'N/A'}\n"
                f"• Reported by: {doc.inspector or 'Unknown'}\n"
                f"• Date: {doc.date or 'Unknown'}\n"
                f"• Time: {doc.time or 'Unknown'}"
            )

            frappe.get_doc({
                "doctype": "Issue",
                "subject": subject,
                "issue_type": "Maintenance",
                "raised_by": frappe.session.user,
                "description": description,
                "reference_doctype": doc.doctype,
                "reference_name": doc.name,
                "priority": "High"
            }).insert(ignore_permissions=True)

