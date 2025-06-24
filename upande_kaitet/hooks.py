app_name = "upande_kaitet"
app_title = "Upande Kaitet"
app_publisher = "	Upande"
app_description = "Kaitet ERP System"
app_email = "dev@upande.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "upande_kaitet",
# 		"logo": "/assets/upande_kaitet/logo.png",
# 		"title": "Upande Kaitet",
# 		"route": "/upande_kaitet",
# 		"has_permission": "upande_kaitet.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/upande_kaitet/css/upande_kaitet.css"
# app_include_js = "/assets/upande_kaitet/js/upande_kaitet.js"

# include js, css files in header of web template
# web_include_css = "/assets/upande_kaitet/css/upande_kaitet.css"
# web_include_js = "/assets/upande_kaitet/js/upande_kaitet.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "upande_kaitet/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "upande_kaitet/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "upande_kaitet.utils.jinja_methods",
# 	"filters": "upande_kaitet.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "upande_kaitet.install.before_install"
# after_install = "upande_kaitet.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "upande_kaitet.uninstall.before_uninstall"
# after_uninstall = "upande_kaitet.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "upande_kaitet.utils.before_app_install"
# after_app_install = "upande_kaitet.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "upande_kaitet.utils.before_app_uninstall"
# after_app_uninstall = "upande_kaitet.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "upande_kaitet.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "Sales Order": {
        "on_submit": [
            #"upande_kaitet.server_scripts.reserve_stock.unreserve_stems",
            "upande_kaitet.server_scripts.pick_list_automation.create_pick_list_for_sales_order"
        ],
        "on_update": [
            # "upande_kaitet.server_scripts.reserve_stock.on_sales_order_update",
            "upande_kaitet.server_scripts.so_delivery_warehouse.handle_sales_order_approval"
        ],
        "before_submit":
        "upande_kaitet.upande_kaitet.custom.sales_order_custom.validate_customer_check_limit",
        "on_cancel":
        "upande_kaitet.server_scripts.so_delivery_warehouse.handle_sales_order_cancellation",
        # "on_save":
        # "upande_kaitet.server_scripts.reserve_stock.on_sales_order_save",
        # "after_insert":
        # "upande_kaitet.server_scripts.reserve_stock.on_sales_order_created",
    },
    "Consolidated Pack List": {
        # "on_submit":
        # "upande_kaitet.server_scripts.create_sales_invoice.create_sales_invoice_from_packlist",
        "on_cancel": "upande_kaitet.server_scripts.events.on_cpl_cancel"

        # "before_submit":
        # "upande_kaitet.server_scripts.completion_percentage.validate_completion_percentage"
    },
    "Sales Invoice": {
        "on_submit":
        "upande_kaitet.server_scripts.sinv_approved_by.set_approved_by",
        "on_cancel":
        "upande_kaitet.server_scripts.events.on_sales_invoice_cancel"
    },
    "Farm Pack List": {
        "before_cancel":
        "upande_kaitet.server_scripts.fpl_to_cpl_link.before_cancel",
        # "on_submit":
        # "upande_kaitet.server_scripts.create_sales_invoice.create_sales_invoice_from_packlist",
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"upande_kaitet.tasks.transfer_holding_to_cold_store"
	# ],
	"daily": [
		"upande_kaitet.tasks.transfer_holding_to_cold_store"
	],
# 	"hourly": [
# 		"upande_kaitet.tasks.hourly"
# 	],
# 	"weekly": [
# 		"upande_kaitet.tasks.weekly"
# 	],
# 	"monthly": [
# 		"upande_kaitet.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "upande_kaitet.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "upande_kaitet.event.get_events"
}

override_class = {
    "erpnext.controllers.taxes_and_totals.calculate_taxes_and_totals":
    "upande_kaitet.overrides.standard_system_rate.CustomTaxesAndTotals"
}

whitelisted_methods = {
    "get_item_group_price":
    "upande_kaitet.server_scripts.fetch_item_grp_price.get_item_group_price",
    "create_sales_invoice":
    "upande_kaitet.server_scripts.create_sales_invoice.create_sales_invoice"
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "upande_kaitet.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["upande_kaitet.utils.before_request"]
# after_request = ["upande_kaitet.utils.after_request"]

# Job Events
# ----------
# before_job = ["upande_kaitet.utils.before_job"]
# after_job = ["upande_kaitet.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"upande_kaitet.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [{
    "dt":
    "DocType",
    "filters": [[
        "name", "in",
        [
            "QR Code", "Packing List", "Pack List Item",
            "Scan", "Box Label", "Box Label Item", "Label Print",
            "Bucket QR Code", "Bunch QR Code", "Grader QR Code", "Harvest",
            "Scanned Items", "Scan Check", "Scan Check List", "QR Sequence",
            "Rejection Reason", "Grading Repack Tracker Item",
            "Grading Forecast Tracker", "Forecast Entry", "Forecast Entry Item",
            "Business Unit", "Scan Location Mapping", "Scan Location Mapping Items",
            "Farm", "Joint Companies", "Business Unit", "GPS Reading", "Vehicle",
            "GPS Readings", "Delivery Type", "Loss Reason", "SO Warehouse Mapping",
            "SO Warehouse Mapping Item", "Temperature Reading", "Consignee",
        ]
    ]]
}, {
    "dt":
    "Server Script",
    "filters": [[
        "name", "in",
        [
            "Stock Entry Script", "Stock Entry After Save", "Scan Timestamp",
            "Harvest Stock Entry", "Automate Rejects Material Issue",
            "Create Box Labels", "Update Grading Forecast Tracker",
            "Update Sales Order ID on Save",
            "Update Forecast Tracker (During Grading)",
            "Update Tracker (During Grading Cancel)",
            "Update Tracker (Grading Forecast)", "Forecast Entry",
            "Allow Packing Of Returned Bunches", "FPL Block New Version",
            "Lock Dates On Submit of Sales Invoice",
            "Validate unique bucket ID", "Set Bucket Id Status",
            "Create delivery trip", "Request Concession", "Filtering based on Role",
            "Work Order, Event; on_submit", "Material Issue Notification", "Start Trip Transfer",
            "End Trip Transfer", "Gps", "Repack", "Create Invoice From Dispatch Form",
            "Create Field Reject Entry"
        ]
    ]]
}, {
    "dt":
    "Client Script",
    "filters": [[
        "name", "in",
        [
            "Qr Code gen", "Close Box Button", "Scan Via Honeywell",
            "Scan Data Field Listener", "Scan QR Button",
            "Populate Number of Items", "Grading Stock Entry",
            "Field Rejects Stock Entry", "Archive Employee",
            "Transfer Grading Stock", "Generate Bucket Codes", "Harvest Scan",
            "New Form After Save", "Remove Read Only on Field",
            "Ensure Bucket Is Scanned On Save", "Field Rejects Stock Entry",
            "Hide Filter Button 2",
            "Hide Filter Button (Bucket QR Code List) 2",
            "Ensure Uppercase in Bay Field", "Grading Traceability Symbols",
            "SO target warehouse Population",
            "Set List View Limit to 500(GRADER)",
            "Set List View Limit to 500(BUNCH)",
            "Set List View Limit to 500(BUCKET)", "Restrict Bay to Alphabets",
            "Autopopulate Sales Order ID in CPL",
            "Ensure Items are in SO Before Manually Adding (FPL)",
            "Authorise Under Pack Button in FPL",
            "Autopopulate Sales Order ID in FPL",
            "Amount Calc Based on IGP", "Under Pack Cancel Button",
            "Combined Script", "Request Concession Button", "Request Concession 2",
            "Employee Filtering", "Yoghurt Manufacturing Stock Entry", "Work Order",
            "Geo", "Hide Fields in Work Order", "Loss Reason Mandatory", "Stock Entry Type Automation",
            "Default Source and Target Warehouse", "Allow Valuation Rate", "Start Job Script",
            "Fetch Farm and Business Unit", "Update Source Warehouse", "Trip Button",
            "Populate WIP and Target Warehoise in Work Order", "Auto-fetch Company from BOM in Work Order",
            "Auto-fetch Company", "Auto-set Company on BOM based on Item's Warehouse", "Repack Button", 
            "Create Delivery Note Button", "Autopopulate Farm and Business Unit (SO)", "Custom Workflow Approval (Delivery note)",
            "Fetch SO Details", "Yoghurt Delivery Workflow", "Autopopulate Week Number", "Populate Available Qty Field"
            "CSU AM Checksheet" , "Tractor Inspection Checksheet" , "Truck Inspection Checksheet" ,"Packhouse Equipment and Machine AM Checklist" , "CFU Inspection Checksheet" , "CSU AM Checksheet" ,"Tractor Inspection Checksheet"
        ]
    ]]
}, {
    "dt":
    "Print Format",
    "filters": [[
        "name", "in",
        [
            "QR Code Only", "Box Label", "Harvest Label",
            "Grader QR Print Format", "Bunch QR Code",
            "Trial Bunch Print Format", "Grader QR Print format 2",
            "Harvest Label 2"
        ]
    ]]
}]
# fixtures = ["Custom Field", "Property Setter", "DocType"]
