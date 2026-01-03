
import frappe

def force_consultant_label():
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()

    print("Forcing 'Consultant' label via Client Script...")

    js_code = """
frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        // Force the page title to say 'Consultant'
        if (frm.doc.__islocal) {
            frm.page.set_title(__('New Consultant'));
        } else {
            frm.page.set_title(frm.doc.employee_name || __('Consultant'));
        }
        
        // Update breadcrumbs (Visual hack)
        setTimeout(() => {
            $('.navbar-breadcrumb .breadcrumb-item a[href="/app/employee"]').text('Consulting');
        }, 500);
    }
});
    """

    # Create or Update Client Script
    if frappe.db.exists("Client Script", {"dt": "Employee", "name": "Employee to Consultant Label"}):
        frappe.delete_doc("Client Script", "Employee to Consultant Label")

    doc = frappe.new_doc("Client Script")
    doc.dt = "Employee"
    doc.name = "Employee to Consultant Label"
    doc.script = js_code
    doc.enabled = 1
    doc.insert()
    
    # Also verify Property Setter again
    if not frappe.db.exists("Property Setter", {"doc_type": "Employee", "property": "label"}):
        from frappe.custom.doctype.property_setter.property_setter import make_property_setter
        make_property_setter("Employee", None, "label", "Consultant", "Data")
    
    frappe.db.commit()
    print("✓ Client Script applied to rename Employee UI to Consultant.")

force_consultant_label()
