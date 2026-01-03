
import frappe

def implement_phase_4a_scripts():
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()

    print("Implementing Phase 4A Scripts...")

    # 1. Client Script for Deliverable
    js_logic = """
frappe.ui.form.on('Deliverable', {
    refresh: function(frm) {
        // Status Colors
        const status_colors = {
            "Draft": "gray",
            "In Progress": "blue",
            "Submitted": "cyan",
            "Under Review": "orange",
            "Approved": "green",
            "Revision Required": "red",
            "Final": "darkgreen",
            "Cancelled": "black"
        };
        if (frm.doc.status) {
            frm.set_indicator(frm.doc.status, status_colors[frm.doc.status]);
        }

        // Add Revision Button
        if (['Draft', 'In Progress', 'Revision Required'].includes(frm.doc.status) && !frm.doc.__islocal) {
            frm.add_custom_button(__('Upload Revision'), function() {
                new frappe.ui.Dialog({
                    title: 'Upload Revision',
                    fields: [
                        {label: 'File', fieldname: 'file', fieldtype: 'Attach', reqd: 1},
                        {label: 'Comments', fieldname: 'comments', fieldtype: 'Small Text'}
                    ],
                    primary_action_label: 'Upload',
                    primary_action: function(values) {
                        // Add row to revisions
                        let row = frappe.model.add_child(frm.doc, 'Deliverable Revision', 'revisions');
                        row.file = values.file;
                        row.comments = values.comments;
                        row.submission_date = frappe.datetime.now_datetime();
                        row.submitted_by = frappe.session.user;
                        
                        // Increment version
                        frm.set_value('current_version', (frm.doc.current_version || 0) + 1);
                        frm.set_value('status', 'Submitted');
                        frm.set_value('submission_date', frappe.datetime.now_date());
                        
                        frm.save();
                        this.hide();
                    }
                }).show();
            });
        }

        // Approval Buttons
        if (frm.doc.status === 'Submitted' && frappe.user.has_role('Projects Manager')) {
            frm.add_custom_button(__('Approve'), function() {
                frm.set_value('approval_status', 'Approved');
                frm.set_value('status', 'Approved');
                frm.set_value('approved_by', frappe.session.user);
                frm.set_value('approved_on', frappe.datetime.now_datetime());
                frm.save();
            }, "Actions");

            frm.add_custom_button(__('Request Revision'), function() {
                frappe.prompt([
                    {label: 'Reason', fieldname: 'reason', fieldtype: 'Small Text', reqd: 1}
                ], function(values) {
                    frm.set_value('approval_status', 'Rejected');
                    frm.set_value('status', 'Revision Required');
                    frm.set_value('rejection_reason', values.reason);
                    frm.save();
                }, 'Rejection Reason', 'Reject');
            }, "Actions");
        }

        // Mark Final
        if (frm.doc.status === 'Approved' && frappe.user.has_role('Projects Manager')) {
            frm.add_custom_button(__('Mark as Final'), function() {
                frm.set_value('status', 'Final');
                frm.save();
            });
        }
    },

    project: function(frm) {
        if (frm.doc.project) {
            frappe.db.get_doc('Project', frm.doc.project).then(project => {
                if (project.client_contract) frm.set_value('client_contract', project.client_contract);
                if (project.customer) frm.set_value('customer', project.customer);
            });
        }
    }
});
    """

    if frappe.db.exists("Client Script", {"dt": "Deliverable", "name": "Deliverable Logic"}):
        frappe.delete_doc("Client Script", "Deliverable Logic")

    doc = frappe.new_doc("Client Script")
    doc.dt = "Deliverable"
    doc.name = "Deliverable Logic"
    doc.script = js_logic
    doc.enabled = 1
    doc.insert()
    print("✓ Client Script 'Deliverable Logic' created")


    # 2. Server Script for Deliverable (Validations)
    py_logic = """
if doc.due_date and doc.due_date < frappe.utils.today() and doc.status not in ['Completed', 'Final', 'Cancelled', 'Approved']:
    # Optional: Warn or set status. For now, just a logic check example.
    pass

if doc.status == 'Submitted' and not doc.revisions:
    frappe.throw("Cannot submit without at least one revision")
    """

    if frappe.db.exists("Server Script", "Deliverable Validations"):
        frappe.delete_doc("Server Script", "Deliverable Validations")

    # Creating Server Script (DocType Event)
    # Check if Server Script is enabled and we can create it
    try:
        ss = frappe.new_doc("Server Script")
        ss.name = "Deliverable Validations"
        ss.reference_doctype = "Deliverable"
        ss.script_type = "DocType Event"
        ss.doctype_event = "Before Save"
        ss.script = py_logic
        ss.insert()
        print("✓ Server Script 'Deliverable Validations' created")
    except Exception as e:
        print(f"Warning: Could not create Server Script (maybe disabled?): {e}")

    frappe.db.commit()

implement_phase_4a_scripts()
