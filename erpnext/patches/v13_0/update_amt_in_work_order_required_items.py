import frappe


def execute():
	"""Correct amount in child table of required items table."""

	frappe.reload_doc("manufacturing", "doctype", "work_order")
	frappe.reload_doc("manufacturing", "doctype", "work_order_item")

<<<<<<< HEAD
	frappe.db.sql("""UPDATE `tabWork Order Item` SET amount = rate * required_qty""")
=======
	frappe.db.sql(
		"""UPDATE `tabWork Order Item` SET amount = ifnull(rate, 0.0) * ifnull(required_qty, 0.0)"""
	)
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
