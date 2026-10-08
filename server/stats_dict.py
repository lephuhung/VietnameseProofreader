"""Thong ke tong tu dien"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.dictionary import CONFUSED_PAIRS, INFORMAL_WORDS, SINO_VIETNAMESE_ERRORS, DIACRITICS_RULES, TONE_MARK_ERRORS
from engine.dictionary_admin import ADMIN_CONFUSED_PAIRS, ADMIN_REDUNDANCY, ADMIN_CONTEXT_ERRORS, ADMIN_DIALECT

# Merge giong nhu rules.py
raw_confused = {**CONFUSED_PAIRS, **ADMIN_CONFUSED_PAIRS, **ADMIN_CONTEXT_ERRORS, **ADMIN_DIALECT}
raw_sino = {**SINO_VIETNAMESE_ERRORS, **ADMIN_REDUNDANCY}

# Loc self-referencing
real_confused = {k: v for k, v in raw_confused.items() if k.strip().lower() != v[0].strip().lower()}
real_sino = {k: v for k, v in raw_sino.items() if k.strip().lower() != v[0].strip().lower()}

print("=" * 60)
print("  THONG KE BO TU DIEN VN GRAMMAR ASSISTANT")
print("=" * 60)
print()
print("--- TU DIEN GOC (dictionary.py) ---")
print(f"  Confused Pairs:        {len(CONFUSED_PAIRS)}")
print(f"  Informal Words:        {len(INFORMAL_WORDS)}")
print(f"  Sino-Vietnamese:       {len(SINO_VIETNAMESE_ERRORS)}")
print(f"  Diacritics Rules:      {len(DIACRITICS_RULES)}")
print(f"  Tone Mark Pairs:       {len(TONE_MARK_ERRORS)}")
print()
print("--- TU DIEN ADMIN (dictionary_admin.py) ---")
print(f"  Admin Confused Pairs:  {len(ADMIN_CONFUSED_PAIRS)}")
print(f"  Admin Redundancy:      {len(ADMIN_REDUNDANCY)}")
print(f"  Admin Context Errors:  {len(ADMIN_CONTEXT_ERRORS)}")
print(f"  Admin Dialect:         {len(ADMIN_DIALECT)}")
print()
print("--- SAU KHI GOP + LOC SELF-REF ---")
print(f"  Confused Pairs (gop):  {len(raw_confused)} raw -> {len(real_confused)} hieu luc")
print(f"  Sino/Redundancy (gop): {len(raw_sino)} raw -> {len(real_sino)} hieu luc")
print(f"  Informal Words:        {len(INFORMAL_WORDS)}")
print(f"  Diacritics Rules:      {len(DIACRITICS_RULES)}")
print(f"  Self-ref bi loai:      {len(raw_confused) - len(real_confused) + len(raw_sino) - len(real_sino)}")
print()
total = len(real_confused) + len(real_sino) + len(INFORMAL_WORDS) + len(DIACRITICS_RULES)
print(f"  *** TONG ENTRIES HIEU LUC: {total} ***")
print()

# Phan loai
types = {}
for k, (v, r, t) in real_confused.items():
    types[t] = types.get(t, 0) + 1
print("--- PHAN LOAI LOI ---")
for t, c in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {t:20s}: {c:4d}")
print(f"  {'redundancy':20s}: {len(real_sino):4d}")
print(f"  {'informal':20s}: {len(INFORMAL_WORDS):4d}")
print(f"  {'diacritics':20s}: {len(DIACRITICS_RULES):4d}")

# Dung luong
dict_file = os.path.join(os.path.dirname(__file__), 'engine', 'dictionary.py')
admin_file = os.path.join(os.path.dirname(__file__), 'engine', 'dictionary_admin.py')
d1 = os.path.getsize(dict_file) if os.path.exists(dict_file) else 0
d2 = os.path.getsize(admin_file) if os.path.exists(admin_file) else 0
print()
print(f"--- DUNG LUONG FILE ---")
print(f"  dictionary.py:       {d1/1024:.1f} KB")
print(f"  dictionary_admin.py: {d2/1024:.1f} KB")
print(f"  TONG:                {(d1+d2)/1024:.1f} KB")
print("=" * 60)
