
import frappe

def restore_client_scripts():
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()

    scripts = [
        {
            "dt": "Client Contract",
            "name": "Client Contract Logic",
            "script": """
frappe.ui.form.on('Client Contract', {
    refresh: function(frm) {
        if (!frm.doc.__islocal && frm.doc.status === 'Active') {
            frm.add_custom_button(__('Create Project'), function() {
                frappe.model.open_mapped_doc({
                    method: "frappe.model.mapper.make_mapped_doc",
                    frm: frm,
                    method_args: {
                        source_name: frm.doc.name,
                        target_doc: "Project",
                        postprocess: function(source, target) {
                            target.client_contract = source.name;
                            target.customer = source.client;
                            target.project_name = source.contract_title;
                        }
                    }
                });
            });
        }
    },
    validate: function(frm) {
        if (frm.doc.start_date && frm.doc.end_date) {
            if (frm.doc.end_date < frm.doc.start_date) {
                frappe.msgprint(__("End Date cannot be before Start Date"));
                frappe.validated = false;
            }
        }
    }
});
            """
        },
        {
            "dt": "Consultant Contract",
            "name": "Consultant Contract Logic",
            "script": """
frappe.ui.form.on('Consultant Contract', {
    validate: function(frm) {
        if (frm.doc.rate_amount < 0) {
            frappe.msgprint(__("Rate cannot be negative"));
            frappe.validated = false;
        }
    }
});
            """
        }
    ]

    for s in scripts:
        if frappe.db.exists("Client Script", {"dt": s["dt"], "name": s["name"]}):
             frappe.delete_doc("Client Script", s["name"])
        
        doc = frappe.new_doc("Client Script")
        doc.dt = s["dt"]
        doc.name = s["name"]
        doc.script = s["script"]
        doc.enabled = 1
        doc.insert()
        print(f"✓ Client Script for {s['dt']} restored")
    
    frappe.db.commit()

restore_client_scripts()
