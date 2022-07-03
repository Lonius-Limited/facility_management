# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe import _
from frappe.utils import validate_phone_number, validate_email_address
import string, random
from frappe.core.doctype.user_permission.user_permission import clear_user_permissions

class Landlord(WebsiteGenerator):
	def validate(self):
		_validate_contacts(self)
	
	def before_insert(self):
		self.user = link_user_and_company(self)

def _validate_contacts(landlord):
	if not validate_phone_number(landlord.phone):
		frappe.throw(_('Please enter a valid phone number'))
	if validate_email_address(landlord.email) == '':
		frappe.throw(_('Please enter a valid email address'))

# CODE TO REGISTER LANDLORD/AGENT AS USER AND SET THE RIGHT USER PERMISSIONS AND RESTRICTIONS ON MODULES
def get_company_id():
	payload = string.ascii_uppercase + "1234567890"
	abbr1 = random.choices(payload, k=5)
	return "".join(abbr1)
def link_user_and_company(doc):
	company = make_company(doc)
	user = make_and_link_user(doc)
	create_user_cost_center(doc, user, company)
	doc.set('user', user.get('name'))
	# doc.save(ignore_permissions=True)
	message ="""<p>Dear <b style='color:green'>{}</b> <br/>
			An account has been successfully set up for you.\nYou will be able to set your login password via the provided email address:  <b style='color:blue'>{}. </p> 
			<p>Once you have logged in, click on the 'Property Management' Menu on the left hand of the screen. You will be presented with the following menu buttons and actions you can do:
			<br/><ul>
			<li><b style='color:green'>Property</b> - This is where you register your entire property. A single property will contain one or more units.</li>
			<li><b style='color:green'>Units</b> - For each <b>Property</b> you have registered, you can add unlimited number of units. Example is a 2 bedroom house.</li>
			<li><b style='color:green'>New Tenant </b>- You will be able to enter a tenant plus their details here. You can enter them one by one or upload via an Excel template.</li>
			<li><b style='color:green'>Rental Contracts </b>- You will be able to manage tenant contracts here. Upload existing contracts together with their templates and you can scan existing contracts and upload them as well.</li>
			<li><b style='color:green'>Landlord Master List </b>- You will be able to view your account here. Additionally, if you are an agent, you will be able to add more landlords that you are managing. Each of the landlords added will get their own accounts to track their tenants but you will be able to view their portfolios as well.</li>
			<li><b style='color:green'>Tenant Monthly Invoices </b>- The system uses the contracts you have set to automatically generate invoices. Those invoices will be sent out to your tenants automatically on the set dates e.g. 1st of every month. You will be able to view those invoices here. Any correspondences from clients will be attached to these invoices and can be handled from here.</li>
			<li><b style='color:green'>Tenant Receipts </b>- Payments made by your tenants using your Paybill or any other integrated payments e.g. bank, will get posted here automatically. Receipts are sent automatically for every recorded payments to reassure tenants of receipt. You can also create payment entries here for payments that may have been made to you outside this system and receipts will be sent to your tenants.</li>
			<li><b style='color:green'>Income Report </b>- This report gives you one dashboard of the performance of payments by your tenants. It is an accounts receivable report aged on 30 days interval.</li>
			<li><b style='color:green'>Expense Claim/Petty Cash </b>- This menu gives you the capability to post petty cash as well as other expenses to your employees. It allows you to keep track of expenses incurred for the property.</li>
			<li><b style='color:green'>My Vendors </b>- You will be able to register all your suppliers/vendors/service providers here. If you have a contracted electrician or plumber for example, this is where you register them.</li>
			<li><b style='color:green'>Vendor Invoices </b>- For every supplier/vendor/service provider, you can keep track of all their invoices here as well as process payments linked to every invoice.</li>
			<li><b style='color:green'>Payments </b>- Payments made against any invoice to any supplier/vendor can be accessed from here.</li>
			<li><b style='color:green'>Property Checkin/Checkout </b>- This is the document you will use to record the status of the unit when a tenant checks in or during checkout.</li>
			<li><b style='color:green'>Property Inventory </b>- If you have one or two <b>Fully Furnished or Semi Furnished</b> units, you may be interested in tracking their inventory. This is where you do that. You can add each item and their quantities and can form basis for future inspections.</li>
			<li><b style='color:green'>Property Maintenance </b>- This helps you keep track of your tenant tickets and automatically updates your tenants when those tickets are closed. It is useful for keeping track of maintenance requests and other chores. The categories include: carpentry, civil, electrical, mechanical, plumbing, electrical, technology and others.</li>
			<li><b style='color:green'>Tenant Violations</b>- You may have one or two troublesome tenants. As part of the contracts you may have a requirements of maximum number of violations before contract voiding. This is where this document comes handy. You can track all violations and their resolutions here.</li>
			</ul>
			</p>
			<p>We hope this can help you quickly get you started on Ploti Cloud. Enjoy the instant benefits of never staying in the dark about your Properties.<br/> If you have any questions contact us via the email: info@ploti.cloud.
			</p><br/><br/>""".format(doc.get('landlord_name').title(),doc.get('email').lower())
	# frappe.msgprint(f"{message}")
	alert_practitioner(doc,message)
	return user.get('name')
def alert_practitioner(doc, message):
	"""send email with intro message"""
	email_args = {
		"recipients": doc.get("email"),
		# "sender": None,
		"subject": 'Welcome to Ploti Cloud!',
		"message": message,
		"now": True
		#"attachments": [frappe.attach_print(doc.doctype, doc.name,
		#	file_name=doc.name)]
	}
	frappe.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
def make_company(doc):
	pc = frappe.get_all(
		"Company",
		#filters=dict(is_group=1, parent_company=""),
		filters=dict(parent_company=""),
		fields=["*"],
		order_by="creation DESC",
		page_length=1,
	)
	if not pc:
		frappe.throw(
			"Sorry, there is an issue preventing your registration at this time. Try again later."
		)
	parent_company = pc[0]
	""" args = dict(
		doctype="Company",
		company_name=doc.get("name"),
		parent_company=parent_company.get("name"),
		is_group=0,
		abbr=get_company_id(),
		default_currency=parent_company.get("default_currency"),
		country=parent_company.get("country"),
	)
	company = frappe.get_doc(args).save(ignore_permissions=1) """
	return parent_company.get("name")


def make_and_link_user(doc):
	args = {
		"doctype": "User",
		"send_welcome_email": 1,
		"email": doc.get('email'),
		"first_name": doc.get("landlord_name"),
		"user_type": "System User",
	}
	user = frappe.get_doc(args)

	user.append('roles',dict(role='Expense Approver'))
	user.append('roles',dict(role='Item Manager'))
	user.append('roles',dict(role='HR User'))
	user.append('roles',dict(role='Stock Manager'))
	# user.append('roles',dict(role='Accounts Manager'))
	user.append('roles',dict(role='Purchase Manager'))
	user.append('roles',dict(role='Purchase User'))
	user.append('roles',dict(role='Purchase Master Manager'))
	user.append('roles',dict(role='Sales Master Manager'))
	user.append('roles',dict(role='Sales Manager'))
	user.append('roles',dict(role='Sales User'))
	user.append('roles',dict(role='Accounts User'))
	user.append('roles',dict(role='Inbox User'))
	user.append('roles',dict(role='Report Manager'))
	user.append('roles',dict(role='Prepared Report User'))
	user.append('roles',dict(role='Dashboard Manager'))
	
	#BLOCK ALL MODULES THAT THEY DON'T NEED ACCESS TO
	from frappe.config import get_modules_from_all_apps
	user.set('block_modules', [])
	allowed_modules = ['Workflow', 'Desk', 'Printing', 'Facility Management']
	for m in get_modules_from_all_apps():
		if m.get("module_name") not in allowed_modules:
			user.append('block_modules', {
				'module': m.get("module_name") 
			})
	user.save(ignore_permissions=True)
	return user

def create_user_cost_center(doc, user, company):
	#CREATE COST CENTER
	group_cost_center = frappe.get_all("Cost Center", filters=dict(is_group=1, parent_cost_center = ""), fields = ["*"], page_length=1)
	cost_center = frappe.get_doc(
		dict(
			doctype="Cost Center",
			cost_center_name = user.get('name'),
			cost_center_number = doc.get('name'),
			parent_cost_center = group_cost_center[0].get('name'),
			company = company
		)
	).insert(ignore_permissions=True)
	add_restrictions(doc, user, company, cost_center)
	doc.cost_center = cost_center.get('name')
	if doc.agent_cost_center == "": doc.agent_cost_center = cost_center.get('name')

def add_restrictions(doc, user, company, cost_center):
	""" clear_user_permissions(user, "Company")
	frappe.get_doc(
		dict(
			doctype="User Permission",
			user=user.get('name'),
			allow="Company",
			for_value=company.get('name'),
			apply_to_all_doctypes=1,
			# applicable_for="Material Request",
		)
	).insert(ignore_permissions=True) """

	#SET USER PERMISSION TO COST CENTER FOR BOTH LOGIN USER AND LANDLORD USER
	# clear_user_permissions(user, "Cost Center")
	if not frappe.db.exists("User Permission", {"allow": "Cost Center", "user": user.get('name'), "for_value": cost_center.get('name')}):
		frappe.get_doc(
			dict(
				doctype="User Permission",
				user=user.get('name'),
				allow="Cost Center",
				for_value=cost_center.get('name'),
				apply_to_all_doctypes=1,
				# applicable_for="Material Request",
			)
		).insert(ignore_permissions=True)
	if (user.get('name') != frappe.session.user) and (frappe.session.user != 'Administrator'):
		if not frappe.db.exists("User Permission", {"allow": "Cost Center", "user": frappe.session.user, "for_value": cost_center.get('name')}):
			frappe.get_doc(
				dict(
					doctype="User Permission",
					user=frappe.session.user,
					allow="Cost Center",
					for_value=cost_center.get('name'),
					apply_to_all_doctypes=1,
					# applicable_for="Material Request",
				)
			).insert(ignore_permissions=True)
