# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from operator import itemgetter
from typing import Any, Dict, List, Optional, TypedDict

import frappe
from frappe import _
<<<<<<< HEAD
from frappe.query_builder.functions import Coalesce, CombineDatetime
from frappe.utils import cint, date_diff, flt, getdate
=======
from frappe.query_builder import Order
from frappe.query_builder.functions import Coalesce, CombineDatetime
from frappe.utils import add_days, cint, date_diff, flt, getdate
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
from frappe.utils.nestedset import get_descendants_of

import erpnext
from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter
from erpnext.stock.report.stock_ageing.stock_ageing import FIFOSlots, get_average_age
<<<<<<< HEAD
from erpnext.stock.utils import add_additional_uom_columns, is_reposting_item_valuation_in_progress
=======
from erpnext.stock.utils import add_additional_uom_columns
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)


class StockBalanceFilter(TypedDict):
	company: Optional[str]
	from_date: str
	to_date: str
	item_group: Optional[str]
	item: Optional[str]
	warehouse: Optional[str]
	warehouse_type: Optional[str]
	include_uom: Optional[str]  # include extra info in converted UOM
	show_stock_ageing_data: bool
	show_variant_attributes: bool


SLEntry = Dict[str, Any]


def execute(filters: Optional[StockBalanceFilter] = None):
<<<<<<< HEAD
	is_reposting_item_valuation_in_progress()
	if not filters:
		filters = {}

	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	include_uom = filters.get("include_uom")
	columns = get_columns(filters)
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)

	if filters.get("show_stock_ageing_data"):
		filters["show_warehouse_wise_stock"] = True
		item_wise_fifo_queue = FIFOSlots(filters, sle).generate()

	# if no stock ledger entry found return
	if not sle:
		return columns, []

	iwb_map = get_item_warehouse_map(filters, sle)
	item_map = get_item_details(items, sle, filters)
	item_reorder_detail_map = get_item_reorder_details(item_map.keys())

	data = []
	conversion_factors = {}

	_func = itemgetter(1)

	to_date = filters.get("to_date")

	for group_by_key in iwb_map:
		item = group_by_key[1]
		warehouse = group_by_key[2]
		company = group_by_key[0]

		if item_map.get(item):
			qty_dict = iwb_map[group_by_key]
			item_reorder_level = 0
			item_reorder_qty = 0
			if item + warehouse in item_reorder_detail_map:
				item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
				item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]

			report_data = {
				"currency": company_currency,
				"item_code": item,
				"warehouse": warehouse,
				"company": company,
				"reorder_level": item_reorder_level,
				"reorder_qty": item_reorder_qty,
			}
			report_data.update(item_map[item])
			report_data.update(qty_dict)

			if include_uom:
				conversion_factors.setdefault(item, item_map[item].conversion_factor)

			if filters.get("show_stock_ageing_data"):
				fifo_queue = item_wise_fifo_queue[(item, warehouse)].get("fifo_queue")

				stock_ageing_data = {"average_age": 0, "earliest_age": 0, "latest_age": 0}
				if fifo_queue:
					fifo_queue = sorted(filter(_func, fifo_queue), key=_func)
					if not fifo_queue:
						continue

					stock_ageing_data["average_age"] = get_average_age(fifo_queue, to_date)
					stock_ageing_data["earliest_age"] = date_diff(to_date, fifo_queue[0][1])
					stock_ageing_data["latest_age"] = date_diff(to_date, fifo_queue[-1][1])

				report_data.update(stock_ageing_data)

			data.append(report_data)

	add_additional_uom_columns(columns, data, include_uom, conversion_factors)
	return columns, data


def get_columns(filters: StockBalanceFilter):
	"""return columns"""
	columns = [
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 100,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 100,
		},
	]

	for dimension in get_inventory_dimensions():
		columns.append(
			{
				"label": _(dimension.doctype),
				"fieldname": dimension.fieldname,
				"fieldtype": "Link",
				"options": dimension.doctype,
				"width": 110,
			}
		)

	columns.extend(
		[
			{
				"label": _("Stock UOM"),
				"fieldname": "stock_uom",
				"fieldtype": "Link",
				"options": "UOM",
				"width": 90,
			},
			{
				"label": _("Balance Qty"),
				"fieldname": "bal_qty",
				"fieldtype": "Float",
				"width": 100,
				"convertible": "qty",
			},
			{
				"label": _("Balance Value"),
				"fieldname": "bal_val",
				"fieldtype": "Currency",
				"width": 100,
				"options": "currency",
			},
			{
				"label": _("Opening Qty"),
				"fieldname": "opening_qty",
				"fieldtype": "Float",
				"width": 100,
				"convertible": "qty",
			},
			{
				"label": _("Opening Value"),
				"fieldname": "opening_val",
				"fieldtype": "Currency",
				"width": 110,
				"options": "currency",
			},
			{
				"label": _("In Qty"),
				"fieldname": "in_qty",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{"label": _("In Value"), "fieldname": "in_val", "fieldtype": "Float", "width": 80},
			{
				"label": _("Out Qty"),
				"fieldname": "out_qty",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{"label": _("Out Value"), "fieldname": "out_val", "fieldtype": "Float", "width": 80},
			{
				"label": _("Valuation Rate"),
				"fieldname": "val_rate",
				"fieldtype": "Currency",
				"width": 90,
				"convertible": "rate",
				"options": "currency",
			},
			{
				"label": _("Reorder Level"),
				"fieldname": "reorder_level",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{
				"label": _("Reorder Qty"),
				"fieldname": "reorder_qty",
				"fieldtype": "Float",
				"width": 80,
				"convertible": "qty",
			},
			{
				"label": _("Company"),
				"fieldname": "company",
				"fieldtype": "Link",
				"options": "Company",
				"width": 100,
			},
		]
	)

	if filters.get("show_stock_ageing_data"):
		columns += [
			{"label": _("Average Age"), "fieldname": "average_age", "width": 100},
			{"label": _("Earliest Age"), "fieldname": "earliest_age", "width": 100},
			{"label": _("Latest Age"), "fieldname": "latest_age", "width": 100},
		]

	if filters.get("show_variant_attributes"):
		columns += [
			{"label": att_name, "fieldname": att_name, "width": 100}
			for att_name in get_variants_attributes()
		]

	return columns


def apply_conditions(query, filters):
	sle = frappe.qb.DocType("Stock Ledger Entry")
	warehouse_table = frappe.qb.DocType("Warehouse")

	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if to_date := filters.get("to_date"):
		query = query.where(sle.posting_date <= to_date)
	else:
		frappe.throw(_("'To Date' is required"))

	if company := filters.get("company"):
		query = query.where(sle.company == company)

	if filters.get("warehouse"):
		query = apply_warehouse_filter(query, sle, filters)
	elif warehouse_type := filters.get("warehouse_type"):
		query = (
			query.join(warehouse_table)
			.on(warehouse_table.name == sle.warehouse)
			.where(warehouse_table.warehouse_type == warehouse_type)
		)

	return query


def get_stock_ledger_entries(filters: StockBalanceFilter, items: List[str]) -> List[SLEntry]:
	sle = frappe.qb.DocType("Stock Ledger Entry")

	query = (
		frappe.qb.from_(sle)
		.select(
			sle.item_code,
			sle.warehouse,
			sle.posting_date,
			sle.actual_qty,
			sle.valuation_rate,
			sle.company,
			sle.voucher_type,
			sle.qty_after_transaction,
			sle.stock_value_difference,
			sle.item_code.as_("name"),
			sle.voucher_no,
			sle.stock_value,
			sle.batch_no,
		)
		.where((sle.docstatus < 2) & (sle.is_cancelled == 0))
		.orderby(CombineDatetime(sle.posting_date, sle.posting_time))
		.orderby(sle.creation)
		.orderby(sle.actual_qty)
	)

	inventory_dimension_fields = get_inventory_dimension_fields()
	if inventory_dimension_fields:
		for fieldname in inventory_dimension_fields:
			query = query.select(fieldname)
			if fieldname in filters and filters.get(fieldname):
				query = query.where(sle[fieldname].isin(filters.get(fieldname)))

	if items:
		query = query.where(sle.item_code.isin(items))

	query = apply_conditions(query, filters)
	return query.run(as_dict=True)


def get_opening_vouchers(to_date):
	opening_vouchers = {"Stock Entry": [], "Stock Reconciliation": []}

	se = frappe.qb.DocType("Stock Entry")
	sr = frappe.qb.DocType("Stock Reconciliation")

	vouchers_data = (
		frappe.qb.from_(
			(
				frappe.qb.from_(se)
				.select(se.name, Coalesce("Stock Entry").as_("voucher_type"))
				.where((se.docstatus == 1) & (se.posting_date <= to_date) & (se.is_opening == "Yes"))
			)
			+ (
				frappe.qb.from_(sr)
				.select(sr.name, Coalesce("Stock Reconciliation").as_("voucher_type"))
				.where((sr.docstatus == 1) & (sr.posting_date <= to_date) & (sr.purpose == "Opening Stock"))
			)
		).select("voucher_type", "name")
	).run(as_dict=True)

	if vouchers_data:
		for d in vouchers_data:
			opening_vouchers[d.voucher_type].append(d.name)

	return opening_vouchers


def get_inventory_dimension_fields():
	return [dimension.fieldname for dimension in get_inventory_dimensions()]


def get_item_warehouse_map(filters: StockBalanceFilter, sle: List[SLEntry]):
	iwb_map = {}
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))
	opening_vouchers = get_opening_vouchers(to_date)
	float_precision = cint(frappe.db.get_default("float_precision")) or 3
	inventory_dimensions = get_inventory_dimension_fields()

	for d in sle:
		group_by_key = get_group_by_key(d, filters, inventory_dimensions)
		if group_by_key not in iwb_map:
			iwb_map[group_by_key] = frappe._dict(
				{
					"opening_qty": 0.0,
					"opening_val": 0.0,
					"in_qty": 0.0,
					"in_val": 0.0,
					"out_qty": 0.0,
					"out_val": 0.0,
					"bal_qty": 0.0,
					"bal_val": 0.0,
					"val_rate": 0.0,
				}
			)

		qty_dict = iwb_map[group_by_key]
		for field in inventory_dimensions:
			qty_dict[field] = d.get(field)

		if d.voucher_type == "Stock Reconciliation" and not d.batch_no:
			qty_diff = flt(d.qty_after_transaction) - flt(qty_dict.bal_qty)
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date < from_date or d.voucher_no in opening_vouchers.get(d.voucher_type, []):
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if flt(qty_diff, float_precision) >= 0:
=======
	return StockBalanceReport(filters).run()


class StockBalanceReport(object):
	def __init__(self, filters: Optional[StockBalanceFilter]) -> None:
		self.filters = filters
		self.from_date = getdate(filters.get("from_date"))
		self.to_date = getdate(filters.get("to_date"))

		self.start_from = None
		self.data = []
		self.columns = []
		self.sle_entries: List[SLEntry] = []
		self.set_company_currency()

	def set_company_currency(self) -> None:
		if self.filters.get("company"):
			self.company_currency = erpnext.get_company_currency(self.filters.get("company"))
		else:
			self.company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	def run(self):
		self.float_precision = cint(frappe.db.get_default("float_precision")) or 3

		self.inventory_dimensions = self.get_inventory_dimension_fields()
		self.prepare_opening_data_from_closing_balance()
		self.prepare_stock_ledger_entries()
		self.prepare_new_data()

		if not self.columns:
			self.columns = self.get_columns()

		self.add_additional_uom_columns()

		return self.columns, self.data

	def prepare_opening_data_from_closing_balance(self) -> None:
		self.opening_data = frappe._dict({})

		closing_balance = self.get_closing_balance()
		if not closing_balance:
			return

		self.start_from = add_days(closing_balance[0].to_date, 1)
		res = frappe.get_doc("Closing Stock Balance", closing_balance[0].name).get_prepared_data()

		for entry in res.data:
			entry = frappe._dict(entry)

			group_by_key = self.get_group_by_key(entry)
			if group_by_key not in self.opening_data:
				self.opening_data.setdefault(group_by_key, entry)

	def prepare_new_data(self):
		if not self.sle_entries:
			return

		if self.filters.get("show_stock_ageing_data"):
			self.filters["show_warehouse_wise_stock"] = True
			item_wise_fifo_queue = FIFOSlots(self.filters, self.sle_entries).generate()

		_func = itemgetter(1)

		self.item_warehouse_map = self.get_item_warehouse_map()

		variant_values = {}
		if self.filters.get("show_variant_attributes"):
			variant_values = self.get_variant_values_for()

		for key, report_data in self.item_warehouse_map.items():
			if variant_data := variant_values.get(report_data.item_code):
				report_data.update(variant_data)

			if self.filters.get("show_stock_ageing_data"):
				opening_fifo_queue = self.get_opening_fifo_queue(report_data) or []

				fifo_queue = []
				if fifo_queue := item_wise_fifo_queue.get((report_data.item_code, report_data.warehouse)):
					fifo_queue = fifo_queue.get("fifo_queue")

				if fifo_queue:
					opening_fifo_queue.extend(fifo_queue)

				stock_ageing_data = {"average_age": 0, "earliest_age": 0, "latest_age": 0}
				if opening_fifo_queue:
					fifo_queue = sorted(filter(_func, opening_fifo_queue), key=_func)
					if not fifo_queue:
						continue

					to_date = self.to_date
					stock_ageing_data["average_age"] = get_average_age(fifo_queue, to_date)
					stock_ageing_data["earliest_age"] = date_diff(to_date, fifo_queue[0][1])
					stock_ageing_data["latest_age"] = date_diff(to_date, fifo_queue[-1][1])
					stock_ageing_data["fifo_queue"] = fifo_queue

				report_data.update(stock_ageing_data)

			self.data.append(report_data)

	def get_item_warehouse_map(self):
		item_warehouse_map = {}
		self.opening_vouchers = self.get_opening_vouchers()

		for entry in self.sle_entries:
			group_by_key = self.get_group_by_key(entry)
			if group_by_key not in item_warehouse_map:
				self.initialize_data(item_warehouse_map, group_by_key, entry)

			self.prepare_item_warehouse_map(item_warehouse_map, entry, group_by_key)

			if self.opening_data.get(group_by_key):
				del self.opening_data[group_by_key]

		for group_by_key, entry in self.opening_data.items():
			if group_by_key not in item_warehouse_map:
				self.initialize_data(item_warehouse_map, group_by_key, entry)

		item_warehouse_map = filter_items_with_no_transactions(
			item_warehouse_map, self.float_precision, self.inventory_dimensions
		)

		return item_warehouse_map

	def prepare_item_warehouse_map(self, item_warehouse_map, entry, group_by_key):
		qty_dict = item_warehouse_map[group_by_key]
		for field in self.inventory_dimensions:
			qty_dict[field] = entry.get(field)

		if entry.voucher_type == "Stock Reconciliation" and (not entry.batch_no or entry.serial_no):
			qty_diff = flt(entry.qty_after_transaction) - flt(qty_dict.bal_qty)
		else:
			qty_diff = flt(entry.actual_qty)

		value_diff = flt(entry.stock_value_difference)

		if entry.posting_date < self.from_date or entry.voucher_no in self.opening_vouchers.get(
			entry.voucher_type, []
		):
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif entry.posting_date >= self.from_date and entry.posting_date <= self.to_date:

			if flt(qty_diff, self.float_precision) >= 0:
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
				qty_dict.in_qty += qty_diff
				qty_dict.in_val += value_diff
			else:
				qty_dict.out_qty += abs(qty_diff)
				qty_dict.out_val += abs(value_diff)

<<<<<<< HEAD
		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff

	iwb_map = filter_items_with_no_transactions(iwb_map, float_precision, inventory_dimensions)

	return iwb_map


def get_group_by_key(row, filters, inventory_dimension_fields) -> tuple:
	group_by_key = [row.company, row.item_code, row.warehouse]

	for fieldname in inventory_dimension_fields:
		if filters.get(fieldname):
			group_by_key.append(row.get(fieldname))

	return tuple(group_by_key)


def filter_items_with_no_transactions(iwb_map, float_precision: float, inventory_dimensions: list):
=======
		qty_dict.val_rate = entry.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff

	def initialize_data(self, item_warehouse_map, group_by_key, entry):
		opening_data = self.opening_data.get(group_by_key, {})

		item_warehouse_map[group_by_key] = frappe._dict(
			{
				"item_code": entry.item_code,
				"warehouse": entry.warehouse,
				"item_group": entry.item_group,
				"company": entry.company,
				"currency": self.company_currency,
				"stock_uom": entry.stock_uom,
				"item_name": entry.item_name,
				"opening_qty": opening_data.get("bal_qty") or 0.0,
				"opening_val": opening_data.get("bal_val") or 0.0,
				"opening_fifo_queue": opening_data.get("fifo_queue") or [],
				"in_qty": 0.0,
				"in_val": 0.0,
				"out_qty": 0.0,
				"out_val": 0.0,
				"bal_qty": opening_data.get("bal_qty") or 0.0,
				"bal_val": opening_data.get("bal_val") or 0.0,
				"val_rate": 0.0,
			}
		)

	def get_group_by_key(self, row) -> tuple:
		group_by_key = [row.company, row.item_code, row.warehouse]

		for fieldname in self.inventory_dimensions:
			if self.filters.get(fieldname):
				group_by_key.append(row.get(fieldname))

		return tuple(group_by_key)

	def get_closing_balance(self) -> List[Dict[str, Any]]:
		if self.filters.get("ignore_closing_balance"):
			return []

		table = frappe.qb.DocType("Closing Stock Balance")

		query = (
			frappe.qb.from_(table)
			.select(table.name, table.to_date)
			.where(
				(table.docstatus == 1)
				& (table.company == self.filters.company)
				& ((table.to_date <= self.from_date))
			)
			.orderby(table.to_date, order=Order.desc)
			.limit(1)
		)

		for fieldname in ["warehouse", "item_code", "item_group", "warehouse_type"]:
			if self.filters.get(fieldname):
				query = query.where(table[fieldname] == self.filters.get(fieldname))

		return query.run(as_dict=True)

	def prepare_stock_ledger_entries(self):
		sle = frappe.qb.DocType("Stock Ledger Entry")
		item_table = frappe.qb.DocType("Item")

		query = (
			frappe.qb.from_(sle)
			.inner_join(item_table)
			.on(sle.item_code == item_table.name)
			.select(
				sle.item_code,
				sle.warehouse,
				sle.posting_date,
				sle.actual_qty,
				sle.valuation_rate,
				sle.company,
				sle.voucher_type,
				sle.qty_after_transaction,
				sle.stock_value_difference,
				sle.item_code.as_("name"),
				sle.voucher_no,
				sle.stock_value,
				sle.batch_no,
				sle.serial_no,
				item_table.item_group,
				item_table.stock_uom,
				item_table.item_name,
			)
			.where((sle.docstatus < 2) & (sle.is_cancelled == 0))
			.orderby(CombineDatetime(sle.posting_date, sle.posting_time))
			.orderby(sle.creation)
			.orderby(sle.actual_qty)
		)

		query = self.apply_inventory_dimensions_filters(query, sle)
		query = self.apply_warehouse_filters(query, sle)
		query = self.apply_items_filters(query, item_table)
		query = self.apply_date_filters(query, sle)

		if self.filters.get("company"):
			query = query.where(sle.company == self.filters.get("company"))

		self.sle_entries = query.run(as_dict=True)

	def apply_inventory_dimensions_filters(self, query, sle) -> str:
		inventory_dimension_fields = self.get_inventory_dimension_fields()
		if inventory_dimension_fields:
			for fieldname in inventory_dimension_fields:
				query = query.select(fieldname)
				if self.filters.get(fieldname):
					query = query.where(sle[fieldname].isin(self.filters.get(fieldname)))

		return query

	def apply_warehouse_filters(self, query, sle) -> str:
		warehouse_table = frappe.qb.DocType("Warehouse")

		if self.filters.get("warehouse"):
			query = apply_warehouse_filter(query, sle, self.filters)
		elif warehouse_type := self.filters.get("warehouse_type"):
			query = (
				query.join(warehouse_table)
				.on(warehouse_table.name == sle.warehouse)
				.where(warehouse_table.warehouse_type == warehouse_type)
			)

		return query

	def apply_items_filters(self, query, item_table) -> str:
		if item_group := self.filters.get("item_group"):
			children = get_descendants_of("Item Group", item_group, ignore_permissions=True)
			query = query.where(item_table.item_group.isin(children + [item_group]))

		for field in ["item_code", "brand"]:
			if not self.filters.get(field):
				continue

			query = query.where(item_table[field] == self.filters.get(field))

		return query

	def apply_date_filters(self, query, sle) -> str:
		if not self.filters.ignore_closing_balance and self.start_from:
			query = query.where(sle.posting_date >= self.start_from)

		if self.to_date:
			query = query.where(sle.posting_date <= self.to_date)

		return query

	def get_columns(self):
		columns = [
			{
				"label": _("Item"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 100,
			},
			{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
			{
				"label": _("Item Group"),
				"fieldname": "item_group",
				"fieldtype": "Link",
				"options": "Item Group",
				"width": 100,
			},
			{
				"label": _("Warehouse"),
				"fieldname": "warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 100,
			},
		]

		for dimension in get_inventory_dimensions():
			columns.append(
				{
					"label": _(dimension.doctype),
					"fieldname": dimension.fieldname,
					"fieldtype": "Link",
					"options": dimension.doctype,
					"width": 110,
				}
			)

		columns.extend(
			[
				{
					"label": _("Stock UOM"),
					"fieldname": "stock_uom",
					"fieldtype": "Link",
					"options": "UOM",
					"width": 90,
				},
				{
					"label": _("Balance Qty"),
					"fieldname": "bal_qty",
					"fieldtype": "Float",
					"width": 100,
					"convertible": "qty",
				},
				{
					"label": _("Balance Value"),
					"fieldname": "bal_val",
					"fieldtype": "Currency",
					"width": 100,
					"options": "currency",
				},
				{
					"label": _("Opening Qty"),
					"fieldname": "opening_qty",
					"fieldtype": "Float",
					"width": 100,
					"convertible": "qty",
				},
				{
					"label": _("Opening Value"),
					"fieldname": "opening_val",
					"fieldtype": "Currency",
					"width": 110,
					"options": "currency",
				},
				{
					"label": _("In Qty"),
					"fieldname": "in_qty",
					"fieldtype": "Float",
					"width": 80,
					"convertible": "qty",
				},
				{"label": _("In Value"), "fieldname": "in_val", "fieldtype": "Float", "width": 80},
				{
					"label": _("Out Qty"),
					"fieldname": "out_qty",
					"fieldtype": "Float",
					"width": 80,
					"convertible": "qty",
				},
				{"label": _("Out Value"), "fieldname": "out_val", "fieldtype": "Float", "width": 80},
				{
					"label": _("Valuation Rate"),
					"fieldname": "val_rate",
					"fieldtype": "Currency",
					"width": 90,
					"convertible": "rate",
					"options": "currency",
				},
				{
					"label": _("Company"),
					"fieldname": "company",
					"fieldtype": "Link",
					"options": "Company",
					"width": 100,
				},
			]
		)

		if self.filters.get("show_stock_ageing_data"):
			columns += [
				{"label": _("Average Age"), "fieldname": "average_age", "width": 100},
				{"label": _("Earliest Age"), "fieldname": "earliest_age", "width": 100},
				{"label": _("Latest Age"), "fieldname": "latest_age", "width": 100},
			]

		if self.filters.get("show_variant_attributes"):
			columns += [
				{"label": att_name, "fieldname": att_name, "width": 100}
				for att_name in get_variants_attributes()
			]

		return columns

	def add_additional_uom_columns(self):
		if not self.filters.get("include_uom"):
			return

		conversion_factors = self.get_itemwise_conversion_factor()
		add_additional_uom_columns(self.columns, self.data, self.filters.include_uom, conversion_factors)

	def get_itemwise_conversion_factor(self):
		items = []
		if self.filters.item_code or self.filters.item_group:
			items = [d.item_code for d in self.data]

		table = frappe.qb.DocType("UOM Conversion Detail")
		query = (
			frappe.qb.from_(table)
			.select(
				table.conversion_factor,
				table.parent,
			)
			.where((table.parenttype == "Item") & (table.uom == self.filters.include_uom))
		)

		if items:
			query = query.where(table.parent.isin(items))

		result = query.run(as_dict=1)
		if not result:
			return {}

		return {d.parent: d.conversion_factor for d in result}

	def get_variant_values_for(self):
		"""Returns variant values for items."""
		attribute_map = {}
		items = []
		if self.filters.item_code or self.filters.item_group:
			items = [d.item_code for d in self.data]

		filters = {}
		if items:
			filters = {"parent": ("in", items)}

		attribute_info = frappe.get_all(
			"Item Variant Attribute",
			fields=["parent", "attribute", "attribute_value"],
			filters=filters,
		)

		for attr in attribute_info:
			attribute_map.setdefault(attr["parent"], {})
			attribute_map[attr["parent"]].update({attr["attribute"]: attr["attribute_value"]})

		return attribute_map

	def get_opening_vouchers(self):
		opening_vouchers = {"Stock Entry": [], "Stock Reconciliation": []}

		se = frappe.qb.DocType("Stock Entry")
		sr = frappe.qb.DocType("Stock Reconciliation")

		vouchers_data = (
			frappe.qb.from_(
				(
					frappe.qb.from_(se)
					.select(se.name, Coalesce("Stock Entry").as_("voucher_type"))
					.where((se.docstatus == 1) & (se.posting_date <= self.to_date) & (se.is_opening == "Yes"))
				)
				+ (
					frappe.qb.from_(sr)
					.select(sr.name, Coalesce("Stock Reconciliation").as_("voucher_type"))
					.where(
						(sr.docstatus == 1) & (sr.posting_date <= self.to_date) & (sr.purpose == "Opening Stock")
					)
				)
			).select("voucher_type", "name")
		).run(as_dict=True)

		if vouchers_data:
			for d in vouchers_data:
				opening_vouchers[d.voucher_type].append(d.name)

		return opening_vouchers

	@staticmethod
	def get_inventory_dimension_fields():
		return [dimension.fieldname for dimension in get_inventory_dimensions()]

	@staticmethod
	def get_opening_fifo_queue(report_data):
		opening_fifo_queue = report_data.get("opening_fifo_queue") or []
		for row in opening_fifo_queue:
			row[1] = getdate(row[1])

		return opening_fifo_queue


def filter_items_with_no_transactions(
	iwb_map, float_precision: float, inventory_dimensions: list = None
):
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
	pop_keys = []
	for group_by_key in iwb_map:
		qty_dict = iwb_map[group_by_key]

		no_transactions = True
		for key, val in qty_dict.items():
<<<<<<< HEAD
			if key in inventory_dimensions:
=======
			if inventory_dimensions and key in inventory_dimensions:
				continue

			if key in [
				"item_code",
				"warehouse",
				"item_name",
				"item_group",
				"project",
				"stock_uom",
				"company",
				"opening_fifo_queue",
			]:
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
				continue

			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False

		if no_transactions:
			pop_keys.append(group_by_key)

	for key in pop_keys:
		iwb_map.pop(key)

	return iwb_map


<<<<<<< HEAD
def get_items(filters: StockBalanceFilter) -> List[str]:
	"Get items based on item code, item group or brand."
	if item_code := filters.get("item_code"):
		return [item_code]
	else:
		item_filters = {}
		if item_group := filters.get("item_group"):
			children = get_descendants_of("Item Group", item_group, ignore_permissions=True)
			item_filters["item_group"] = ("in", children + [item_group])
		if brand := filters.get("brand"):
			item_filters["brand"] = brand

		return frappe.get_all("Item", filters=item_filters, pluck="name", order_by=None)


def get_item_details(items: List[str], sle: List[SLEntry], filters: StockBalanceFilter):
	item_details = {}
	if not items:
		items = list(set(d.item_code for d in sle))

	if not items:
		return item_details

	item_table = frappe.qb.DocType("Item")

	query = (
		frappe.qb.from_(item_table)
		.select(
			item_table.name,
			item_table.item_name,
			item_table.description,
			item_table.item_group,
			item_table.brand,
			item_table.stock_uom,
		)
		.where(item_table.name.isin(items))
	)

	if uom := filters.get("include_uom"):
		uom_conv_detail = frappe.qb.DocType("UOM Conversion Detail")
		query = (
			query.left_join(uom_conv_detail)
			.on((uom_conv_detail.parent == item_table.name) & (uom_conv_detail.uom == uom))
			.select(uom_conv_detail.conversion_factor)
		)

	result = query.run(as_dict=1)

	for item_table in result:
		item_details.setdefault(item_table.name, item_table)

	if filters.get("show_variant_attributes"):
		variant_values = get_variant_values_for(list(item_details))
		item_details = {k: v.update(variant_values.get(k, {})) for k, v in item_details.items()}

	return item_details


def get_item_reorder_details(items):
	item_reorder_details = frappe._dict()

	if items:
		item_reorder_details = frappe.get_all(
			"Item Reorder",
			["parent", "warehouse", "warehouse_reorder_qty", "warehouse_reorder_level"],
			filters={"parent": ("in", items)},
		)

	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)


def get_variants_attributes() -> List[str]:
	"""Return all item variant attributes."""
	return frappe.get_all("Item Attribute", pluck="name")


def get_variant_values_for(items):
	"""Returns variant values for items."""
	attribute_map = {}

	attribute_info = frappe.get_all(
		"Item Variant Attribute",
		["parent", "attribute", "attribute_value"],
		{
			"parent": ("in", items),
		},
	)

	for attr in attribute_info:
		attribute_map.setdefault(attr["parent"], {})
		attribute_map[attr["parent"]].update({attr["attribute"]: attr["attribute_value"]})

	return attribute_map
=======
def get_variants_attributes() -> List[str]:
	"""Return all item variant attributes."""
	return frappe.get_all("Item Attribute", pluck="name")
>>>>>>> d9aa4057d7 (chore(release): Bumped to Version 14.32.1)
