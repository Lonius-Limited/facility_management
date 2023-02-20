# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PropertyCheckup(Document):
	@frappe.whitelist()
	def tenant_deposit(self):
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