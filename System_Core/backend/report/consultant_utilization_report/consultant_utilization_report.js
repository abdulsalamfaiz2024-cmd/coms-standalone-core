frappe.query_reports["Consultant Utilization Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "employee",
            "label": __("Consultant"),
            "fieldtype": "Link",
            "options": "Employee",
            "get_query": function () {
                return {
                    filters: {
                        "status": "Active"
                    }
                };
            }
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "utilization" && data) {
            if (data.utilization >= 80) {
                value = `<span style="color: green; font-weight: bold;">${data.utilization}%</span>`;
            } else if (data.utilization >= 60) {
                value = `<span style="color: orange;">${data.utilization}%</span>`;
            } else {
                value = `<span style="color: red;">${data.utilization}%</span>`;
            }
        }

        return value;
    }
};
