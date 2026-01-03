
import frappe

def create_client_script():
    script_content = """
frappe.ui.form.on('Project', {
    refresh: function(frm) {
        // Show contract info if linked
        if (frm.doc.client_contract) {
            frm.add_custom_button(__('View Contract'), function() {
                frappe.set_route('Form', 'Client Contract', frm.doc.client_contract);
            });
        }
        
        // Show team summary
        show_team_summary(frm);
        
        // Add quick action to add consultant
        frm.add_custom_button(__('Add Consultant'), function() {
            add_consultant_dialog(frm);
        }, __('Actions'));
    },
    
    client_contract: function(frm) {
        // Fetch contract details when contract is selected
        if (frm.doc.client_contract) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Client Contract',
                    name: frm.doc.client_contract
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('customer', r.message.client);
                        frm.set_value('expected_start_date', r.message.start_date);
                        frm.set_value('expected_end_date', r.message.end_date);
                        frm.set_value('estimated_costing', r.message.contract_value);
                    }
                }
            });
        }
    }
});

function show_team_summary(frm) {
    if (frm.doc.consultant_team && frm.doc.consultant_team.length > 0) {
        let total_estimated = 0;
        let total_actual = 0;
        
        frm.doc.consultant_team.forEach(function(row) {
            total_estimated += row.estimated_hours || 0;
            total_actual += row.actual_hours || 0;
        });
        
        frm.dashboard.add_indicator(
            __('Team: {0} consultants', [frm.doc.consultant_team.length]),
            'blue'
        );
        frm.dashboard.add_indicator(
            __('Hours: {0} / {1}', [total_actual.toFixed(1), total_estimated.toFixed(1)]),
            total_actual > total_estimated ? 'red' : 'green'
        );
    }
}

function add_consultant_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Add Consultant to Project'),
        fields: [
            {
                label: 'Consultant',
                fieldname: 'consultant',
                fieldtype: 'Link',
                options: 'Employee',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'is_billable': 1,
                            'status': 'Active'
                        }
                    };
                }
            },
            {
                label: 'Role',
                fieldname: 'role',
                fieldtype: 'Data'
            },
            {
                label: 'Allocation %',
                fieldname: 'allocation_percentage',
                fieldtype: 'Percent',
                default: 100
            },
            {
                label: 'Estimated Hours',
                fieldname: 'estimated_hours',
                fieldtype: 'Float'
            }
        ],
        primary_action_label: __('Add'),
        primary_action: function(values) {
            // Check if already in team
            let exists = frm.doc.consultant_team.some(
                row => row.consultant === values.consultant
            );
            
            if (exists) {
                frappe.msgprint(__('Consultant already in team'));
                return;
            }
            
            // Add to table
            let row = frm.add_child('consultant_team');
            row.consultant = values.consultant;
            row.role = values.role;
            row.allocation_percentage = values.allocation_percentage;
            row.estimated_hours = values.estimated_hours;
            
            frm.refresh_field('consultant_team');
            d.hide();
            
            frappe.show_alert({
                message: __('Consultant added'),
                indicator: 'green'
            });
        }
    });
    d.show();
}
"""
    
    # Create or update Client Script
    if frappe.db.exists("Client Script", {"dt": "Project", "module": "Consulting"}):
        doc = frappe.get_doc("Client Script", {"dt": "Project", "module": "Consulting"})
        doc.script = script_content
        doc.save()
        print("Updated Project Client Script")
    else:
        doc = frappe.new_doc("Client Script")
        doc.dt = "Project"
        doc.module = "Consulting"
        doc.name = "Project Consulting Extensions" # Set name explicitly
        doc.script = script_content
        doc.save()
        print("Created Project Client Script")
    
    frappe.db.commit()

create_client_script()
