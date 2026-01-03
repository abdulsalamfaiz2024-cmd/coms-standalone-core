
import os
import json
import ast
import sys

BASE_DIR = r"d:\erpnext\coms\consulting\doctype"
BAD_DIR = r"d:\erpnext\coms\coms"

def check_files():
    print("Starting Static Verification...")
    errors = []
    
    # 1. Check for Bad Directory
    if os.path.exists(BAD_DIR):
        errors.append(f"FAIL: The incorrect directory structure exists: {BAD_DIR}")
    else:
        print(f"PASS: Incorrect directory {BAD_DIR} is gone.")

    # 2. Check Standard Doctype Folders
    required_doctypes = [
        "client_contract", "consultant_contract", "deliverable", "expertise_area",
        "contract_milestone", "contract_project", "consultant_project_assignment",
        "consultant_expertise", "deliverable_revision", "project_consultant"
    ]
    
    for dt in required_doctypes:
        dt_path = os.path.join(BASE_DIR, dt)
        if not os.path.exists(dt_path):
            errors.append(f"FAIL: Missing folder for {dt}")
            continue
            
        print(f"\nChecking {dt}...")
        
        # Check integrity of files in the folder
        files = os.listdir(dt_path)
        
        # Check JSON
        json_file = f"{dt}.json"
        if json_file in files:
            try:
                with open(os.path.join(dt_path, json_file), 'r') as f:
                    json.load(f)
                print(f"  PASS: JSON Valid: {json_file}")
            except Exception as e:
                errors.append(f"FAIL: Invalid JSON in {dt}/{json_file}: {e}")
        else:
             errors.append(f"FAIL: Missing {json_file}")

        # Check Python (if exists)
        has_init = False
        for f_name in files:
            if f_name == "__init__.py":
                has_init = True
            
            if f_name.endswith(".py"):
                try:
                    with open(os.path.join(dt_path, f_name), 'r') as f:
                        ast.parse(f.read())
                    print(f"  PASS: Python Syntax Valid: {f_name}")
                except Exception as e:
                    errors.append(f"FAIL: Invalid Python Syntax in {dt}/{f_name}: {e}")

        if not has_init:
            errors.append(f"FAIL: Missing __init__.py in {dt}")

    print("\n" + "="*40)
    if errors:
        print(f"FAILED with {len(errors)} errors:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("SUCCESS: All structure and syntax checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    check_files()
