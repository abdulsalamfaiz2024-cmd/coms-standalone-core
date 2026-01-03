
import frappe

def create_timesheet_client_script():
    script_content = """
frappe.ui.form.on('Timesheet', {
    refresh: function(frm) {
        show_contract_info(frm);
        show_totals_summary(frm);
    },
    
    employee: function(frm) {
        if (frm.doc.employee) {
            // Fetch consultant contract
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Consultant Contract',
                    filters: {
                        consultant: frm.doc.employee,
                        status: 'Active'
                    },
                    fieldname: ['name', 'rate_type', 'rate_amount']
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('consultant_contract', r.message.name);
                        frappe.show_alert({
                            message: __('Contract found: {0} rate - {1}', [
                                r.message.rate_type,
                                format_currency(r.message.rate_amount)
                            ]),
                            indicator: 'green'
                        });
                    } else {
                        frm.set_value('consultant_contract', null);
                        frappe.show_alert({
                            message: __('No active contract found'),
                            indicator: 'orange'
                        });
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Timesheet Detail', {
    hours: function(frm, cdt, cdn) {
        calculate_row_amounts(frm, cdt, cdn);
    },
    
    billing_hours: function(frm, cdt, cdn) {
        calculate_row_amounts(frm, cdt, cdn);
    },
    
    consultant_rate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.consultant_rate) {
            frappe.model.set_value(cdt, cdn, 'rate_source', 'Override');
        }
        calculate_row_amounts(frm, cdt, cdn);
    },
    
    project: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.project) {
            // Fetch client contract from project
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Project',
                    filters: { name: row.project },
                    fieldname: ['client_contract', 'customer']
                },
                callback: function(r) {
                    if (r.message && r.message.client_contract) {
                        frappe.model.set_value(cdt, cdn, 'client_contract', r.message.client_contract);
                    }
                }
            });
        }
    }
});

function calculate_row_amounts(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    
    // Determine rate to use
    let rate = row.consultant_rate || row.billing_rate || 0;
    // Handle is_billable flag - check standard field name
    let is_billable = row.is_billable; // Standard field is 'is_billable' (Check)
    let hours = is_billable ? (row.billing_hours || row.hours) : row.hours;
    
    // Update billing amount
    if (is_billable) {
        frappe.model.set_value(cdt, cdn, 'billing_amount', rate * hours);
    } else {
         frappe.model.set_value(cdt, cdn, 'billing_amount', 0);
    }
    
    // Update costing amount
    frappe.model.set_value(cdt, cdn, 'costing_amount', rate * row.hours);
    
    // Refresh totals - standard ERPNext might handle this via calculate_total_amounts
    // But we trigger just in case
    // frm.trigger('calculate_total_amounts'); // This assumes standard logic exists.
    // If not, we rely on server side or built-in listeners.
}

function show_contract_info(frm) {
    if (frm.doc.consultant_contract) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Consultant Contract',
                filters: { name: frm.doc.consultant_contract },
                fieldname: ['rate_type', 'rate_amount']
            },
            callback: function(r) {
                if (r.message) {
                    frm.dashboard.add_indicator(
                        __('Contract: {0} - {1}', [
                            r.message.rate_type,
                            format_currency(r.message.rate_amount)
                        ]),
                        'blue'
                    );
                }
            }
        });
    }
}

function show_totals_summary(frm) {
    if (frm.doc.time_logs && frm.doc.time_logs.length > 0) {
        let total_hours = 0;
        let total_billable = 0;
        
        frm.doc.time_logs.forEach(function(row) {
            total_hours += row.hours || 0;
            if (row.is_billable) {
                total_billable += row.billing_amount || 0;
            }
        });
        
        frm.dashboard.add_indicator(
            __('Total: {0} hrs | Billable: {1}', [
                total_hours.toFixed(1),
                format_currency(total_billable)
            ]),
            'green'
        );
    }
}
"""
    
    # Create or update Client Script
    if frappe.db.exists("Client Script", {"dt": "Timesheet", "module": "Consulting"}):
        doc = frappe.get_doc("Client Script", {"dt": "Timesheet", "module": "Consulting"})
        doc.script = script_content
        doc.save()
        print("Updated Timesheet Client Script")
    else:
        doc = frappe.new_doc("Client Script")
        doc.dt = "Timesheet"
        doc.module = "Consulting"
        doc.name = "Timesheet Rate Logic" # Explicit name
        doc.script = script_content
        doc.save()
        print("Created Timesheet Client Script")
    
    frappe.db.commit()

create_timesheet_client_script()
