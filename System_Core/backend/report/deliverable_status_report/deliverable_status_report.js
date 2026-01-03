frappe.query_reports["Deliverable Status Report"] = {
    "filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nIn Progress\nSubmitted\nApproved\nRevision Required\nCompleted"
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "days_until_due" && data) {
            if (data.days_until_due < 0) {
                value = `<span style="color: red; font-weight: bold;">${data.days_until_due} (Overdue)</span>`;
            } else if (data.days_until_due <= 3) {
                value = `<span style="color: orange;">${data.days_until_due}</span>`;
            } else {
                value = `<span style="color: green;">${data.days_until_due}</span>`;
            }
        }

        if (column.fieldname === "status" && data) {
            let color = "black";
            switch (data.status) {
                case "Completed":
                case "Approved":
                    color = "green";
                    break;
                case "In Progress":
                case "Submitted":
                    color = "blue";
                    break;
                case "Revision Required":
                    color = "orange";
                    break;
                case "Draft":
                    color = "gray";
                    break;
            }
            value = `<span style="color: ${color};">${data.status}</span>`;
        }

        return value;
    }
};
