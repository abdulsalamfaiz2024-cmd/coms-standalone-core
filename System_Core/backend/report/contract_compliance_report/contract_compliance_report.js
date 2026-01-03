frappe.query_reports["Contract Compliance Report"] = {
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
            "options": "\nActive\nCompleted"
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "milestone_compliance" && data) {
            if (data.milestone_compliance >= 100) {
                value = `<span style="color: green; font-weight: bold;">${data.milestone_compliance}%</span>`;
            } else if (data.milestone_compliance >= 50) {
                value = `<span style="color: blue;">${data.milestone_compliance}%</span>`;
            } else {
                value = `<span style="color: orange;">${data.milestone_compliance}%</span>`;
            }
        }

        if (column.fieldname === "invoice_compliance" && data) {
            if (data.invoice_compliance >= 100) {
                value = `<span style="color: green; font-weight: bold;">${data.invoice_compliance}%</span>`;
            } else if (data.invoice_compliance >= 50) {
                value = `<span style="color: blue;">${data.invoice_compliance}%</span>`;
            } else {
                value = `<span style="color: orange;">${data.invoice_compliance}%</span>`;
            }
        }

        return value;
    }
};
