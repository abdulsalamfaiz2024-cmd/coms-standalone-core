
import frappe

def apply_consultant_translation():
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()

    print("Applying Global Translation: Employee -> Consultant...")

    translations = [
        {"source_text": "Employee", "translated_text": "Consultant"},
        {"source_text": "New Employee", "translated_text": "New Consultant"},
        {"source_text": "Employee List", "translated_text": "Consultant List"},
        {"source_text": "Add Employee", "translated_text": "Add Consultant"}
    ]

    for t in translations:
        # Check if translation exists
        if frappe.db.exists("Translation", {"source_text": t["source_text"], "language": "en"}):
            doc = frappe.get_doc("Translation", {"source_text": t["source_text"], "language": "en"})
            doc.translated_text = t["translated_text"]
            doc.save()
        else:
            doc = frappe.new_doc("Translation")
            doc.language = "en"
            doc.source_text = t["source_text"]
            doc.translated_text = t["translated_text"]
            doc.insert()
            
    # Clear cache to apply translations
    frappe.clear_cache()
    print("✓ Global Translations applied.")

apply_consultant_translation()
