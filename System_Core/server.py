
import http.server
import socketserver
import json
import os
import sys
import mimetypes
from urllib.parse import urlparse, parse_qs

# Ensure local modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import db_engine
import backup_manager
import hashlib
import uuid

PORT = int(os.environ.get('PORT', 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_ROOT = os.path.join(BASE_DIR, "frontend")
DOCTYPE_ROOT = os.path.join(BASE_DIR, "backend", "doctype")

# Simple In-Memory Session Store (Token -> UserID)
SESSION_STORE = {}

def verify_session(token):
    return SESSION_STORE.get(token)

class ConsultancyRequestHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        print(f"DEBUG: GET Request -> {self.path}")
        
        # 1. API: Root/Meta Check (API Ping)
        if self.path == "/api/ping":
            self.send_json({"status": "online", "message": "Relational Engine Active"})
            return

        # 2. API: Metadata
        if self.path.startswith("/api/meta"):
            try:
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                dt = qs.get('doctype', [None])[0]
                if not dt:
                    self.send_error(400, "Missing doctype parameter")
                    return
                
                print(f"DEBUG: Fetching metadata for '{dt}'")
                meta = self.get_metadata(dt)
                if "error" in meta:
                    self.send_error(404, f"DocType '{dt}' not found in schema")
                else:
                    self.send_json(meta)
                return
            except Exception as e:
                self.send_error(500, f"Metadata Error: {str(e)}")
                return

        # 3. API: List Data
        if self.path.startswith("/api/list"):
            try:
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                table = qs.get('table', [None])[0]
                search = qs.get('search', [None])[0]
                if not table:
                    self.send_error(400, "Missing table parameter")
                    return
                
                print(f"DEBUG: Fetching data list for '{table}' (Search: {search})")
                data = db_engine.get_all(table, search=search)
                self.send_json(data)
                return
            except Exception as e:
                self.send_error(500, f"Database List Error: {str(e)}")
                return

        # 4. API: Get Single Document
        if self.path.startswith("/api/get"):
            try:
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                table = qs.get('table', [None])[0]
                doc_id = qs.get('id', [None])[0]
                if not table or not doc_id:
                    self.send_error(400, "Missing table or id parameter")
                    return
                
                print(f"DEBUG: Fetching single doc '{doc_id}' from '{table}'")
                doc = db_engine.get_one(table, doc_id)
                self.send_json(doc)
                return
            except Exception as e:
                self.send_error(500, f"Database Get Error: {str(e)}")
                return

        # 5. API: Preview Data
        if self.path.startswith("/api/preview"):
            try:
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                table = qs.get('table', [None])[0]
                doc_id = qs.get('id', [None])[0]
                if not table or not doc_id:
                    self.send_error(400, "Missing table or id")
                    return
                data = db_engine.get_preview(table, doc_id)
                self.send_json(data)
                return
            except Exception as e:
                self.send_error(500, f"Preview Error: {str(e)}")
                return

        # 8. API: Trigger Backup
        if self.path == "/api/admin/backup":
            try:
                print("DEBUG: Triggering Manual Backup...")
                result = backup_manager.create_timestamped_backup()
                self.send_json(result)
                return
            except Exception as e:
                self.send_error(500, f"Backup Error: {str(e)}")
                return

        # 9. API: Get Settings (GET)
        if self.path == "/api/settings/get":
            try:
                self.send_json(db_engine.get_settings())
                return
            except Exception as e:
                self.send_error(500, f"Settings Error: {str(e)}")
                return

        # 10. API: List Users (GET)
        if self.path == "/api/users/list":
            try:
                self.send_json(db_engine.get_users())
                return
            except Exception as e:
                self.send_error(500, f"Users Error: {str(e)}")
                return

        # 11. API: Get Audit Logs (GET)
        if self.path.startswith("/api/audit"):
            try:
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                doctype = qs.get('doctype', [None])[0]
                doc_id = qs.get('id', [None])[0]
                limit = int(qs.get('limit', [50])[0])
                
                print(f"DEBUG: Fetching audit logs for {doctype}/{doc_id}")
                logs = db_engine.get_audit_log(doctype=doctype, doc_id=doc_id, limit=limit)
                self.send_json(logs)
                return
            except Exception as e:
                self.send_error(500, f"Audit Log Error: {str(e)}")
                return

        # 12. API: Get User Permissions (GET)
        if self.path.startswith("/api/permissions"):
            try:
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                role = qs.get('role', [None])[0]
                
                if role:
                    perms = db_engine.get_role_permissions(role)
                    if perms:
                        self.send_json(perms)
                    else:
                        self.send_json({'error': 'Role not found'})
                else:
                    # Return all roles and their permissions
                    conn = db_engine.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT role, permissions FROM RolePermissions')
                    rows = cursor.fetchall()
                    conn.close()
                    result = {row['role']: json.loads(row['permissions']) for row in rows}
                    self.send_json(result)
                return
            except Exception as e:
                self.send_error(500, f"Permissions Error: {str(e)}")
                return
            
        # 5. Static File Routing
        if self.path == "/" or self.path == "/portal" or self.path == "/portal/":
            self.path = "/portal/index.html"

        # Serve uploaded files from /uploads/ path
        if self.path.startswith("/uploads/"):
            uploads_dir = os.path.join(WEB_ROOT, 'uploads')
            file_name = self.path.replace("/uploads/", "")
            file_path = os.path.join(uploads_dir, file_name)
            if os.path.exists(file_path):
                try:
                    # Determine content type
                    import mimetypes
                    content_type, _ = mimetypes.guess_type(file_path)
                    if not content_type:
                        content_type = 'application/octet-stream'
                    
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", content_type)
                    self.send_header("Content-Length", len(file_content))
                    self.end_headers()
                    self.wfile.write(file_content)
                    return
                except Exception as e:
                    print(f"Upload Serve Error: {e}")
                    self.send_error(500, f"Error serving file: {str(e)}")
                    return
            else:
                self.send_error(404, "Uploaded file not found")
                return
             
        # Set directory for SimpleHTTPRequestHandler
        self.directory = WEB_ROOT
        
        # Handle template placeholders in HTML files
        if self.path.endswith(".html"):
            fpath = os.path.join(self.directory, self.path.lstrip("/"))
            if os.path.exists(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = content.replace("{{ user_fullname }}", "System Admin")
                    content = content.replace("{{ user_fullname[:2].upper() }}", "SA")
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                    return
                except Exception as e:
                    print(f"Template Error: {e}")

        # Fallback to standard static file serving
        return super().do_GET()

    def do_POST(self):
        print(f"DEBUG: POST Request -> {self.path}")
        
        # 1. API: Login
        if self.path == "/api/login":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                auth_data = json.loads(post_data)
                
                username = auth_data.get('username')
                password = auth_data.get('password')
                
                # Check DB
                user = db_engine.get_user_by_username(username)
                
                if user and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
                    # Success - include permissions in response
                    token = str(uuid.uuid4())
                    SESSION_STORE[token] = user['id']
                    
                    # Get user's permissions based on role
                    permissions = db_engine.get_role_permissions(user['role'])
                    
                    self.send_json({
                        "status": "success", 
                        "token": token, 
                        "user": user['full_name'], 
                        "role": user['role'],
                        "user_id": user['id'],
                        "permissions": permissions
                    })
                else:
                    self.send_error(401, "Invalid Credentials")
                return
            except Exception as e:
                self.send_error(500, f"Login Error: {str(e)}")
                return

        # EMERGENCY ADMIN RESET (Remove before production final)
        if self.path == "/api/emergency_reset":
            try:
                import hashlib
                import uuid
                
                # 1. Create Users Table if missing
                conn = db_engine.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS "Users" (
                        "id" TEXT PRIMARY KEY,
                        "username" TEXT UNIQUE,
                        "password_hash" TEXT,
                        "full_name" TEXT,
                        "role" TEXT,
                        "email" TEXT
                    );
                """)
                
                # 2. Reset Admin
                pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("DELETE FROM Users WHERE username='admin'")
                cursor.execute("""
                    INSERT INTO Users (id, username, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), "admin", pwd_hash, "System Admin", "Administrator"))
                
                conn.commit()
                conn.close()
                
                self.send_json({"status": "success", "message": "Admin Reset to: admin / admin123"})
                return
            except Exception as e:
                self.send_error(500, f"Reset Error: {str(e)}")
                return

        # 2. API: Delete
        if self.path == "/api/delete":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                table = data.get('doctype')
                doc_id = data.get('id')
                
                if not table or not doc_id:
                    self.send_error(400, "Missing doctype or id")
                    return
                
                print(f"DEBUG: Deleting {doc_id} from {table}")
                db_engine.delete_one(table, doc_id)
                self.send_json({"status": "success", "message": "Record Deleted"})
                return
            except Exception as e:
                self.send_error(500, f"Delete Error: {str(e)}")
                return

        # 3. API: Upload File (Base64)
        if self.path == "/api/upload":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                # Payload: { filename, content (base64), parent_doctype, parent_id }
                import base64
                
                content = data['content']
                if ',' in content:
                    content = content.split(',')[1] # Remove data:application/pdf;base64, prefix
                
                try:
                    file_content = base64.b64decode(content)
                except Exception as e:
                    print(f"Base64 Decode Error: {e}")
                    self.send_error(400, "Invalid Base64 Content")
                    return

                filename = f"{uuid.uuid4()}_{data['filename']}" # Secure filename
                
                # Ensure uploads dir exists
                uploads_dir = os.path.join(WEB_ROOT, "uploads")
                os.makedirs(uploads_dir, exist_ok=True)
                
                save_path = os.path.join(uploads_dir, filename)
                
                with open(save_path, 'wb') as f:
                    f.write(file_content)
                
                # DB Record
                file_id = str(uuid.uuid4())
                public_path = f"/uploads/{filename}"
                
                db_engine.save_file_record({
                    'id': file_id,
                    'file_name': data['filename'],
                    'file_path': public_path,
                    'parent_doctype': data.get('parent_doctype', 'General'),
                    'parent_id': data.get('parent_id', 'UNKNOWN')
                })
                
                self.send_json({"status": "success", "file_path": public_path})
                return
            except Exception as e:
                print(f"Upload Error: {str(e)}")
                self.send_error(500, f"Upload Error: {str(e)}")
                return

        # 4. API: Get Files
        if self.path.startswith("/api/files"):
            try:
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                doctype = qs.get('doctype', [None])[0]
                doc_id = qs.get('id', [None])[0]
                
                if not doctype or not doc_id:
                     self.send_json([])
                     return

                files = db_engine.get_files(doctype, doc_id)
                self.send_json(files)
                return
            except Exception as e:
                self.send_error(500, f"File Fetch Error: {str(e)}")
                return

        # 5. API: Settings & Users
        if self.path == "/api/settings/get":
            self.send_json(db_engine.get_settings())
            return
        
        if self.path == "/api/settings/save":
            try:
                length = int(self.headers['Content-Length'])
                data = json.loads(self.rfile.read(length)) 
                # data = {'system_name': '...', 'theme': '...'}
                for k, v in data.items():
                    db_engine.save_setting(k, v)
                self.send_json({"status": "success"})
                return
            except Exception as e:
                self.send_error(500, str(e))
                return

        if self.path == "/api/users/list":
            self.send_json(db_engine.get_users())
            return

        if self.path == "/api/users/save":
            try:
                length = int(self.headers['Content-Length'])
                data = json.loads(self.rfile.read(length))
                db_engine.save_user(data)
                self.send_json({"status": "success"})
                return
            except Exception as e:
                self.send_error(500, str(e))
                return

        if self.path == "/api/users/delete":
            try:
                length = int(self.headers['Content-Length'])
                data = json.loads(self.rfile.read(length))
                db_engine.delete_user(data['id'])
                self.send_json({"status": "success"})
                return
            except Exception as e:
                self.send_error(500, str(e))
                return

        if self.path.startswith("/api/save"):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                table = data.get('doctype')
                if not table:
                    self.send_error(400, "Missing doctype in payload")
                    return
                
                print(f"DEBUG: Saving to SQL table '{table}'")
                res_id = db_engine.save_one(table, data)
                self.send_json({"id": res_id, "status": "success", "message": "Committed to SQL"})
                return
            except ValueError as ve:
                self.send_error(400, f"Validation Failed: {str(ve)}")
                return
            except Exception as e:
                self.send_error(500, f"Save Error: {str(e)}")
                return
        
        self.send_error(404, "POST endpoint not found")

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # Add CORS for local dev just in case
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def get_metadata(self, doctype):
        dt_name = doctype.lower()
        path = os.path.join(DOCTYPE_ROOT, dt_name, f"{dt_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {"error": "Schema file not found"}

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

def run_server():
    print("="*60)
    print("   CONSULTANCY OS - INDEPENDENT RELATIONAL ENGINE")
    print("="*60)
    print(f"Server URL:  http://localhost:{PORT}/portal")
    print(f"Database:    {db_engine.DB_PATH}")
    print(f"Web Root:    {WEB_ROOT}")
    print(f"Schema Root: {DOCTYPE_ROOT}")
    print("="*60)
    print("\n[Server Live - Awaiting Connections...]")
    
    with ThreadedTCPServer(("", PORT), ConsultancyRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
