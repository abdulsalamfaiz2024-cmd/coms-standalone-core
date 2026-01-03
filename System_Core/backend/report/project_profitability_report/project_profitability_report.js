frappe.query_reports["Project Profitability Report"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nOpen\nCompleted\nCancelled"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date"
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "margin" && data) {
            if (data.margin >= 20) {
                value = `<span style="color: green; font-weight: bold;">${data.margin}%</span>`;
            } else if (data.margin >= 10) {
                value = `<span style="color: orange;">${data.margin}%</span>`;
            } else {
                value = `<span style="color: red;">${data.margin}%</span>`;
            }
        }

        if (column.fieldname === "gross_profit" && data) {
            if (data.gross_profit >= 0) {
                value = `<span style="color: green;">${format_currency(data.gross_profit)}</span>`;
            } else {
                value = `<span style="color: red;">${format_currency(data.gross_profit)}</span>`;
            }
        }

        return value;
    }
};
