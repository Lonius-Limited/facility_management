// Copyright (c) 2020, 9T9IT and contributors
// For license information, please see license.txt

{% include "facility_management/facility_management/doctype/property_checkup/property_checkup_data.js" %}

frappe.ui.form.on('Property Checkup', {
	property: async function(frm) {
        if (frm.doc.property !='') {
            _fetch_items(frm);
        }
	},
    contract: function(frm) {
        if (frm.doc.contract !='') {
            _get_customer_balance(frm)
        }
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

    var balance = frm.doc.balance;
    var to_pay = (-1 *balance) + parseFloat(total)
    var to_refund = ((-1 *balance) + parseFloat(total)) * -1
    frm.set_value("tenant_pays_amount", to_pay);
    frm.refresh_field('tenant_pays_amount');
    frm.set_value("tenant_refunds_amount", to_refund);
    frm.refresh_field('tenant_refunds_amount');
}

function _get_customer_balance(frm) {
    //SOMETIMES THE CUSTOMER FIELD IS NOT SET FOR REASONS NOT WELL KNOWN! 
    // var this_customer = frm.doc.customer;
    // console.log ('Customer loaded: ' + this_customer)
    // if (this_customer == '' || this_customer == undefined){
        frappe.db.get_doc('Tenant Master', frm.doc.tenant)
        .then(doc => {
            var this_customer = doc.customer;
            console.log('Customer from Tenant: ' + this_customer)
            frm.set_value("customer", this_customer);
            frm.refresh_field('customer');
            _set_net_customer_balance(frm, this_customer)
        })
    // } else {
    //     _set_net_customer_balance(frm, this_customer)
    // }
}

function _set_net_customer_balance(frm, customer) {
    //GET DEPOSIT
    frm.call('get_net_tenant_deposit', {})
    .then(r_deposit => {
        if (r_deposit.message) {
            frm.set_value("rent_deposit", r_deposit.message);
            frm.refresh_field('rent_deposit');
            var paid_deposit = r_deposit.message; //frm.doc.rent_deposit
            //GET BALANCE ON CUSTOMER ACCOUNT
            return frappe.call({
                method: "erpnext.accounts.utils.get_balance_on",
                args: {date: frm.doc.posting_date, party_type: 'Customer', party: customer},
                callback: function(r) {
                    var balance = parseFloat(paid_deposit) - parseFloat(r.message)
                    console.log('Balance: ' + balance);
                    //frm.set_value("balance" ,format_currency(r.message, erpnext.get_currency(frm.doc.company)));
                    frm.set_value("balance", balance);
                    frm.refresh_field('balance'); 

                    var to_pay = (-1 *balance) + parseFloat(frm.doc.total_billed)
                    var to_refund = ((-1 *balance) + parseFloat(frm.doc.total_billed)) * -1
                    frm.set_value("tenant_pays_amount", to_pay);
                    frm.refresh_field('tenant_pays_amount');
                    frm.set_value("tenant_refunds_amount", to_refund);
                    frm.refresh_field('tenant_refunds_amount');
                }
            });
        }
    })
}

function _get_the_deposit(frm) {
    frm.call('get_net_tenant_deposit', {})
    .then(r => {
        if (r.message) {
            frm.set_value("rent_deposit", r.message);
            frm.refresh_field('rent_deposit');
        }
    })
}
