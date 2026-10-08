"""
Rule-Based Checker (Layer 1 — Siêu nhanh)
============================================
Quét văn bản bằng các bộ quy tắc và từ điển có sẵn.
Không cần AI, chạy trong < 10ms.
"""
import re
import os
import unicodedata
from .dictionary import (
    CONFUSED_PAIRS,
    INFORMAL_WORDS,
    SINO_VIETNAMESE_ERRORS,
    DIACRITICS_RULES,
)
from .dictionary_admin import (
    ADMIN_CONFUSED_PAIRS,
    ADMIN_REDUNDANCY,
    ADMIN_CONTEXT_ERRORS,
    ADMIN_DIALECT,
)

# Gộp từ điển: admin mở rộng ghi đè nếu trùng key
_raw_confused = {**CONFUSED_PAIRS, **ADMIN_CONFUSED_PAIRS, **ADMIN_CONTEXT_ERRORS, **ADMIN_DIALECT}
_raw_sino = {**SINO_VIETNAMESE_ERRORS, **ADMIN_REDUNDANCY}

# Tự động loại bỏ entries self-referencing (key == value → false positive!)
ALL_CONFUSED_PAIRS = {
    k: v for k, v in _raw_confused.items()
    if k.strip().lower() != v[0].strip().lower()
}
ALL_SINO_ERRORS = {
    k: v for k, v in _raw_sino.items()
    if k.strip().lower() != v[0].strip().lower()
}

import logging as _log
_removed = len(_raw_confused) - len(ALL_CONFUSED_PAIRS) + len(_raw_sino) - len(ALL_SINO_ERRORS)
if _removed > 0:
    _log.getLogger("vngrammar.rules").info(f"Đã loại {_removed} entries self-referencing khỏi từ điển.")

# Danh sách từ người dùng chọn bỏ qua (được nạp bởi main.py)
IGNORED_WORDS: set = set()

# ============================================================
# WHITELIST: Từ ghép hợp lệ chứa âm tiết trùng phương ngữ
# Khi phát hiện từ đơn âm (chi, mô, răng...), kiểm tra ngữ cảnh
# xung quanh. Nếu tạo thành từ ghép hợp lệ → bỏ qua, không báo lỗi.
# ============================================================
DIALECT_COMPOUND_WHITELIST = {
    "chi": [
        "chi tiết", "chi phí", "chi nhánh", "chi bộ", "chi trả",
        "chi viện", "chi cục", "chi hội", "chi đoàn", "chi ủy",
        "chi trội", "chi ly", "chi chít", "chi mại", "chi phối",
        "chi tiêu", "chi dẫn", "chi đội", "chi lưu", "chi đạo",
        "chi bằng", "chi li", "chi chuyển", "chi lương",
        "ít chi", "bao chi", "chi viết", "chi cho",
        "chi bộ đảng", "chi huy", "chi tiêu công",
    ],
    "mô": [
        "mô tả", "mô hình", "mô phỏng", "mô men", "mô đun",
        "mô típ", "mô phạm", "mô thức", "mô giới", "mô đất",
        "mô đá", "mô bệnh học", "mô liên kết", "mô mềm",
        "mô sụn", "mô xương", "mô cơ", "mô thần kinh",
        # Bổ sung
        "quy mô", "mô hồ", "mô phạm", "mô tê", "mô tô",
        "mô phạm", "mô hình hóa", "mô tả chi tiết",
        "quy mô lớn", "quy mô nhỏ",
    ],
    "răng": [
        "răng cưa", "răng miệng", "răng sữa", "răng nanh",
        "răng hàm", "răng khôn", "răng bọc", "nhổ răng",
        "đánh răng", "kem đánh răng", "bàn chải răng",
        "đau răng", "sâu răng", "chải răng", "niềng răng",
        "trồng răng", "hàm răng", "ê răng", "mọc răng",
        "cấy răng", "bọc răng", "tẩy răng",
    ],
    "tui": [
        "cái tui", "túi tui",
    ],
}

# Load whitelist bổ sung từ user (nếu có)
import json as _json
_user_wl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'user_whitelist.json')
try:
    if os.path.exists(_user_wl_path):
        with open(_user_wl_path, 'r', encoding='utf-8') as _f:
            _user_wl = _json.load(_f)
        for _key, _vals in _user_wl.items():
            _key_lower = _key.lower()
            if _key_lower in DIALECT_COMPOUND_WHITELIST:
                DIALECT_COMPOUND_WHITELIST[_key_lower].extend([v.lower() for v in _vals])
            else:
                DIALECT_COMPOUND_WHITELIST[_key_lower] = [v.lower() for v in _vals]
        _log.getLogger("vngrammar.rules").info(f"Loaded user whitelist: {sum(len(v) for v in _user_wl.values())} entries")
except Exception as _e:
    _log.getLogger("vngrammar.rules").warning(f"Could not load user whitelist: {_e}")

def _is_part_of_compound(text_lower: str, pos: int, word_lower: str) -> bool:
    """
    Kiểm tra xem từ tại vị trí `pos` có nằm trong một từ ghép hợp lệ không.
    Nếu có → return True (bỏ qua, không báo lỗi).
    """
    if word_lower not in DIALECT_COMPOUND_WHITELIST:
        return False

    compounds = DIALECT_COMPOUND_WHITELIST[word_lower]
    for compound in compounds:
        compound_lower = compound.lower()
        # Tìm compound trong text xung quanh vị trí pos
        # compound có thể bắt đầu từ trước pos hoặc tại pos
        for offset in range(len(compound_lower)):
            check_start = pos - offset
            if check_start < 0:
                continue
            check_end = check_start + len(compound_lower)
            if check_end > len(text_lower):
                continue
            candidate = text_lower[check_start:check_end]
            if candidate == compound_lower:
                # Kiểm tra ranh giới từ
                before_ok = (check_start == 0) or not text_lower[check_start - 1].isalpha()
                after_ok = (check_end >= len(text_lower)) or not text_lower[check_end].isalpha()
                if before_ok and after_ok:
                    return True
    return False


def match_capitalization(original: str, suggestion: str) -> str:
    """
    Giữ kiểu viết hoa/thường của từ gốc cho suggestion.
    VD: original='Vô hình chung', suggestion='vô hình trung' → 'Vô hình trung'
        original='VÔ HÌNH CHUNG', suggestion='vô hình trung' → 'VÔ HÌNH TRUNG'
        original='sáng lạng',     suggestion='xán lạn'       → 'xán lạn'
    """
    if not original or not suggestion:
        return suggestion

    # Nếu có chứa '/' (nhiều gợi ý), giữ nguyên
    if '/' in suggestion:
        # Chỉ viết hoa chữ đầu tiên của mỗi gợi ý nếu original viết hoa
        if original[0].isupper():
            parts = suggestion.split('/')
            return '/'.join(p.strip().capitalize() if p.strip() else p for p in parts)
        return suggestion

    # Toàn bộ viết hoa: 'VÔ HÌNH CHUNG' → 'VÔ HÌNH TRUNG'
    if original.isupper():
        return suggestion.upper()

    # Chữ đầu viết hoa: 'Vô hình chung' → 'Vô hình trung'
    if original[0].isupper():
        return suggestion[0].upper() + suggestion[1:]

    return suggestion


def check_rules(text: str) -> list[dict]:
    """
    Quét văn bản theo quy tắc từ điển.
    Trả về danh sách lỗi: [{ word, suggestion, reason, type, position }]
    """
    errors = []
    # Normalize Unicode NFC — Word có thể gửi NFD (decomposed Vietnamese)
    text = unicodedata.normalize('NFC', text)
    text_lower = text.lower()

    # ---- 1. Kiểm tra cụm từ sai (Confused Pairs) ----
    for wrong, (correct, reason, err_type) in ALL_CONFUSED_PAIRS.items():
        wrong_lower = wrong.lower()
        # Tìm tất cả vị trí xuất hiện
        start = 0
        while True:
            pos = text_lower.find(wrong_lower, start)
            if pos == -1:
                break
            # Kiểm tra ranh giới từ (word boundary) để tránh bắt sai
            before_ok = (pos == 0) or not text[pos - 1].isalpha()
            after_pos = pos + len(wrong_lower)
            after_ok = (after_pos >= len(text)) or not text[after_pos].isalpha()

            if before_ok and after_ok:
                original_word = text[pos:pos + len(wrong)]

                # Kiểm tra false positive phương ngữ:
                # Nếu từ đơn âm nằm trong từ ghép hợp lệ → bỏ qua
                if err_type == "dialect" and _is_part_of_compound(text_lower, pos, wrong_lower):
                    start = pos + 1
                    continue

                errors.append({
                    "word": original_word,
                    "suggestion": match_capitalization(original_word, correct),
                    "reason": reason,
                    "type": err_type,
                    "position": pos,
                })
            start = pos + 1

    # ---- 2. Kiểm tra từ viết tắt / khẩu ngữ / teencode ----
    for word_lower, (correct, reason) in INFORMAL_WORDS.items():
        # Tìm tất cả vị trí xuất hiện (word boundary)
        pattern = re.compile(r'\b' + re.escape(word_lower) + r'\b', re.IGNORECASE)
        for match in pattern.finditer(text):
            pos = match.start()
            matched_word = text[pos:pos + len(word_lower)]

            # Bỏ qua single-letter list markers: "A.", "B.", "a)", "1."
            # Và abbreviation pairs: "b/c", "p/h", "đ/c"
            if len(word_lower) == 1:
                after_pos = pos + 1
                before_pos = pos - 1
                # Check: X. X) X:
                if after_pos < len(text) and text[after_pos] in '.):':
                    continue
                # Check: X/Y hoặc Y/X (abbreviation pairs)
                if after_pos < len(text) and text[after_pos] == '/':
                    continue
                if before_pos >= 0 and text[before_pos] == '/':
                    continue

            errors.append({
                "word": matched_word,
                "suggestion": match_capitalization(matched_word, correct),
                "reason": f"Khẩu ngữ/Viết tắt: {reason}",
                "type": "informal",
                "position": pos,
            })

    # ---- 3. Kiểm tra cụm từ thừa / lặp nghĩa (Sino-Vietnamese) ----
    for wrong, (correct, reason) in ALL_SINO_ERRORS.items():
        wrong_lower = wrong.lower()
        start = 0
        while True:
            pos = text_lower.find(wrong_lower, start)
            if pos == -1:
                break
            # Kiểm tra ranh giới từ
            before_ok = (pos == 0) or not text[pos - 1].isalpha()
            after_pos = pos + len(wrong_lower)
            after_ok = (after_pos >= len(text)) or not text[after_pos].isalpha()

            if before_ok and after_ok:
                original_word = text[pos:pos + len(wrong)]
                errors.append({
                    "word": original_word,
                    "suggestion": match_capitalization(original_word, correct),
                    "reason": f"Lỗi lặp/thừa từ: {reason}",
                    "type": "redundancy",
                    "position": pos,
                })
            start = pos + 1

    # ---- 4. Kiểm tra quy tắc đặt dấu thanh ----
    # Tìm TOÀN BỘ từ chứa vần sai, không chỉ 2 ký tự vần
    # LƯU Ý: "qu" là phụ âm ghép → "u" thuộc phụ âm, KHÔNG phải nguyên âm
    #   → "quý" đúng (dấu trên 'y'), KHÔNG PHẢI "qúy"
    #   → "quả" đúng (dấu trên 'a'), KHÔNG PHẢI "qủa"
    #   Tương tự: "gi" trong một số trường hợp
    for wrong_diac, (correct_diac, reason) in DIACRITICS_RULES.items():
        start = 0
        while True:
            pos = text_lower.find(wrong_diac, start)
            if pos == -1:
                break
            # Mở rộng ra để bắt cả từ chứa vần sai
            word_start = pos
            while word_start > 0 and text[word_start - 1].isalpha():
                word_start -= 1
            word_end = pos + len(wrong_diac)
            while word_end < len(text) and text[word_end].isalpha():
                word_end += 1
            
            full_word = text[word_start:word_end]
            full_word_lower = full_word.lower()
            
            # === BỎ QUA nếu vần nằm sau phụ âm ghép "qu" ===
            # "qu" + nguyên âm: dấu thanh đặt trên nguyên âm sau "u"
            # VD: quý, quả, quà, quỳ, quỷ — đã đúng vị trí
            if wrong_diac.startswith('u') and pos > 0 and text[pos - 1].lower() == 'q':
                start = pos + 1
                continue
            
            fixed_word = full_word.replace(wrong_diac, correct_diac)
            # Cũng thử với chữ hoa
            wrong_upper = wrong_diac[0].upper() + wrong_diac[1:]
            correct_upper = correct_diac[0].upper() + correct_diac[1:]
            fixed_word = fixed_word.replace(wrong_upper, correct_upper)
            
            if full_word.lower() != fixed_word.lower():
                errors.append({
                    "word": full_word,
                    "suggestion": fixed_word,
                    "reason": f"Lỗi vị trí dấu thanh: {reason}",
                    "type": "diacritics",
                    "position": word_start,
                })
            start = pos + 1

    # ---- 5. Kiểm tra lỗi lặp từ liên tiếp ----
    repeat_pattern = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE | re.UNICODE)
    for match in repeat_pattern.finditer(text):
        repeated_word = match.group(1)
        # Bỏ qua số (100 → "0 0"), ký tự đơn, và từ láy hợp lệ
        if repeated_word.isdigit():
            continue
        if len(repeated_word) <= 1:
            continue
        valid_reduplications = {
            "xanh", "đỏ", "nhỏ", "to", "xa", "gần", "tốt", "xấu",
            "đẹp", "hay", "vui", "buồn", "nhanh", "chậm", "nhẹ",
            "nặng", "dài", "ngắn", "cao", "thấp", "rộng", "hẹp",
        }
        if repeated_word.lower() not in valid_reduplications:
            errors.append({
                "word": match.group(0),
                "suggestion": repeated_word,
                "reason": f"Lỗi lặp từ: '{repeated_word}' xuất hiện liên tiếp 2 lần.",
                "type": "repetition",
                "position": match.start(),
            })

    # Lọc bỏ từ người dùng đã chọn bỏ qua
    if IGNORED_WORDS:
        errors = [e for e in errors if e["word"].lower() not in IGNORED_WORDS]

    # Sắp xếp lỗi theo vị trí xuất hiện trong văn bản
    errors.sort(key=lambda e: e.get("position", 0))

    # Loại bỏ trùng lặp (cùng vị trí, cùng từ)
    seen = set()
    unique_errors = []
    for err in errors:
        key = (err["position"], err["word"].lower())
        if key not in seen:
            seen.add(key)
            unique_errors.append(err)

    return unique_errors
