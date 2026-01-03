
import os

def ensure_upload_dir():
    path = r"d:\Custom_System_Copy\System_Core\frontend\uploads"
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created upload directory: {path}")
    else:
        print(f"Upload directory exists: {path}")

if __name__ == "__main__":
    ensure_upload_dir()
