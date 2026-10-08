"""
NLP Analyzer (Layer 2 — Phân tích ngữ cảnh sâu)
===================================================
Sử dụng thư viện underthesea để:
  - Tách từ (Word Segmentation)
  - Gán nhãn từ loại (POS Tagging)
  - Phân tích ngữ cảnh để chọn gợi ý chính xác nhất
  - Phát hiện lỗi mà Layer 1 (từ điển) không bắt được
"""
import re
import logging

logger = logging.getLogger("vngrammar.nlp")

# Lazy-load underthesea để không làm chậm khởi động
_word_tokenize = None
_pos_tag = None


def _load_nlp():
    """Tải thư viện NLP lần đầu tiên khi cần (lazy-loading)."""
    global _word_tokenize, _pos_tag
    if _word_tokenize is None:
        try:
            from underthesea import word_tokenize, pos_tag
            _word_tokenize = word_tokenize
            _pos_tag = pos_tag
            logger.info("Đã tải thư viện NLP underthesea thành công.")
        except ImportError:
            logger.warning("Không tìm thấy thư viện underthesea. Layer 2 bị vô hiệu hóa.")
        except Exception as e:
            logger.warning(f"Lỗi khi tải underthesea: {e}")


def is_available() -> bool:
    """Kiểm tra xem NLP engine có sẵn sàng không."""
    _load_nlp()
    return _word_tokenize is not None


# ============================================================
#  CONTEXT-AWARE DISAMBIGUATION
#  Bản đồ ngữ cảnh: dựa vào POS tag xung quanh để chọn gợi ý
# ============================================================

# Mapping POS tag → vai trò nghĩa
# Các POS tag chính của underthesea:
#   N = Noun, V = Verb, A = Adjective, R = Adverb
#   P = Pronoun, E = Preposition, C = Conjunction, T = Particle

CONTEXT_SUGGESTIONS = {
    # Từ "ok" tùy ngữ cảnh
    "ok": {
        "after_verb": "ổn thỏa",         # "triển khai ok" → "triển khai ổn thỏa"
        "after_adjective": "phù hợp",     # "rất ok" → "rất phù hợp"
        "sentence_start": "Được rồi",     # "Ok, tôi đồng ý" → "Được rồi, tôi đồng ý"  
        "after_noun": "phù hợp",          # "phương án ok" → "phương án phù hợp"
        "standalone": "đồng ý",           # "Ok" (đứng một mình)
        "default": "đồng ý / ổn thỏa",
    },
    "oke": {
        "after_verb": "ổn thỏa",
        "sentence_start": "Được rồi",
        "default": "đồng ý / ổn thỏa",
    },
    "okie": {
        "after_verb": "ổn thỏa",
        "sentence_start": "Được rồi",
        "default": "đồng ý / ổn thỏa",
    },
    # Từ "dc" / "đc" tùy ngữ cảnh
    "dc": {
        "after_verb": "được",             # "làm dc" → "làm được"
        "before_verb": "có thể",          # "dc làm" → "có thể làm"
        "standalone": "được",
        "default": "được",
    },
    "đc": {
        "after_verb": "được",
        "before_verb": "có thể",
        "default": "được",
    },
    # "j" tùy ngữ cảnh
    "j": {
        "after_verb": "gì",               # "làm j" → "làm gì"
        "after_preposition": "gì",
        "default": "gì",
    },
}


def _get_context_position(word_lower: str, pos_tags: list, word_index: int) -> str:
    """
    Xác định vị trí ngữ cảnh của một từ trong câu.
    Trả về: 'after_verb', 'after_noun', 'sentence_start', 'standalone', v.v.
    """
    total = len(pos_tags)

    # Đứng đầu câu
    if word_index == 0:
        return "sentence_start"

    # Đứng một mình
    if total == 1:
        return "standalone"

    # Kiểm tra từ đứng trước
    if word_index > 0:
        prev_word, prev_tag = pos_tags[word_index - 1]
        if prev_tag.startswith('V'):
            return "after_verb"
        elif prev_tag.startswith('N'):
            return "after_noun"
        elif prev_tag.startswith('A') or prev_tag.startswith('R'):
            return "after_adjective"
        elif prev_tag.startswith('E'):
            return "after_preposition"

    # Kiểm tra từ đứng sau
    if word_index < total - 1:
        next_word, next_tag = pos_tags[word_index + 1]
        if next_tag.startswith('V'):
            return "before_verb"
        elif next_tag.startswith('N'):
            return "before_noun"

    return "default"


def disambiguate_suggestion(word: str, pos_tags: list, word_index: int) -> str | None:
    """
    Dùng POS tags ngữ cảnh để chọn gợi ý chính xác nhất cho một từ.
    
    Returns:
        Gợi ý phù hợp nhất, hoặc None nếu không có context rule.
    """
    word_lower = word.lower().strip()

    if word_lower not in CONTEXT_SUGGESTIONS:
        return None

    context_map = CONTEXT_SUGGESTIONS[word_lower]
    position = _get_context_position(word_lower, pos_tags, word_index)

    # Trả về gợi ý theo vị trí, fallback về default
    suggestion = context_map.get(position, context_map.get("default"))

    logger.debug(f"Disambiguate '{word}': position={position} → '{suggestion}'")
    return suggestion


# ============================================================
#  MAIN ANALYSIS FUNCTIONS
# ============================================================

def analyze_context(text: str) -> list[dict]:
    """
    Phân tích ngữ cảnh sâu bằng NLP.
    Trả về danh sách lỗi: [{ word, suggestion, reason, type, position }]
    """
    _load_nlp()
    if _word_tokenize is None:
        return []

    errors = []

    try:
        # --- 1. Gán nhãn từ loại (POS Tagging) ---
        pos_tags = _pos_tag(text)
        logger.debug(f"POS Tags: {pos_tags}")

        # --- 2. Phát hiện câu quá dài (văn phong hành chính) ---
        errors.extend(_check_sentence_length(text))

        # --- 3. Phát hiện lỗi chấm câu ---
        errors.extend(_check_punctuation(text))

        # --- 4. Phát hiện viết hoa sai ---
        errors.extend(_check_capitalization(text))

    except Exception as e:
        logger.error(f"Lỗi khi phân tích NLP: {e}")

    return errors


def get_pos_tags(text: str) -> list:
    """
    Trả về POS tags cho một đoạn text.
    Dùng cho Hybrid Analyzer để phối hợp Layer 1 + Layer 2.
    """
    _load_nlp()
    if _pos_tag is None:
        return []
    try:
        return _pos_tag(text)
    except Exception:
        return []


def _check_sentence_length(text: str) -> list[dict]:
    """
    Cảnh báo câu quá dài (> 60 từ) trong văn phong hành chính.
    Split theo: dấu chấm câu (.!?), dấu chấm phẩy (;), xuống hàng (\n\r).
    """
    errors = []
    sentences = re.split(r'[.!?;]\s+|[\r\n]+', text)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        word_count = len(sentence.split())
        if word_count > 60:
            pos = text.find(sentence[:30])
            errors.append({
                "word": sentence[:50] + "...",
                "suggestion": "Nên tách thành 2-3 câu ngắn hơn",
                "reason": f"Câu quá dài ({word_count} từ). Văn phong hành chính yêu cầu câu ngắn gọn, dễ hiểu (nên dưới 40 từ).",
                "type": "style",
                "position": pos if pos != -1 else 0,
            })

    return errors


def _is_in_url_or_special(text: str, pos: int) -> bool:
    """
    Kiểm tra vị trí `pos` có nằm trong URL, email, đường dẫn file,
    hoặc viết tắt phổ biến hay không.
    """
    # Tìm "từ" chứa vị trí pos (mở rộng ra 2 bên cho tới khoảng trắng)
    start = pos
    while start > 0 and text[start - 1] not in ' \t\n\r':
        start -= 1
    end = pos
    while end < len(text) and text[end] not in ' \t\n\r':
        end += 1
    token = text[start:end]

    # URL patterns
    if re.search(r'https?://', token, re.IGNORECASE):
        return True
    if re.search(r'www\.', token, re.IGNORECASE):
        return True
    # Email
    if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', token):
        return True
    # File paths (C:\..., /usr/..., file.txt, file.docx)
    if re.search(r'[A-Za-z]:\\', token):
        return True
    if re.search(r'\.\w{2,4}$', token) and not re.search(r'^[A-ZÀ-Ỹ]', token):
        return True
    # Số thập phân: 3.14, 1.000.000
    if re.search(r'\d\.\d', token):
        return True

    return False


# Viết tắt phổ biến tiếng Việt: dấu chấm sau không phải kết thúc câu
_ABBREVIATIONS = re.compile(
    r'(?:PGS|TS|ThS|GS|CN|BS|KTS|TSKH|PTS'
    r'|TP|TX|TT|Tp|Tx|Tt'
    r'|UBND|HĐND|MTTQ|ĐBQH|BCH|BTV|HN'
    r'|Tr|tr|Th|th|St|st|Dr|Mr|Ms|Mrs'
    r'|Corp|Inc|Co|Ltd|JSC|LLC'
    r'|vs|etc|no|No|vol|Vol'
    r'|[A-Z]{1,4})\.$'
)


def _check_punctuation(text: str) -> list[dict]:
    """
    Phát hiện lỗi chấm câu phổ biến.
    BỎ QUA: URLs, emails, file paths, số thập phân, viết tắt phổ biến,
    và paragraph breaks (dấu chấm + newlines).
    """
    errors = []

    # 1. Khoảng trắng trước dấu phẩy/chấm: "từ ," → "từ,"
    #    CHỈ match space/tab trên cùng dòng, KHÔNG match newline
    for match in re.finditer(r'(\S+)[^\S\n]+([,.])', text):
        pos = match.start()
        if _is_in_url_or_special(text, pos):
            continue
        word_before = match.group(1)
        punct = match.group(2)
        full_match = match.group()
        fixed = word_before + punct
        errors.append({
            "word": full_match,
            "suggestion": fixed,
            "reason": f"Không được có khoảng trắng trước dấu '{punct}'.",
            "type": "punctuation",
            "position": pos,
        })

    # 2. Thiếu khoảng trắng sau dấu phẩy: ",từ" (trừ số thập phân)
    for match in re.finditer(r',([^\s\d"\'\)])', text):
        pos = match.start()
        if _is_in_url_or_special(text, pos):
            continue
        char_after = match.group(1)
        errors.append({
            "word": "," + char_after,
            "suggestion": ", " + char_after,
            "reason": "Phải có đúng 1 khoảng trắng sau dấu phẩy.",
            "type": "punctuation",
            "position": pos,
        })

    # 3. Thiếu khoảng trắng sau dấu chấm: ".Từ"
    #    BỎ QUA: viết tắt, URLs, paragraph breaks
    for match in re.finditer(r'\.([A-Za-zÀ-ỹ])', text):
        pos = match.start()
        if _is_in_url_or_special(text, pos):
            continue
        # Bỏ qua viết tắt phổ biến
        before_text = text[max(0, pos - 10):pos + 1]  # bao gồm dấu chấm
        if _ABBREVIATIONS.search(before_text):
            continue
        char_after = match.group(1)
        errors.append({
            "word": "." + char_after,
            "suggestion": ". " + char_after,
            "reason": "Phải có đúng 1 khoảng trắng sau dấu chấm.",
            "type": "punctuation",
            "position": pos,
        })

    # 4. Nhiều khoảng trắng (2+) sau dấu câu trên cùng dòng
    for match in re.finditer(r'([,.])[^\S\n]{2,}(\S)', text):
        pos = match.start()
        if _is_in_url_or_special(text, pos):
            continue
        punct = match.group(1)
        char_after = match.group(2)
        errors.append({
            "word": match.group(),
            "suggestion": punct + " " + char_after,
            "reason": f"Chỉ nên có 1 khoảng trắng sau dấu '{punct}'.",
            "type": "punctuation",
            "position": pos,
        })

    return errors


def _check_capitalization(text: str) -> list[dict]:
    """
    Kiểm tra viết hoa:
    - Đầu văn bản phải viết hoa
    - Sau dấu chấm câu + dấu cách phải viết hoa
    - Sau xuống hàng phải viết hoa (đầu đoạn)
    """
    errors = []
    vn_lower = r'[a-zàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]'

    # 1. Đầu văn bản phải viết hoa
    first_match = re.match(rf'^(\s*)({vn_lower})', text)
    if first_match:
        lower_char = first_match.group(2)
        pos = first_match.start(2)
        # Lấy cả từ đầy đủ để Word search chính xác
        word_match = re.match(rf'{vn_lower}+', text[pos:])
        full_word = word_match.group() if word_match else lower_char
        errors.append({
            "word": full_word,
            "suggestion": full_word[0].upper() + full_word[1:],
            "reason": "Chữ cái đầu văn bản phải viết hoa.",
            "type": "capitalization",
            "position": pos,
        })

    # 2. Sau dấu chấm câu + dấu cách phải viết hoa
    for match in re.finditer(rf'[.!?]\s+({vn_lower})', text):
        lower_char = match.group(1)
        pos = match.start(1)
        word_match = re.match(rf'{vn_lower}+', text[pos:])
        full_word = word_match.group() if word_match else lower_char
        errors.append({
            "word": full_word,
            "suggestion": full_word[0].upper() + full_word[1:],
            "reason": "Chữ cái đầu câu phải viết hoa (sau dấu chấm câu).",
            "type": "capitalization",
            "position": pos,
        })

    # 3. Sau xuống hàng phải viết hoa (đầu đoạn)
    # Word trên Windows dùng \r cho paragraph break, macOS/Linux dùng \n
    for match in re.finditer(rf'[\r\n]+\s*({vn_lower})', text):
        lower_char = match.group(1)
        pos = match.start(1)
        word_match = re.match(rf'{vn_lower}+', text[pos:])
        full_word = word_match.group() if word_match else lower_char
        errors.append({
            "word": full_word,
            "suggestion": full_word[0].upper() + full_word[1:],
            "reason": "Chữ cái đầu đoạn phải viết hoa (sau xuống hàng).",
            "type": "capitalization",
            "position": pos,
        })

    return errors


def get_word_segments(text: str) -> list[str]:
    """
    Tách từ tiếng Việt (public API).
    Ví dụ: "Hà Nội rất đẹp" → ["Hà Nội", "rất", "đẹp"]
    """
    _load_nlp()
    if _word_tokenize is None:
        return text.split()
    try:
        return _word_tokenize(text)
    except Exception:
        return text.split()
