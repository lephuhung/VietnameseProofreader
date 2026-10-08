"""Tim entries sai: key == value"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.dictionary import CONFUSED_PAIRS
from engine.dictionary_admin import ADMIN_CONFUSED_PAIRS, ADMIN_CONTEXT_ERRORS, ADMIN_DIALECT

all_cp = {**CONFUSED_PAIRS, **ADMIN_CONFUSED_PAIRS, **ADMIN_CONTEXT_ERRORS, **ADMIN_DIALECT}

print("=== ENTRIES TU THAM CHIEU (key == value) ===")
count = 0
for k, (v, reason, t) in all_cp.items():
    if k.strip().lower() == v.strip().lower():
        count += 1
        print(f'  "{k}" -> "{v}"')
print(f"\nTONG: {count} entries can xoa")
