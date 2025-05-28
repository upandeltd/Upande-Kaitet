import json
import qrcode
import frappe
import os
from PIL import Image, ImageDraw, ImageFont
import time

@frappe.whitelist(allow_guest=True)
def generate_qr_code(stock_entry_details):
    url = frappe.utils.get_url()

    stock_entry_details = json.loads(stock_entry_details)

    stock_entry_name = stock_entry_details.get('name')
    graded_by_id = stock_entry_details.get('grader')
    stock_entry_url = f"{url}/app/stock-entry/{stock_entry_name}"
    unique_id = int(time.time())

    graded_by_name = frappe.db.get_value("Employee", graded_by_id, "employee_name") or "Unknown"

    bucket_details = {
        "Variety": stock_entry_details.get('variety'),
        "Stock Entry URL": stock_entry_url
    }

    quantity = stock_entry_details.get('qty', 1)
    variety = bucket_details.get("Variety", "Unknown Variety")

    qr_codes_dir_path = frappe.utils.get_files_path("qr_codes")
    os.makedirs(qr_codes_dir_path, exist_ok = True)

    qr_codes = []



    for i in range(1, quantity + 1):
        bunch_id = f"{stock_entry_name}-Bunch-{i}"

        qr_data = {
            "url": stock_entry_url,
            "bunch_id": bunch_id
        }

        qr_data_string = ";".join([f"{key}={value}" for key, value in qr_data.items()])

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )

        qr.add_data(qr_data_string)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')

        qr_width, qr_height = qr_img.size

        label_margin = 10  # Adjust this margin value to your needs
        label_width = qr_width + (label_margin * 2)
        label_height = qr_height + (label_margin * 2)

        qr_target_width = qr_width
        qr_target_height = qr_height
        qr_img = qr_img.resize((qr_target_width, qr_target_height))

        canvas = Image.new("RGB", (label_width, label_height), "white")
        draw = ImageDraw.Draw(canvas)

        # Paste QR Code on the left
        qr_x = (label_width - qr_target_width) // 2 
        qr_y = (label_height - qr_target_height) // 2 
        canvas.paste(qr_img, (qr_x, qr_y))

        file_path = os.path.join(qr_codes_dir_path, f"{stock_entry_name}_{unique_id}_{i}.png")
        canvas.save(file_path)

        file_url = f"/files/qr_codes/{stock_entry_name}_{unique_id}_{i}.png"

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_url": f"/files/qr_codes/{stock_entry_name}_{unique_id}_{i}.png",
            "attached_to_doctype": "Stock Entry",
            "attached_to_name": stock_entry_name,
            "is_private": 0
        })

        file_doc.insert(ignore_permissions=True)

        qr_code_doc = frappe.get_doc({
            "doctype": "QR Code",
            "bunch_id": bunch_id,
            "qr_code_image": file_doc.file_url,
            "stock_entry": stock_entry_name,
            "graded_by": graded_by_name,
            "variety": variety
        })



        qr_code_doc.insert(ignore_permissions=True)
        frappe.db.commit() 

        qr_codes.append({
            "bunch_id": bunch_id,
            "qr_url": file_url, 
            "qr_doctype_id": qr_code_doc.name  
        })

    return {"message": qr_codes}