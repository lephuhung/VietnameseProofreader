# -*- coding: utf-8 -*-
"""
Convert the office-toolbox sideload .docx to .dotm template
and place in Word STARTUP folder for persistent loading.
"""
import zipfile
import os
import sys
import glob

TEMP = os.environ['TEMP']
WORD_STARTUP = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Word', 'STARTUP')
OUTPUT = os.path.join(WORD_STARTUP, 'VNGrammar.dotm')

def find_sideload_docx():
    pattern = os.path.join(TEMP, 'word add-in*.docx')
    files = glob.glob(pattern)
    return files[0] if files else None

def convert_to_dotm(docx_path):
    os.makedirs(WORD_STARTUP, exist_ok=True)
    
    with zipfile.ZipFile(docx_path, 'r') as zin:
        with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                
                # Change content type from document to template
                if item.filename == '[Content_Types].xml':
                    content = data.decode('utf-8')
                    content = content.replace(
                        'wordprocessingml.document.main+xml',
                        'wordprocessingml.template.main+xml'
                    )
                    data = content.encode('utf-8')
                
                zout.writestr(item, data)
    
    print(f"[OK] Created: {OUTPUT}")
    print(f"     Size: {os.path.getsize(OUTPUT)} bytes")
    return True

if __name__ == '__main__':
    docx = find_sideload_docx()
    if not docx:
        print("[ERROR] Sideload .docx not found in TEMP!")
        sys.exit(1)
    
    print(f"[OK] Source: {docx}")
    convert_to_dotm(docx)
    print("[DONE] VNGrammar.dotm placed in Word STARTUP.")
