"""
Hybrid Analyzer — Bộ phân tích kết hợp
=========================================
Điều phối 2 lớp kiểm tra:
  Layer 1: Rule-based (từ điển + quy tắc) — siêu nhanh
  Layer 2: NLP context (underthesea) — phân tích sâu + disambiguation

Layer 2 NÂNG CẤP kết quả Layer 1:
  - Khi Layer 1 trả về nhiều gợi ý (VD: "đồng ý / ổn thỏa / phù hợp")
  - Layer 2 dùng POS tag ngữ cảnh để chọn MỘT gợi ý chuẩn nhất
"""
import time
import logging
import unicodedata
from .hunspell_checker import check_hunspell
from .rules import check_rules
from . import nlp_analyzer

logger = logging.getLogger("vngrammar.analyzer")

# Màu sắc và label cho từng loại lỗi (dùng cho frontend)
ERROR_TYPE_INFO = {
    "spelling":      {"label": "Chính tả",    "color": "#EF4444", "priority": 0},
    "context":       {"label": "Ngữ cảnh",    "color": "#F59E0B", "priority": 1},
    "diacritics":    {"label": "Dấu thanh",   "color": "#EC4899", "priority": 2},
    "redundancy":    {"label": "Thừa từ",     "color": "#8B5CF6", "priority": 3},
    "informal":      {"label": "Khẩu ngữ",   "color": "#3B82F6", "priority": 4},
    "dialect":       {"label": "Phương ngữ",  "color": "#06B6D4", "priority": 5},
    "repetition":    {"label": "Lặp từ",      "color": "#F97316", "priority": 6},
    "style":         {"label": "Văn phong",   "color": "#6366F1", "priority": 7},
    "punctuation":   {"label": "Chấm câu",    "color": "#14B8A6", "priority": 8},
    "capitalization": {"label": "Viết hoa",   "color": "#A855F7", "priority": 9},
    "formal":        {"label": "Hành chính",  "color": "#0EA5E9", "priority": 10},
}


def analyze(text: str, settings: dict = None) -> dict:
    """
    Phân tích văn bản tiếng Việt theo cơ chế Hybrid.
    
    Quy trình:
      1. Layer 1 quét siêu nhanh bằng từ điển
      2. Layer 2 phân tích ngữ cảnh + disambiguation
      3. Layer 2 nâng cấp gợi ý của Layer 1 (nếu có context rule)
      4. Gộp kết quả, loại trùng, gắn metadata, sắp xếp
    """
    if not text or not text.strip():
        return {
            "status": "success",
            "message": "Văn bản trống.",
            "errors": [],
            "stats": {},
        }

    original_text = text
    # Keep a boundary map back to the original code points (NFD and emoji).
    clusters = []
    for index, char in enumerate(text):
        if unicodedata.combining(char) and clusters:
            clusters[-1][0] += char
            clusters[-1][2] = index + 1
        else:
            clusters.append([char, index, index + 1])
    starts, ends, normalized = [], [], []
    for cluster, start, end in clusters:
        value = unicodedata.normalize('NFC', cluster)
        normalized.append(value)
        starts.extend([start] * len(value))
        ends.extend([end] * len(value))
    text = ''.join(normalized)
    all_errors = []
    if settings is None:
        settings = {}

    layer1_enabled = settings.get("layer1_enabled", True)
    layer2_enabled = settings.get("layer2_enabled", True)

    # ========== LAYER 1: Rule-based (Siêu nhanh) ==========
    t1_start = time.perf_counter()
    layer1_errors = check_rules(text) if layer1_enabled else []
    hunspell_errors = check_hunspell(text, settings, layer1_errors) if layer1_enabled and settings.get('hunspell_enabled', True) else []
    layer1_errors.extend(hunspell_errors)
    t1_end = time.perf_counter()
    t1_ms = round((t1_end - t1_start) * 1000, 2)
    
    logger.info(f"Layer 1 (Rules): {len(layer1_errors)} lỗi, {t1_ms}ms")

    # ========== LAYER 2: NLP Context ==========
    t2_start = time.perf_counter()
    layer2_available = nlp_analyzer.is_available() if layer2_enabled else False
    layer2_errors = []
    pos_tags = []

    if layer2_enabled and layer2_available:
        try:
            # 2a. Lấy POS tags cho toàn bộ text
            pos_tags = nlp_analyzer.get_pos_tags(text)

            # 2b. DISAMBIGUATION: Nâng cấp gợi ý Layer 1 bằng ngữ cảnh
            if pos_tags:
                _refine_suggestions_with_context(layer1_errors, pos_tags, text)

            # 2c. Phân tích lỗi chỉ Layer 2 mới bắt được
            layer2_errors = nlp_analyzer.analyze_context(text)
            logger.info(f"Layer 2 (NLP): {len(layer2_errors)} lỗi, disambiguation applied")
        except Exception as e:
            logger.error(f"Layer 2 lỗi: {e}")
    elif layer2_enabled:
        logger.warning("Layer 2 (NLP) không khả dụng, chỉ dùng Layer 1.")

    t2_end = time.perf_counter()
    t2_ms = round((t2_end - t2_start) * 1000, 2)

    all_errors.extend(layer1_errors)
    all_errors.extend(layer2_errors)

    # ========== Lọc theo Settings ==========
    filtered_errors = _filter_by_settings(all_errors, settings)

    # ========== Gộp, gắn metadata, loại trùng, sắp xếp ==========
    unique_errors = _deduplicate(filtered_errors)
    
    # Gắn metadata (label, color) cho frontend
    for err in unique_errors:
        err_type = err.get("type", "spelling")
        type_info = ERROR_TYPE_INFO.get(err_type, ERROR_TYPE_INFO["spelling"])
        err["label"] = type_info["label"]
        err["color"] = type_info["color"]
        # GIỮ position để frontend biết chính xác vị trí lỗi
        # (tránh highlight sai khi từ xuất hiện nhiều lần)

    # Sắp xếp theo priority (chính tả trước)
    unique_errors.sort(key=lambda e: ERROR_TYPE_INFO.get(e.get("type", ""), {}).get("priority", 99))

    for err in unique_errors:
        start = err.get('position', 0)
        end = start + len(err.get('word', ''))
        if 0 <= start < end <= len(starts):
            original_start, original_end = starts[start], ends[end - 1]
            err['position'] = original_start
            err['word'] = original_text[original_start:original_end]
            err['length'] = original_end - original_start
            err['position_utf16'] = len(original_text[:original_start].encode('utf-16-le')) // 2
            err['length_utf16'] = len(err['word'].encode('utf-16-le')) // 2

    total_ms = round(t1_ms + t2_ms, 2)

    # Tạo message
    if unique_errors:
        message = f"Phát hiện {len(unique_errors)} vấn đề ({total_ms}ms)"
    else:
        message = f"Văn bản chuẩn, không phát hiện lỗi ({total_ms}ms)"

    return {
        "status": "success",
        "message": message,
        "errors": unique_errors,
        "stats": {
            "layer1_time_ms": t1_ms,
            "layer2_time_ms": t2_ms,
            "total_time_ms": total_ms,
            "layer1_errors": len(layer1_errors),
            "layer2_errors": len(layer2_errors),
            "layer2_available": layer2_available,
        }
    }


def _refine_suggestions_with_context(errors: list[dict], pos_tags: list, text: str):
    """
    Dùng POS tags để NÂNG CẤP gợi ý của Layer 1.
    
    Ví dụ: Layer 1 gợi ý "ok" → "đồng ý / ổn thỏa / phù hợp"
           Layer 2 xem xét POS: "triển khai(V) ok" → "ok" đứng sau Verb
           → Chọn chính xác: "ổn thỏa"
    """
    for err in errors:
        word = err.get("word", "").lower().strip()

        # Chỉ refine nếu từ có trong bảng context
        if word not in nlp_analyzer.CONTEXT_SUGGESTIONS:
            continue

        # Tìm vị trí của từ đó trong danh sách POS tags
        word_index = _find_word_in_pos_tags(word, pos_tags)
        if word_index is None:
            continue

        # Lấy gợi ý phù hợp nhất theo ngữ cảnh
        refined = nlp_analyzer.disambiguate_suggestion(word, pos_tags, word_index)
        if refined:
            old_suggestion = err["suggestion"]
            err["suggestion"] = refined
            err["reason"] = f"[AI ngữ cảnh] {err['reason']}"
            logger.info(f"Disambiguation: '{word}' | '{old_suggestion}' → '{refined}'")


def _find_word_in_pos_tags(word: str, pos_tags: list) -> int | None:
    """Tìm index của một từ trong danh sách POS tags."""
    word_lower = word.lower()
    for i, (w, tag) in enumerate(pos_tags):
        if w.lower() == word_lower:
            return i
    return None


def _filter_by_settings(errors: list[dict], settings: dict) -> list[dict]:
    """Lọc lỗi theo cài đặt người dùng."""
    if not settings:
        return errors

    # Mapping: settings key → error types bị ảnh hưởng
    type_toggles = {
        "check_informal": ["informal"],
        "check_dialect": ["dialect"],
        "check_punctuation": ["punctuation"],
        "check_capitalization": ["capitalization"],
        "check_redundancy": ["redundancy"],
    }

    # Danh sách loại lỗi bị tắt
    disabled_types = set()
    for setting_key, error_types in type_toggles.items():
        if not settings.get(setting_key, True):
            disabled_types.update(error_types)

    # Nếu writing_style là "free" thì tắt thêm formal + style + dialect
    writing_style = settings.get("writing_style", "administrative")
    if writing_style == "free":
        disabled_types.update(["formal", "style", "dialect"])
    elif writing_style == "journalism":
        disabled_types.update(["formal"])

    # Lọc
    if not disabled_types:
        return errors

    return [err for err in errors if err.get("type", "") not in disabled_types]


def _deduplicate(errors: list[dict]) -> list[dict]:
    """Loại bỏ các lỗi trùng lặp (cùng từ sai, cùng vị trí)."""
    seen = set()
    unique = []
    for err in errors:
        key = (err.get("position", 0), err.get("word", "").lower())
        if key not in seen:
            seen.add(key)
            unique.append(err)
    return unique
