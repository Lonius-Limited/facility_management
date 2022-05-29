# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = "0.14.0"


import frappe


def retain_workspace():
	print("Deleting unneccessary workspaces")
	frappe.db.sql("DELETE FROM `tabWorkspace` WHERE module !='Facility Management'")
