# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
<<<<<<< HEAD
from frappe.utils import flt
=======
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, flt
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
<<<<<<< HEAD
from erpnext.accounts.utils import get_account_currency
=======
from erpnext.accounts.utils import get_account_currency, get_fiscal_year, validate_fiscal_year
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
from erpnext.controllers.accounts_controller import AccountsController


class PeriodClosingVoucher(AccountsController):
	def validate(self):
		self.validate_account_head()
		self.validate_posting_date()

	def on_submit(self):
		self.db_set("gle_processing_status", "In Progress")
<<<<<<< HEAD
		self.make_gl_entries()

	def on_cancel(self):
=======
		get_opening_entries = False

		if not frappe.db.exists(
			"Period Closing Voucher", {"company": self.company, "docstatus": 1, "name": ("!=", self.name)}
		):
			get_opening_entries = True

		self.make_gl_entries(get_opening_entries=get_opening_entries)

	def on_cancel(self):
		self.validate_future_closing_vouchers()
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
		self.db_set("gle_processing_status", "In Progress")
		self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry")
		gle_count = frappe.db.count(
			"GL Entry",
			{"voucher_type": "Period Closing Voucher", "voucher_no": self.name, "is_cancelled": 0},
		)
		if gle_count > 5000:
			frappe.enqueue(
				make_reverse_gl_entries,
				voucher_type="Period Closing Voucher",
				voucher_no=self.name,
				queue="long",
<<<<<<< HEAD
=======
				enqueue_after_commit=True,
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
			)
			frappe.msgprint(
				_("The GL Entries will be cancelled in the background, it can take a few minutes."), alert=True
			)
		else:
			make_reverse_gl_entries(voucher_type="Period Closing Voucher", voucher_no=self.name)

<<<<<<< HEAD
	def validate_account_head(self):
		closing_account_type = frappe.db.get_value("Account", self.closing_account_head, "root_type")
=======
		self.delete_closing_entries()

	def validate_future_closing_vouchers(self):
		if frappe.db.exists(
			"Period Closing Voucher",
			{"posting_date": (">", self.posting_date), "docstatus": 1, "company": self.company},
		):
			frappe.throw(
				_(
					"You can not cancel this Period Closing Voucher, please cancel the future Period Closing Vouchers first"
				)
			)

	def delete_closing_entries(self):
		closing_balance = frappe.qb.DocType("Account Closing Balance")
		frappe.qb.from_(closing_balance).delete().where(
			closing_balance.period_closing_voucher == self.name
		).run()

	def validate_account_head(self):
		closing_account_type = frappe.get_cached_value("Account", self.closing_account_head, "root_type")
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)

		if closing_account_type not in ["Liability", "Equity"]:
			frappe.throw(
				_("Closing Account {0} must be of type Liability / Equity").format(self.closing_account_head)
			)

		account_currency = get_account_currency(self.closing_account_head)
		company_currency = frappe.get_cached_value("Company", self.company, "default_currency")
		if account_currency != company_currency:
			frappe.throw(_("Currency of the Closing Account must be {0}").format(company_currency))

	def validate_posting_date(self):
<<<<<<< HEAD
		from erpnext.accounts.utils import get_fiscal_year, validate_fiscal_year

=======
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
		validate_fiscal_year(
			self.posting_date, self.fiscal_year, self.company, label=_("Posting Date"), doc=self
		)

		self.year_start_date = get_fiscal_year(
			self.posting_date, self.fiscal_year, company=self.company
		)[1]

<<<<<<< HEAD
=======
		self.check_if_previous_year_closed()

>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
		pce = frappe.db.sql(
			"""select name from `tabPeriod Closing Voucher`
			where posting_date > %s and fiscal_year = %s and docstatus = 1 and company = %s""",
			(self.posting_date, self.fiscal_year, self.company),
		)
		if pce and pce[0][0]:
			frappe.throw(
				_("Another Period Closing Entry {0} has been made after {1}").format(
					pce[0][0], self.posting_date
				)
			)

<<<<<<< HEAD
	def make_gl_entries(self):
		gl_entries = self.get_gl_entries()
		if gl_entries:
			if len(gl_entries) > 5000:
				frappe.enqueue(process_gl_entries, gl_entries=gl_entries, queue="long")
				frappe.msgprint(
					_("The GL Entries will be processed in the background, it can take a few minutes."),
					alert=True,
				)
			else:
				process_gl_entries(gl_entries)
=======
	def check_if_previous_year_closed(self):
		last_year_closing = add_days(self.year_start_date, -1)

		previous_fiscal_year = get_fiscal_year(last_year_closing, company=self.company, boolean=True)

		if previous_fiscal_year and not frappe.db.exists(
			"GL Entry", {"posting_date": ("<=", last_year_closing), "company": self.company}
		):
			return

		if previous_fiscal_year and not frappe.db.exists(
			"Period Closing Voucher",
			{"posting_date": ("<=", last_year_closing), "docstatus": 1, "company": self.company},
		):
			frappe.throw(_("Previous Year is not closed, please close it first"))

	def make_gl_entries(self, get_opening_entries=False):
		gl_entries = self.get_gl_entries()
		closing_entries = self.get_grouped_gl_entries(get_opening_entries=get_opening_entries)
		if len(gl_entries) > 5000:
			frappe.enqueue(
				process_gl_entries,
				gl_entries=gl_entries,
				closing_entries=closing_entries,
				voucher_name=self.name,
				company=self.company,
				closing_date=self.posting_date,
				queue="long",
			)
			frappe.msgprint(
				_("The GL Entries will be processed in the background, it can take a few minutes."),
				alert=True,
			)
		else:
			process_gl_entries(gl_entries, closing_entries, self.name, self.company, self.posting_date)

	def get_grouped_gl_entries(self, get_opening_entries=False):
		closing_entries = []
		for acc in self.get_balances_based_on_dimensions(
			group_by_account=True, for_aggregation=True, get_opening_entries=get_opening_entries
		):
			closing_entries.append(self.get_closing_entries(acc))

		return closing_entries
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)

	def get_gl_entries(self):
		gl_entries = []

		# pl account
<<<<<<< HEAD
		for acc in self.get_pl_balances_based_on_dimensions(group_by_account=True):
=======
		for acc in self.get_balances_based_on_dimensions(
			group_by_account=True, report_type="Profit and Loss"
		):
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
			if flt(acc.bal_in_company_currency):
				gl_entries.append(self.get_gle_for_pl_account(acc))

		# closing liability account
<<<<<<< HEAD
		for acc in self.get_pl_balances_based_on_dimensions(group_by_account=False):
=======
		for acc in self.get_balances_based_on_dimensions(
			group_by_account=False, report_type="Profit and Loss"
		):
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
			if flt(acc.bal_in_company_currency):
				gl_entries.append(self.get_gle_for_closing_account(acc))

		return gl_entries

	def get_gle_for_pl_account(self, acc):
		gl_entry = self.get_gl_dict(
			{
<<<<<<< HEAD
=======
				"company": self.company,
				"closing_date": self.posting_date,
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
				"account": acc.account,
				"cost_center": acc.cost_center,
				"finance_book": acc.finance_book,
				"account_currency": acc.account_currency,
				"debit_in_account_currency": abs(flt(acc.bal_in_account_currency))
				if flt(acc.bal_in_account_currency) < 0
				else 0,
				"debit": abs(flt(acc.bal_in_company_currency)) if flt(acc.bal_in_company_currency) < 0 else 0,
				"credit_in_account_currency": abs(flt(acc.bal_in_account_currency))
				if flt(acc.bal_in_account_currency) > 0
				else 0,
				"credit": abs(flt(acc.bal_in_company_currency)) if flt(acc.bal_in_company_currency) > 0 else 0,
<<<<<<< HEAD
=======
				"is_period_closing_voucher_entry": 1,
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
			},
			item=acc,
		)
		self.update_default_dimensions(gl_entry, acc)
		return gl_entry

	def get_gle_for_closing_account(self, acc):
		gl_entry = self.get_gl_dict(
			{
<<<<<<< HEAD
=======
				"company": self.company,
				"closing_date": self.posting_date,
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
				"account": self.closing_account_head,
				"cost_center": acc.cost_center,
				"finance_book": acc.finance_book,
				"account_currency": acc.account_currency,
				"debit_in_account_currency": abs(flt(acc.bal_in_account_currency))
				if flt(acc.bal_in_account_currency) > 0
				else 0,
				"debit": abs(flt(acc.bal_in_company_currency)) if flt(acc.bal_in_company_currency) > 0 else 0,
				"credit_in_account_currency": abs(flt(acc.bal_in_account_currency))
				if flt(acc.bal_in_account_currency) < 0
				else 0,
				"credit": abs(flt(acc.bal_in_company_currency)) if flt(acc.bal_in_company_currency) < 0 else 0,
<<<<<<< HEAD
=======
				"is_period_closing_voucher_entry": 1,
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
			},
			item=acc,
		)
		self.update_default_dimensions(gl_entry, acc)
		return gl_entry

<<<<<<< HEAD
=======
	def get_closing_entries(self, acc):
		closing_entry = self.get_gl_dict(
			{
				"company": self.company,
				"closing_date": self.posting_date,
				"period_closing_voucher": self.name,
				"account": acc.account,
				"cost_center": acc.cost_center,
				"finance_book": acc.finance_book,
				"account_currency": acc.account_currency,
				"debit_in_account_currency": flt(acc.debit_in_account_currency),
				"debit": flt(acc.debit),
				"credit_in_account_currency": flt(acc.credit_in_account_currency),
				"credit": flt(acc.credit),
			},
			item=acc,
		)

		for dimension in self.accounting_dimensions:
			closing_entry.update({dimension: acc.get(dimension)})

		return closing_entry

>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
	def update_default_dimensions(self, gl_entry, acc):
		if not self.accounting_dimensions:
			self.accounting_dimensions = get_accounting_dimensions()

		for dimension in self.accounting_dimensions:
			gl_entry.update({dimension: acc.get(dimension)})

<<<<<<< HEAD
	def get_pl_balances_based_on_dimensions(self, group_by_account=False):
		"""Get balance for dimension-wise pl accounts"""

		dimension_fields = ["t1.cost_center", "t1.finance_book"]

		self.accounting_dimensions = get_accounting_dimensions()
		for dimension in self.accounting_dimensions:
			dimension_fields.append("t1.{0}".format(dimension))

		if group_by_account:
			dimension_fields.append("t1.account")

		return frappe.db.sql(
			"""
			select
				t2.account_currency,
				{dimension_fields},
				sum(t1.debit_in_account_currency) - sum(t1.credit_in_account_currency) as bal_in_account_currency,
				sum(t1.debit) - sum(t1.credit) as bal_in_company_currency
			from `tabGL Entry` t1, `tabAccount` t2
			where
				t1.is_cancelled = 0
				and t1.account = t2.name
				and t2.report_type = 'Profit and Loss'
				and t2.docstatus < 2
				and t2.company = %s
				and t1.posting_date between %s and %s
			group by {dimension_fields}
		""".format(
				dimension_fields=", ".join(dimension_fields)
			),
			(self.company, self.get("year_start_date"), self.posting_date),
			as_dict=1,
		)


def process_gl_entries(gl_entries):
	from erpnext.accounts.general_ledger import make_gl_entries

	try:
		make_gl_entries(gl_entries, merge_entries=False)
		frappe.db.set_value(
			"Period Closing Voucher", gl_entries[0].get("voucher_no"), "gle_processing_status", "Completed"
		)
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(e)
		frappe.db.set_value(
			"Period Closing Voucher", gl_entries[0].get("voucher_no"), "gle_processing_status", "Failed"
		)
=======
	def get_balances_based_on_dimensions(
		self, group_by_account=False, report_type=None, for_aggregation=False, get_opening_entries=False
	):
		"""Get balance for dimension-wise pl accounts"""

		qb_dimension_fields = ["cost_center", "finance_book", "project"]

		self.accounting_dimensions = get_accounting_dimensions()
		for dimension in self.accounting_dimensions:
			qb_dimension_fields.append(dimension)

		if group_by_account:
			qb_dimension_fields.append("account")

		account_filters = {
			"company": self.company,
			"is_group": 0,
		}

		if report_type:
			account_filters.update({"report_type": report_type})

		accounts = frappe.get_all("Account", filters=account_filters, pluck="name")

		gl_entry = frappe.qb.DocType("GL Entry")
		query = frappe.qb.from_(gl_entry).select(gl_entry.account, gl_entry.account_currency)

		if not for_aggregation:
			query = query.select(
				(Sum(gl_entry.debit_in_account_currency) - Sum(gl_entry.credit_in_account_currency)).as_(
					"bal_in_account_currency"
				),
				(Sum(gl_entry.debit) - Sum(gl_entry.credit)).as_("bal_in_company_currency"),
			)
		else:
			query = query.select(
				(Sum(gl_entry.debit_in_account_currency)).as_("debit_in_account_currency"),
				(Sum(gl_entry.credit_in_account_currency)).as_("credit_in_account_currency"),
				(Sum(gl_entry.debit)).as_("debit"),
				(Sum(gl_entry.credit)).as_("credit"),
			)

		for dimension in qb_dimension_fields:
			query = query.select(gl_entry[dimension])

		query = query.where(
			(gl_entry.company == self.company)
			& (gl_entry.is_cancelled == 0)
			& (gl_entry.account.isin(accounts))
		)

		if get_opening_entries:
			query = query.where(
				gl_entry.posting_date.between(self.get("year_start_date"), self.posting_date)
				| gl_entry.is_opening
				== "Yes"
			)
		else:
			query = query.where(
				gl_entry.posting_date.between(self.get("year_start_date"), self.posting_date)
				& gl_entry.is_opening
				== "No"
			)

		if for_aggregation:
			query = query.where(gl_entry.voucher_type != "Period Closing Voucher")

		for dimension in qb_dimension_fields:
			query = query.groupby(gl_entry[dimension])

		return query.run(as_dict=1)


def process_gl_entries(gl_entries, closing_entries, voucher_name, company, closing_date):
	from erpnext.accounts.doctype.account_closing_balance.account_closing_balance import (
		make_closing_entries,
	)
	from erpnext.accounts.general_ledger import make_gl_entries

	try:
		if gl_entries:
			make_gl_entries(gl_entries, merge_entries=False)

		make_closing_entries(gl_entries + closing_entries, voucher_name, company, closing_date)
		frappe.db.set_value("Period Closing Voucher", voucher_name, "gle_processing_status", "Completed")
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(e)
		frappe.db.set_value("Period Closing Voucher", voucher_name, "gle_processing_status", "Failed")
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)


def make_reverse_gl_entries(voucher_type, voucher_no):
	from erpnext.accounts.general_ledger import make_reverse_gl_entries

	try:
		make_reverse_gl_entries(voucher_type=voucher_type, voucher_no=voucher_no)
		frappe.db.set_value("Period Closing Voucher", voucher_no, "gle_processing_status", "Completed")
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(e)
		frappe.db.set_value("Period Closing Voucher", voucher_no, "gle_processing_status", "Failed")
