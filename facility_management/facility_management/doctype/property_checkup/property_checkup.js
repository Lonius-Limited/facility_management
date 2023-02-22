// Copyright (c) 2020, 9T9IT and contributors
// For license information, please see license.txt

{% include "facility_management/facility_management/doctype/property_checkup/property_checkup_data.js" %}

frappe.ui.form.on('Property Checkup', {
	onload_post_render: function(frm) {
        frm.call('get_net_tenant_deposit', {})
        .then(r => {
            if (r.message) {
                frm.set_value("rent_deposit", r.message);
                refresh_field('rent_deposit');
            }
        })

        // frappe.call('facility_management.helpers.set_all_property_as_vacant', {
        //     contract: frm.doc.contract
        // }).then(r => {
        //     console.log(r.message)
        // })
	},
	property: async function(frm) {
	    _fetch_items(frm);
	},
    contract: function(frm) {
        _get_customer_balance(frm)
    }
});

frappe.ui.form.on('Property Checkup Sale Item', {
    qty: function(frm, cdt, cdn)  {
        var d = locals[cdt][cdn];
        _calculate_amount(frm, d, cdt, cdn);
    },
    rate: function(frm, cdt, cdn)  {
        var d = locals[cdt][cdn];
        _calculate_amount(frm, d,  cdt, cdn);
    }
});

async function _fetch_items(frm) {
    const property = frm.doc.property;
    const items = await get_items(property);
    items.forEach((item) => {
        const child = frm.add_child('items');
        frappe.model.set_value(child.doctype, child.name, 'item', item.item);
    });
    frm.refresh_field('items');
}

function _calculate_amount(frm, d,  cdt, cdn) {
    frappe.model.set_value(cdt, cdn, "amount", d.qty * d.rate); 
    frm.refresh_field("amount");
    var total = 0;
    frm.doc.sales_items.forEach(function(d) { total += d.amount; });
    frm.set_value("total_billed", total);
    refresh_field("total_billed");
}

function _get_customer_balance(frm) {
    //GET DEPOSIT
    _get_the_deposit(frm);
    var paid_deposit = frm.doc.rent_deposit
    //GET BALANCE ON CUSTOMER ACCOUNT
    return frappe.call({
		method: "erpnext.accounts.utils.get_balance_on",
		args: {date: frm.doc.posting_date, party_type: 'Customer', party: frm.doc.customer},
		callback: function(r) {
            console.log('Balance: ' + (parseFloat(paid_deposit) - parseFloat(r.message)));
			//frm.set_value("balance" ,format_currency(r.message, erpnext.get_currency(frm.doc.company)));
            frm.set_value("balance", (parseFloat(paid_deposit) - parseFloat(r.message)));
			refresh_field('balance');
		}
	});
}

function _get_the_deposit(frm) {
    
}
