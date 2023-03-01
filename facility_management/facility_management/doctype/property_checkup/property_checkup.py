# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_to_date, getdate, nowdate, now_datetime, get_first_day
from facility_management.helpers import get_status, get_debit_to, set_invoice_created

class PropertyCheckup(Document):
	def autoname(self):
		pass
	def validate(self):
		pass
	def on_submit(self):
		_post_rent_deposit_credit_note(self)
		_generate_invoices(self)
	@frappe.whitelist()
	def get_net_tenant_deposit(self):
		deposit_amount = 0.0
		all_deposits = frappe.get_all(
			"Rental Contract Item",
			filters={"description": "Security Deposit", "parent": self.contract}, 
			fields = ["invoice_ref"]
		)
		if all_deposits and all_deposits[0]:
			invoice_ref = all_deposits[0].get("invoice_ref")
			invoice_doc = frappe.get_doc("Sales Invoice", invoice_ref)
			deposit_amount = invoice_doc.get("total") - invoice_doc.get("outstanding_amount")
		return deposit_amount

def _post_rent_deposit_credit_note(self):
	all_deposits = frappe.get_all(
		"Rental Contract Item",
		filters={"description": "Security Deposit", "parent": self.contract}, 
		fields = ["invoice_ref"]
	)
	if all_deposits and all_deposits[0]:
		invoice_ref = all_deposits[0].get("invoice_ref")
		if frappe.get_doc('Sales Invoice', invoice_ref).get('status') != 'Credit Note Issued':
			from erpnext.controllers.sales_and_purchase_return import make_return_doc
			target_doc=None
			return_invoice_doc = make_return_doc("Sales Invoice", invoice_ref, target_doc)
			return_invoice_doc.save()
			return_invoice_doc.submit()

def _generate_invoices(checkup):
	def make_invoice_data():
		contract = frappe.get_doc('Rental Contract', checkup.contract)
		customer = frappe.db.get_value("Tenant Master", contract.tenant, "customer")
		cost_center = frappe.get_doc('Company', contract.company).get('cost_center')
		debit_to = get_debit_to(contract.company)
		return {
			"customer": customer,
			"due_date": checkup.creation,
			"posting_date": checkup.creation,
			"debit_to": debit_to,
			"set_posting_time": 1,
			"posting_time": 0,
			"pm_rental_contract": contract.name,
			"company": contract.company,
			"cost_center": cost_center
		}
	if checkup.sales_items and len(checkup.sales_items) > 0:
		invoice_data = make_invoice_data()
		invoice = frappe.new_doc("Sales Invoice")
		invoice.update(invoice_data)
		for item in checkup.sales_items:
			invoice_item = {"item_code": item.item, "rate": item.rate, "qty": item.qty}
			invoice.append("items", invoice_item)
		invoice.set_missing_values()
		invoice.save(ignore_permissions=True)
		invoice.submit()
