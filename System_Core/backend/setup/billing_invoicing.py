# COMS Phase 5A Implementation Script
# Time-to-Invoice Automation
# 
# Run this script in bench console:
# docker exec -w /home/frappe/frappe-bench frappe_docker-backend-1 bench --site frontend execute implement_phase_5a.implement_phase_5a

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def implement_phase_5a():
    """Implement Phase 5A: Time-to-Invoice Automation"""
    
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()
    
    print("=" * 60)
    print("COMS Phase 5A: Time-to-Invoice Automation")
    print("=" * 60)
    
    # Step 1: Create Sales Invoice Custom Fields
    print("\n[1/4] Creating Sales Invoice custom fields...")
    create_sales_invoice_fields()
    
    # Step 2: Create Sales Invoice Item Custom Fields
    print("\n[2/4] Creating Sales Invoice Item custom fields...")
    create_sales_invoice_item_fields()
    
    # Step 3: Create Consulting Services Item
    print("\n[3/4] Creating Consulting Services item...")
    create_billing_item()
    
    # Step 4: Update Project Client Script
    print("\n[4/4] Updating Project client script...")
    update_project_client_script()
    
    # Commit all changes
    frappe.db.commit()
    
    print("\n" + "=" * 60)
    print("✓ Phase 5A Implementation Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Run: bench --site frontend migrate")
    print("2. Verify custom fields in Sales Invoice form")
    print("3. Test invoice generation from Project")
    print("=" * 60)


def create_sales_invoice_fields():
    """Create custom fields for Sales Invoice"""
    
    invoice_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Sales Invoice",
            "label": "Client Contract",
            "fieldname": "client_contract",
            "fieldtype": "Link",
            "options": "Client Contract",
            "insert_after": "project",
            "module": "Consulting"
        },
        {
            "doctype": "Custom Field",
            "dt": "Sales Invoice",
            "label": "Billing Type",
            "fieldname": "billing_type",
            "fieldtype": "Select",
            "options": "Time-Based\nMilestone\nFixed\nMixed",
            "insert_after": "client_contract",
            "module": "Consulting"
        },
        {
            "doctype": "Custom Field",
            "dt": "Sales Invoice",
            "label": "Is Consulting Invoice",
            "fieldname": "is_consulting",
            "fieldtype": "Check",
            "insert_after": "billing_type",
            "module": "Consulting"
        }
    ]
    
    for field in invoice_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            doc = frappe.get_doc(field)
            doc.insert()
            print(f"  ✓ Created: {field['dt']}.{field['fieldname']}")
        else:
            print(f"  - Exists: {field['dt']}.{field['fieldname']}")


def create_sales_invoice_item_fields():
    """Create custom fields for Sales Invoice Item"""
    
    item_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Sales Invoice Item",
            "label": "Timesheet",
            "fieldname": "timesheet",
            "fieldtype": "Link",
            "options": "Timesheet",
            "insert_after": "delivery_note",
            "module": "Consulting"
        },
        {
            "doctype": "Custom Field",
            "dt": "Sales Invoice Item",
            "label": "Timesheet Detail",
            "fieldname": "ts_detail",
            "fieldtype": "Data",
            "insert_after": "timesheet",
            "read_only": 1,
            "module": "Consulting"
        },
        {
            "doctype": "Custom Field",
            "dt": "Sales Invoice Item",
            "label": "Consultant",
            "fieldname": "consultant",
            "fieldtype": "Link",
            "options": "Employee",
            "insert_after": "ts_detail",
            "read_only": 1,
            "module": "Consulting"
        },
        {
            "doctype": "Custom Field",
            "dt": "Sales Invoice Item",
            "label": "Hours Billed",
            "fieldname": "hours_billed",
            "fieldtype": "Float",
            "insert_after": "consultant",
            "read_only": 1,
            "module": "Consulting"
        }
    ]
    
    for field in item_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            doc = frappe.get_doc(field)
            doc.insert()
            print(f"  ✓ Created: {field['dt']}.{field['fieldname']}")
        else:
            print(f"  - Exists: {field['dt']}.{field['fieldname']}")


def create_billing_item():
    """Create Consulting Services billing item"""
    
    item_code = "Consulting Services"
    
    if not frappe.db.exists("Item", item_code):
        # Make sure Services item group exists
        if not frappe.db.exists("Item Group", "Services"):
            ig = frappe.new_doc("Item Group")
            ig.item_group_name = "Services"
            ig.parent_item_group = "All Item Groups"
            ig.insert(ignore_permissions=True)
            print("  ✓ Created Item Group: Services")
        
        # Create the item
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = "Consulting Services"
        item.item_group = "Services"
        item.stock_uom = "Hour"
        item.is_stock_item = 0
        item.is_sales_item = 1
        item.include_item_in_manufacturing = 0
        item.description = "Professional consulting services billed by hour"
        item.insert(ignore_permissions=True)
        print(f"  ✓ Created Item: {item_code}")
    else:
        print(f"  - Item exists: {item_code}")


def update_project_client_script():
    """Update or create Project client script with invoice button"""
    
    script_name = "Project Invoice Button"
    
    js_code = """
// Generate Invoice button for Project
frappe.ui.form.on('Project', {
    refresh: function(frm) {
        // Add Generate Invoice button for open projects
        if (!frm.is_new() && frm.doc.status === 'Open') {
            frm.add_custom_button(__('Generate Invoice'), function() {
                generate_project_invoice(frm);
            }, __('Create'));
            
            // Show unbilled time summary
            show_unbilled_summary(frm);
        }
    }
});

function generate_project_invoice(frm) {
    frappe.confirm(
        __('Generate invoice for all unbilled time entries on this project?'),
        function() {
            frappe.call({
                method: 'backend.billing.invoice_generator.generate_invoice_for_project',
                args: {
                    project: frm.doc.name
                },
                freeze: true,
                freeze_message: __('Generating Invoice...'),
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frappe.set_route('Form', 'Sales Invoice', r.message[0]);
                    }
                    frm.reload_doc();
                }
            });
        }
    );
}

function show_unbilled_summary(frm) {
    frappe.call({
        method: 'backend.billing.invoice_generator.get_unbilled_summary',
        callback: function(r) {
            if (r.message) {
                let project_data = r.message.by_project[frm.doc.name];
                if (project_data && project_data.amount > 0) {
                    frm.dashboard.add_indicator(
                        __('Unbilled: {0} hrs ({1})', [
                            project_data.hours.toFixed(1),
                            format_currency(project_data.amount)
                        ]),
                        'orange'
                    );
                }
            }
        }
    });
}
"""
    
    # Check if script exists
    if frappe.db.exists("Client Script", {"dt": "Project", "name": script_name}):
        frappe.delete_doc("Client Script", script_name, force=True)
    
    # Create or update
    cs = frappe.new_doc("Client Script")
    cs.name = script_name
    cs.dt = "Project"
    cs.script = js_code
    cs.enabled = 1
    cs.insert(ignore_permissions=True)
    print(f"  ✓ Created Client Script: {script_name}")


# Run if executed directly
if __name__ == "__main__":
    implement_phase_5a()
