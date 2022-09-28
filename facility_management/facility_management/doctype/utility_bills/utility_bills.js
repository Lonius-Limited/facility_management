// Copyright (c) 2022, 9T9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Utility Bills', {
	// refresh: function(frm) {

	// }
	property: function(frm) {
		frm.call('load_tenants')
		.then(r => {
			if (r.message) {
				let linked_doc = r.message;
				// do something with linked_doc
			}
			frappe.show_alert({
				message:__('The tenants for the property choosen with active contracts have been preloaded.'),
				indicator:'green'
			}, 5);
		})
	},
	units_consumed: function(frm) {
		calculate_rate(frm, frm.doc.units_consumed, frm.doc.amount_billed)
	},
	amount_billed: function(frm) {
		calculate_rate(frm, frm.doc.units_consumed, frm.doc.amount_billed)
	},
	tenant_total: function(frm) {
		if (frm.doc.tenant_total > frm.doc.amount_billed ) {
			frappe.show_alert({
				message:__('Ensure the units consumed by the tenants do not exceed the total units for the bill.'),
				indicator:'red'
			}, 5);
		}
	}
});

frappe.ui.form.on('Utility Bill Item', {
	units_consumed: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", d.units_consumed * frm.doc.rate_per_unit); 
    	frm.refresh_field("amount"); 
		calculate_tenant_totals(frm);
	}
});

function calculate_rate(frm, units, amount) {
	if (units > 0 ) {
		frm.doc.rate_per_unit = amount/units;
		frm.refresh_field("rate_per_unit");
		var running_totals = 0;
		for ( let i in frm.doc.split_to_tenants){
			frm.doc.split_to_tenants[i].amount = frm.doc.split_to_tenants[i].units_consumed * frm.doc.rate_per_unit;
			running_totals += frm.doc.split_to_tenants[i].amount; 
		}
		frm.refresh_field("split_to_tenants"); 
		frm.doc.tenant_total = running_totals;
		frm.refresh_field("tenant_total"); 
	}
	if (frm.doc.tenant_total > frm.doc.amount_billed ) {
		frappe.show_alert({
			message:__('Ensure the units consumed by the tenants do not exceed the total units for the bill.'),
			indicator:'red'
		}, 5);
	}
}

function calculate_tenant_totals(frm) {
	var running_totals = 0;
	for ( let i in frm.doc.split_to_tenants){
		running_totals += frm.doc.split_to_tenants[i].amount; 
	}
	frm.doc.tenant_total = running_totals;
	frm.refresh_field("tenant_total");
	if (frm.doc.tenant_total > frm.doc.amount_billed ) {
		frappe.show_alert({
			message:__('Ensure the units consumed by the tenants do not exceed the total units for the bill.'),
			indicator:'red'
		}, 5);
	}
}