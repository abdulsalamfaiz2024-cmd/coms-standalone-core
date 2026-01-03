frappe.query_reports["Client Billing Summary"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "overdue" && data && data.overdue > 0) {
            value = `<span style="color: red; font-weight: bold;">${format_currency(data.overdue)}</span>`;
        }

        if (column.fieldname === "outstanding" && data && data.outstanding > 0) {
            value = `<span style="color: orange;">${format_currency(data.outstanding)}</span>`;
        }

        return value;
    }
};
