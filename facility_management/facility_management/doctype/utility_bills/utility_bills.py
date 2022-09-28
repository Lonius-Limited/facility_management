# Copyright (c) 2022, 9T9IT and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class UtilityBills(Document):
	def validate(self):
		if self.tenant_total != self.amount_billed:
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