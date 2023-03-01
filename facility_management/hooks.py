# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "facility_management"
app_title = "Facility Management"
app_publisher = "9T9IT"
app_description = "ERPNext app for managing facilities"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@lonius.co.ke"
app_license = "MIT"
required_apps = ["hrms"]

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				[
					"Expense Claim-pm_property_maintenance",
					"Material Request-pm_property_maintenance",
					"Asset Repair-pm_property_maintenance",
					"Sales Invoice-pm_rental_contract",
					"Sales Invoice-pm_property_sb",
					"Sales Invoice-pm_property",
					"Sales Invoice-pm_tenant",
					"Sales Invoice-pm_property_group"
				]
			]
		]
	},
	{
		"doctype": "Property Setter",
		"filters": [
			[
				"name",
				"in",
				[
					"Dashboard Chart-type-options"
				]
			]
		]
	},
	{
		"doctype": "Item",
		"filters": [
			[
				"name",
				"in",
				[
					"ITM-00001", "ITM-00002", "ITM-00003", "ITM-00004", "ITM-00005", "ITM-00006", "ITM-00007"
				]
			]
		]
	},
	{
		"doctype": "Account",
		"filters": [
			[
				"account_number",
				"in",
				[
					"2130"
				]
			]
		]
	},
	{
		"doctype": "Dashboard Chart",
		"filters": [
			[
				"name",
				"in",
				[
					"Rental Value",
					"Rental Revenue",
					"Rental Billing",
					"Rental Property Occupancy"
				]
			]
		]
	}
]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/facility_management/css/facility_management.css"
# app_include_js = "/assets/facility_management/js/facility_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/facility_management/css/facility_management.css"
# web_include_js = "/assets/facility_management/js/facility_management.js"

# include js in page
page_js = {"dashboard": "public/js/dashboard.js"}

# include js in doctype views
doctype_js = {
	"Sales Invoice": "public/js/scripts/sales_invoice.js",
	"Payment Entry": "public/js/scripts/payment_entry.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "facility_management.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Landlord"]

# Installation
# ------------

# before_install = "facility_management.install.before_install"
# after_install = "facility_management.install.after_install"
after_migrate = [
	"facility_management.patches.v0_1.add_initial_violation_categories1.execute",
	"facility_management.patches.v0_4.remove_pm_tenant_renting1.execute",
	"facility_management.patches.v0_14.rental_deposit_and_items_patch1.execute"
]
# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "facility_management.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"validate": "facility_management.doc_events.sales_invoice.validate",
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"facility_management.events.create_invoice.execute",
		"facility_management.events.cancel_rental_contract.execute"
	]
}

auto_cancel_exempted_doctypes = [
	"Property Checkup",
]

# Testing
# -------

# before_tests = "facility_management.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "facility_management.event.get_events"
# }

jenv = {
	"methods": [
		"get_landlord_details:facility_management.api.tenant_renting.get_landlord_details",
		"get_tenant_details:facility_management.api.tenant_renting.get_tenant_details"
	]
}
