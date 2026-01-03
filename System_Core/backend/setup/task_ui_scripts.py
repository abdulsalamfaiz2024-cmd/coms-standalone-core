
import frappe

def create_task_client_script():
    script_content = """
frappe.ui.form.on('Task', {
    refresh: function(frm) {
        // Show consultant info
        if (frm.doc.assigned_consultant) {
            show_consultant_info(frm);
        }
        
        // Add quick actions
        add_task_actions(frm);
        
        // Show hours indicator
        show_hours_indicator(frm);
    },
    
    assigned_consultant: function(frm) {
        if (frm.doc.assigned_consultant) {
            // Fetch consultant details
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Employee',
                    filters: { name: frm.doc.assigned_consultant },
                    fieldname: ['employee_name', 'hourly_rate', 'consultant_type']
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Assigned to {0} ({1}) - Rate: {2}/hr', [
                                r.message.employee_name,
                                r.message.consultant_type || 'N/A',
                                format_currency(r.message.hourly_rate || 0)
                            ]),
                            indicator: 'green'
                        });
                    }
                }
            });
            
            // Fetch and set consultant contract
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Consultant Contract',
                    filters: {
                        consultant: frm.doc.assigned_consultant,
                        status: 'Active'
                    },
                    fieldname: ['name']
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('consultant_contract', r.message.name);
                    }
                }
            });
        } else {
            frm.set_value('consultant_contract', null);
        }
    },
    
    estimated_hours: function(frm) {
        show_hours_indicator(frm);
    }
});

function show_consultant_info(frm) {
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Employee',
            filters: { name: frm.doc.assigned_consultant },
            fieldname: ['employee_name', 'hourly_rate']
        },
        callback: function(r) {
            if (r.message) {
                let rate = r.message.hourly_rate || 0;
                let estimated_cost = (frm.doc.estimated_hours || 0) * rate;
                
                frm.dashboard.add_indicator(
                    __('Consultant: {0}', [r.message.employee_name]),
                    'blue'
                );
                frm.dashboard.add_indicator(
                    __('Est. Cost: {0}', [format_currency(estimated_cost)]),
                    'green'
                );
            }
        }
    });
}

function add_task_actions(frm) {
    if (!frm.is_new() && frm.doc.assigned_consultant) {
        // Log Time button
        frm.add_custom_button(__('Log Time'), function() {
            frappe.route_options = {
                'employee': frm.doc.assigned_consultant,
                'project': frm.doc.project,
                'task': frm.doc.name
            };
            frappe.new_doc('Timesheet');
        }, __('Create'));
    }
    
    // View Project button
    if (frm.doc.project) {
        frm.add_custom_button(__('View Project'), function() {
            frappe.set_route('Form', 'Project', frm.doc.project);
        });
    }
}

function show_hours_indicator(frm) {
    let estimated = frm.doc.estimated_hours || 0;
    let actual = frm.doc.actual_time || 0;
    
    if (estimated > 0) {
        let percentage = (actual / estimated * 100).toFixed(0);
        let color = percentage > 100 ? 'red' : (percentage > 80 ? 'orange' : 'green');
        
        frm.dashboard.add_indicator(
            __('Hours: {0} / {1} ({2}%)', [actual.toFixed(1), estimated, percentage]),
            color
        );
    }
}
"""
    
    # Create or update Client Script
    if frappe.db.exists("Client Script", {"dt": "Task", "module": "Consulting"}):
        doc = frappe.get_doc("Client Script", {"dt": "Task", "module": "Consulting"})
        doc.script = script_content
        doc.save()
        print("Updated Task Client Script")
    else:
        doc = frappe.new_doc("Client Script")
        doc.dt = "Task"
        doc.module = "Consulting"
        doc.name = "Task Workflow Customizations" # Explicit name
        doc.script = script_content
        doc.save()
        print("Created Task Client Script")
    
    frappe.db.commit()

create_task_client_script()
