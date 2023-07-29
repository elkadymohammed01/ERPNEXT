// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Terms Template', {
<<<<<<< HEAD
	setup: function(frm) {

=======
	refresh: function(frm) {
		frm.fields_dict.terms.grid.toggle_reqd("payment_term", frm.doc.allocate_payment_based_on_payment_terms);
	},

	allocate_payment_based_on_payment_terms: function(frm) {
		frm.fields_dict.terms.grid.toggle_reqd("payment_term", frm.doc.allocate_payment_based_on_payment_terms);
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
	}
});
