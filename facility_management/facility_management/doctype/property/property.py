# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class Property(Document):
	def validate(self):
		_validate_property_status(self)
	
	def after_insert(self):
		_set_user_permissions(self)

	def on_update(self):
		pass
		#_set_user_permissions(self)

def _validate_property_status(property):
	if property.property_status == 'Rental' and not property.rental_status:
		frappe.throw(_('Please set Rental Status as Vacant or Rented'))

def _set_user_permissions(property):
	landlord = frappe.get_doc('Landlord', property.landlord)
	if not frappe.db.exists("User Permission", {"allow": "Cost Center", "user": landlord.user, "for_value": property.get('name')}):
		frappe.get_doc(
			dict(
				doctype = "User Permission",
				user = landlord.user,
				allow = "Cost Center",
				for_value = property.get('name'),
				apply_to_all_doctypes = 1
			)
		).insert(ignore_permissions=True)
	
	if (landlord.user != frappe.session.user) and (frappe.session.user != 'Administrator'):
		if not frappe.db.exists("User Permission", {"allow": "Cost Center", "user": frappe.session.user, "for_value": property.get('name')}):
			frappe.get_doc(
				dict(
					doctype = "User Permission",
					user = frappe.session.user,
					allow = "Cost Center",
					for_value = property.get('name'),
					apply_to_all_doctypes = 1
				)
			).insert(ignore_permissions=True)