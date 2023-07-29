# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

<<<<<<< HEAD

=======
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
import re

import frappe
from frappe import _
from frappe.utils import format_datetime

<<<<<<< HEAD

def execute(filters=None):
	account_details = {}
	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters)

	return columns, res


def validate_filters(filters, account_details):
=======
COLUMNS = [
	{
		"label": "JournalCode",
		"fieldname": "JournalCode",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "JournalLib",
		"fieldname": "JournalLib",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "EcritureNum",
		"fieldname": "EcritureNum",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "EcritureDate",
		"fieldname": "EcritureDate",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "CompteNum",
		"fieldname": "CompteNum",
		"fieldtype": "Link",
		"options": "Account",
		"width": 100,
	},
	{
		"label": "CompteLib",
		"fieldname": "CompteLib",
		"fieldtype": "Link",
		"options": "Account",
		"width": 200,
	},
	{
		"label": "CompAuxNum",
		"fieldname": "CompAuxNum",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "CompAuxLib",
		"fieldname": "CompAuxLib",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "PieceRef",
		"fieldname": "PieceRef",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "PieceDate",
		"fieldname": "PieceDate",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "EcritureLib",
		"fieldname": "EcritureLib",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "Debit",
		"fieldname": "Debit",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "Credit",
		"fieldname": "Credit",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "EcritureLet",
		"fieldname": "EcritureLet",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "DateLet",
		"fieldname": "DateLet",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "ValidDate",
		"fieldname": "ValidDate",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "Montantdevise",
		"fieldname": "Montantdevise",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": "Idevise",
		"fieldname": "Idevise",
		"fieldtype": "Data",
		"width": 90,
	},
]


def execute(filters=None):
	validate_filters(filters)
	return COLUMNS, get_result(
		company=filters["company"],
		fiscal_year=filters["fiscal_year"],
	)


def validate_filters(filters):
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
	if not filters.get("company"):
		frappe.throw(_("{0} is mandatory").format(_("Company")))

	if not filters.get("fiscal_year"):
		frappe.throw(_("{0} is mandatory").format(_("Fiscal Year")))


<<<<<<< HEAD
def set_account_currency(filters):

	filters["company_currency"] = frappe.get_cached_value(
		"Company", filters.company, "default_currency"
	)

	return filters


def get_columns(filters):
	columns = [
		"JournalCode" + "::90",
		"JournalLib" + "::90",
		"EcritureNum" + ":Dynamic Link:90",
		"EcritureDate" + "::90",
		"CompteNum" + ":Link/Account:100",
		"CompteLib" + ":Link/Account:200",
		"CompAuxNum" + "::90",
		"CompAuxLib" + "::90",
		"PieceRef" + "::90",
		"PieceDate" + "::90",
		"EcritureLib" + "::90",
		"Debit" + "::90",
		"Credit" + "::90",
		"EcritureLet" + "::90",
		"DateLet" + "::90",
		"ValidDate" + "::90",
		"Montantdevise" + "::90",
		"Idevise" + "::90",
	]

	return columns


def get_result(filters):
	gl_entries = get_gl_entries(filters)

	result = get_result_as_list(gl_entries, filters)

	return result


def get_gl_entries(filters):

	group_by_condition = (
		"group by voucher_type, voucher_no, account"
		if filters.get("group_by_voucher")
		else "group by gl.name"
	)

	gl_entries = frappe.db.sql(
		"""
		select
			gl.posting_date as GlPostDate, gl.name as GlName, gl.account, gl.transaction_date,
			sum(gl.debit) as debit, sum(gl.credit) as credit,
			sum(gl.debit_in_account_currency) as debitCurr, sum(gl.credit_in_account_currency) as creditCurr,
			gl.voucher_type, gl.voucher_no, gl.against_voucher_type,
			gl.against_voucher, gl.account_currency, gl.against,
			gl.party_type, gl.party,
			inv.name as InvName, inv.title as InvTitle, inv.posting_date as InvPostDate,
			pur.name as PurName, pur.title as PurTitle, pur.posting_date as PurPostDate,
			jnl.cheque_no as JnlRef, jnl.posting_date as JnlPostDate, jnl.title as JnlTitle,
			pay.name as PayName, pay.posting_date as PayPostDate, pay.title as PayTitle,
			cus.customer_name, cus.name as cusName,
			sup.supplier_name, sup.name as supName,
			emp.employee_name, emp.name as empName,
			stu.title as student_name, stu.name as stuName,
			member_name, mem.name as memName

		from `tabGL Entry` gl
			left join `tabSales Invoice` inv on gl.voucher_no = inv.name
			left join `tabPurchase Invoice` pur on gl.voucher_no = pur.name
			left join `tabJournal Entry` jnl on gl.voucher_no = jnl.name
			left join `tabPayment Entry` pay on gl.voucher_no = pay.name
			left join `tabCustomer` cus on gl.party = cus.name
			left join `tabSupplier` sup on gl.party = sup.name
			left join `tabEmployee` emp on gl.party = emp.name
			left join `tabStudent` stu on gl.party = stu.name
			left join `tabMember` mem on gl.party = mem.name
		where gl.company=%(company)s and gl.fiscal_year=%(fiscal_year)s
		{group_by_condition}
		order by GlPostDate, voucher_no""".format(
			group_by_condition=group_by_condition
		),
		filters,
		as_dict=1,
	)

	return gl_entries


def get_result_as_list(data, filters):
	result = []

	company_currency = frappe.get_cached_value("Company", filters.company, "default_currency")
	accounts = frappe.get_all(
		"Account", filters={"Company": filters.company}, fields=["name", "account_number"]
	)

	for d in data:

=======
def get_gl_entries(company, fiscal_year):
	gle = frappe.qb.DocType("GL Entry")
	sales_invoice = frappe.qb.DocType("Sales Invoice")
	purchase_invoice = frappe.qb.DocType("Purchase Invoice")
	journal_entry = frappe.qb.DocType("Journal Entry")
	payment_entry = frappe.qb.DocType("Payment Entry")
	customer = frappe.qb.DocType("Customer")
	supplier = frappe.qb.DocType("Supplier")
	employee = frappe.qb.DocType("Employee")

	debit = frappe.query_builder.functions.Sum(gle.debit).as_("debit")
	credit = frappe.query_builder.functions.Sum(gle.credit).as_("credit")
	debit_currency = frappe.query_builder.functions.Sum(gle.debit_in_account_currency).as_(
		"debitCurr"
	)
	credit_currency = frappe.query_builder.functions.Sum(gle.credit_in_account_currency).as_(
		"creditCurr"
	)

	query = (
		frappe.qb.from_(gle)
		.left_join(sales_invoice)
		.on(gle.voucher_no == sales_invoice.name)
		.left_join(purchase_invoice)
		.on(gle.voucher_no == purchase_invoice.name)
		.left_join(journal_entry)
		.on(gle.voucher_no == journal_entry.name)
		.left_join(payment_entry)
		.on(gle.voucher_no == payment_entry.name)
		.left_join(customer)
		.on(gle.party == customer.name)
		.left_join(supplier)
		.on(gle.party == supplier.name)
		.left_join(employee)
		.on(gle.party == employee.name)
		.select(
			gle.posting_date.as_("GlPostDate"),
			gle.name.as_("GlName"),
			gle.account,
			gle.transaction_date,
			debit,
			credit,
			debit_currency,
			credit_currency,
			gle.voucher_type,
			gle.voucher_no,
			gle.against_voucher_type,
			gle.against_voucher,
			gle.account_currency,
			gle.against,
			gle.party_type,
			gle.party,
			sales_invoice.name.as_("InvName"),
			sales_invoice.title.as_("InvTitle"),
			sales_invoice.posting_date.as_("InvPostDate"),
			purchase_invoice.name.as_("PurName"),
			purchase_invoice.title.as_("PurTitle"),
			purchase_invoice.posting_date.as_("PurPostDate"),
			journal_entry.cheque_no.as_("JnlRef"),
			journal_entry.posting_date.as_("JnlPostDate"),
			journal_entry.title.as_("JnlTitle"),
			payment_entry.name.as_("PayName"),
			payment_entry.posting_date.as_("PayPostDate"),
			payment_entry.title.as_("PayTitle"),
			customer.customer_name,
			customer.name.as_("cusName"),
			supplier.supplier_name,
			supplier.name.as_("supName"),
			employee.employee_name,
			employee.name.as_("empName"),
		)
		.where((gle.company == company) & (gle.fiscal_year == fiscal_year))
		.groupby(gle.voucher_type, gle.voucher_no, gle.account)
		.orderby(gle.posting_date, gle.voucher_no)
	)

	return query.run(as_dict=True)


def get_result(company, fiscal_year):
	data = get_gl_entries(company, fiscal_year)

	result = []

	company_currency = frappe.get_cached_value("Company", company, "default_currency")
	accounts = frappe.get_all(
		"Account", filters={"Company": company}, fields=["name", "account_number"]
	)

	for d in data:
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
		JournalCode = re.split("-|/|[0-9]", d.get("voucher_no"))[0]

		if d.get("voucher_no").startswith("{0}-".format(JournalCode)) or d.get("voucher_no").startswith(
			"{0}/".format(JournalCode)
		):
			EcritureNum = re.split("-|/", d.get("voucher_no"))[1]
		else:
<<<<<<< HEAD
			EcritureNum = re.search(
				r"{0}(\d+)".format(JournalCode), d.get("voucher_no"), re.IGNORECASE
			).group(1)
=======
			EcritureNum = re.search(r"{0}(\d+)".format(JournalCode), d.get("voucher_no"), re.IGNORECASE)[1]
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)

		EcritureDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")

		account_number = [
			account.account_number for account in accounts if account.name == d.get("account")
		]
		if account_number[0] is not None:
			CompteNum = account_number[0]
		else:
			frappe.throw(
				_(
					"Account number for account {0} is not available.<br> Please setup your Chart of Accounts correctly."
				).format(d.get("account"))
			)

		if d.get("party_type") == "Customer":
			CompAuxNum = d.get("cusName")
			CompAuxLib = d.get("customer_name")

		elif d.get("party_type") == "Supplier":
			CompAuxNum = d.get("supName")
			CompAuxLib = d.get("supplier_name")

		elif d.get("party_type") == "Employee":
			CompAuxNum = d.get("empName")
			CompAuxLib = d.get("employee_name")

		elif d.get("party_type") == "Student":
			CompAuxNum = d.get("stuName")
			CompAuxLib = d.get("student_name")

		elif d.get("party_type") == "Member":
			CompAuxNum = d.get("memName")
			CompAuxLib = d.get("member_name")

		else:
			CompAuxNum = ""
			CompAuxLib = ""

		ValidDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")

<<<<<<< HEAD
		PieceRef = d.get("voucher_no") if d.get("voucher_no") else "Sans Reference"
=======
		PieceRef = d.get("voucher_no") or "Sans Reference"
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)

		# EcritureLib is the reference title unless it is an opening entry
		if d.get("is_opening") == "Yes":
			EcritureLib = _("Opening Entry Journal")
		if d.get("voucher_type") == "Sales Invoice":
			EcritureLib = d.get("InvTitle")
		elif d.get("voucher_type") == "Purchase Invoice":
			EcritureLib = d.get("PurTitle")
		elif d.get("voucher_type") == "Journal Entry":
			EcritureLib = d.get("JnlTitle")
		elif d.get("voucher_type") == "Payment Entry":
			EcritureLib = d.get("PayTitle")
		else:
			EcritureLib = d.get("voucher_type")

		PieceDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")

		debit = "{:.2f}".format(d.get("debit")).replace(".", ",")

		credit = "{:.2f}".format(d.get("credit")).replace(".", ",")

		Idevise = d.get("account_currency")

		if Idevise != company_currency:
			Montantdevise = (
				"{:.2f}".format(d.get("debitCurr")).replace(".", ",")
				if d.get("debitCurr") != 0
				else "{:.2f}".format(d.get("creditCurr")).replace(".", ",")
			)
		else:
			Montantdevise = (
				"{:.2f}".format(d.get("debit")).replace(".", ",")
				if d.get("debit") != 0
				else "{:.2f}".format(d.get("credit")).replace(".", ",")
			)

		row = [
			JournalCode,
			d.get("voucher_type"),
			EcritureNum,
			EcritureDate,
			CompteNum,
			d.get("account"),
			CompAuxNum,
			CompAuxLib,
			PieceRef,
			PieceDate,
			EcritureLib,
			debit,
			credit,
			"",
			"",
			ValidDate,
			Montantdevise,
			Idevise,
		]

		result.append(row)

	return result
