// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Batch Item Expiry Status"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.sys_defaults.year_start_date,
<<<<<<< HEAD
=======
			"reqd": 1,
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
<<<<<<< HEAD
			"default": frappe.datetime.get_today()
=======
			"default": frappe.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "100",
			"get_query": function () {
				return {
					filters: {"has_batch_no": 1}
				}
			}
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
		}
	]
}
