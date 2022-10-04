# Copyright (c) 2022, 9T9IT and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class UtilityBills(Document):
	def validate(self):
		if (self.tenant_total + self.landlord_bill_amount) != self.amount_billed:
			frappe.throw("Please ensure that the distribution to the tenants adds up to the total units in the bill.")
	
	@frappe.whitelist()
	def load_tenants(self):
		items = []
		this_property_contracts = frappe.db.get_list("Rental Contract",
			filters={
				'property_group': self.property,
				'status': 'Active',
				'docstatus': 1
			},
			fields = ['name', 'tenant', 'tenant_name']
		)
		for contract in this_property_contracts:
			item = {
				'contract': contract.name,
				'tenant': contract.tenant_name
			}
			items.append(item)
		self.update({"split_to_tenants": items})
	
	@frappe.whitelist()
	def get_last_reading(self, property, bill):
		last_bill = frappe.db.get_list("Utility Bills",
			filters={
				'property': property,
				'bill': bill,
				'posting_date': ['<', self.posting_date]
			},
		 	fields = ['posting_date', 'bill_reading'],
		  	order_by = 'posting_date desc',
		   	page_length=1
		)
		if last_bill and last_bill[0]:
			self.last_bill_date = last_bill[0].posting_date or self.posting_date
			self.last_reading = last_bill[0].bill_reading
			# self.update("last_bill_date", last_bill[0].posting_date or self.posting_date)
			# self.update("last_reading", last_bill[0].bill_reading)
