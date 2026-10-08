"""
Download Office.js files for offline use.
Run once (with internet): python tools\download_officejs.py
"""
import os
import urllib.request
import ssl

BASE_URL = "https://appsforoffice.microsoft.com/lib/1/hosted"
FILES = [
    ("office.js", f"{BASE_URL}/office.js"),
    ("word-win32-16.01.js", f"{BASE_URL}/word-win32-16.01.js"),
    (os.path.join("en-us", "office_strings.js"), f"{BASE_URL}/en-us/office_strings.js"),
]

def main():
    # Target: addin/lib/ relative to this script's parent
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.join(script_dir, "..", "addin", "lib")
    os.makedirs(lib_dir, exist_ok=True)

    # Allow self-signed certs (some corporate proxies)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for filename, url in FILES:
        dest = os.path.join(lib_dir, filename)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"  Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, dest)
            size = os.path.getsize(dest)
            print(f"  [OK] {filename} ({size:,} bytes)")
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")

    print()
    print("  Done! Office.js files saved to addin/lib/")
    print("  You can now switch index.html back to local:")
    print('  <script src="lib/office.js" type="text/javascript"></script>')

if __name__ == "__main__":
    main()
