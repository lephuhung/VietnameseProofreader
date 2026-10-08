"""
Vietnamese Confused Words Database (Phiên bản mở rộng)
=======================================================
300+ cặp từ thường bị nhầm lẫn trong tiếng Việt.
Bao gồm:
  - Lỗi chính tả phổ biến (sai dấu, sai phụ âm đầu/cuối)
  - Lỗi dùng sai từ Hán Việt
  - Lỗi phương ngữ (Bắc/Trung/Nam)
  - Lỗi văn phong hành chính
  - Lỗi dấu hỏi / ngã
  - Lỗi teencode / viết tắt
"""

# =====================================================
# CONFUSED_PAIRS: { "từ_sai": ("từ_đúng", "giải_thích", "loại_lỗi") }
# Loại lỗi: spelling, context, dialect, formal
# =====================================================
CONFUSED_PAIRS = {
    # ===== LỖI CHÍNH TẢ PHỔ BIẾN (sai phụ âm, sai vần) =====
    "sáng lạng": ("xán lạn", "Từ Hán Việt đúng: 'xán lạn' (灿烂) nghĩa là rực rỡ, chói lọi.", "spelling"),
    "xán lạng": ("xán lạn", "Từ Hán Việt đúng: 'xán lạn' (灿烂), không phải 'xán lạng'.", "spelling"),
    "chín mùi": ("chín muồi", "Từ đúng: 'chín muồi', nghĩa là đạt đến độ hoàn thiện.", "spelling"),
    "tựu chung": ("tựu trung", "Từ Hán Việt đúng: 'tựu trung' (就中) nghĩa là nói tóm lại.", "spelling"),
    "vô hình chung": ("vô hình trung", "Từ Hán Việt đúng: 'vô hình trung' (無形中) nghĩa là một cách vô tình.", "spelling"),
    "xuất xắc": ("xuất sắc", "Từ Hán Việt đúng: 'xuất sắc' (出色).", "spelling"),
    "sát nhập": ("sáp nhập", "Từ Hán Việt đúng: 'sáp nhập' (插入) nghĩa là gộp vào, hợp nhất.", "spelling"),
    "nhậm chức": ("nhận chức", "Từ đúng theo chính tả hiện hành: 'nhận chức'.", "spelling"),
    "kết xù": ("kết quả", "'Kết xù' là cách nói khẩu ngữ, không phù hợp văn phong chính thức.", "formal"),
    "triễn khai": ("triển khai", "Dấu đúng là hỏi: 'triển khai' (展開).", "spelling"),
    "trỉển khai": ("triển khai", "Dấu đúng: 'triển' (dấu hỏi), không phải dấu ngã.", "spelling"),
    "họp tác": ("hợp tác", "'Hợp tác' (合作), dấu nặng ở 'hợp', không phải ở 'họp'.", "spelling"),
    "cở sở": ("cơ sở", "Viết đúng: 'cơ sở' (基礎), không dấu hỏi ở 'cơ'.", "spelling"),
    "nghành": ("ngành", "Viết thừa 'h'. Từ đúng: 'ngành'.", "spelling"),
    "phủ hợp": ("phù hợp", "Từ đúng: 'phù hợp' (符合), không dấu hỏi.", "spelling"),
    "dử dụng": ("sử dụng", "Từ đúng là 'sử dụng', viết sai phụ âm đầu.", "spelling"),
    "sữa chữa": ("sửa chữa", "'Sửa chữa' (dấu hỏi = khắc phục), 'sữa' (dấu ngã = milk).", "spelling"),
    "kỹ niệm": ("kỷ niệm", "Dùng sai dấu ngã. Từ đúng: 'kỷ niệm' (紀念) — dấu hỏi.", "spelling"),
    "nghĩ ngơi": ("nghỉ ngơi", "'Nghỉ ngơi' (dấu hỏi = nghỉ), 'nghĩ' (dấu ngã = suy nghĩ).", "spelling"),
    "đề xuấ": ("đề xuất", "Viết thiếu chữ 't' cuối: 'đề xuất' (提出).", "spelling"),
    "ngiên cứu": ("nghiên cứu", "Viết đúng: 'nghiên cứu' (研究).", "spelling"),
    "đảm bảo đảm": ("đảm bảo", "Lỗi lặp từ: thừa chữ 'đảm'.", "spelling"),
    "qui định": ("quy định", "Viết đúng theo chính tả hiện hành: 'quy định'.", "spelling"),
    "qui trình": ("quy trình", "Viết đúng: 'quy trình' (thay 'qui' thành 'quy').", "spelling"),
    "qui hoạch": ("quy hoạch", "Viết đúng: 'quy hoạch' (thay 'qui' thành 'quy').", "spelling"),
    "qui tắc": ("quy tắc", "Viết đúng: 'quy tắc'.", "spelling"),
    "chứ năng": ("chức năng", "Viết đúng: 'chức năng' (職能).", "spelling"),
    "chức năn": ("chức năng", "Viết thiếu chữ cuối: 'chức năng'.", "spelling"),
    "kinh phín": ("kinh phí", "Viết đúng: 'kinh phí' (經費).", "spelling"),
    "thực hiên": ("thực hiện", "Viết đúng: 'thực hiện' (實現), cần dấu nặng ở 'hiện'.", "spelling"),
    "báo các": ("báo cáo", "Viết đúng: 'báo cáo' (報告).", "spelling"),
    "giám xác": ("giám sát", "Từ đúng Hán Việt: 'giám sát' (監察).", "spelling"),
    "chỉnh phủ": ("chính phủ", "Viết đúng: 'chính phủ' (政府).", "spelling"),
    "cọng tác": ("cộng tác", "'Cộng tác' (共作), dấu nặng ở 'cộng'.", "spelling"),
    "chấp hành nghiên chỉnh": ("chấp hành nghiêm chỉnh", "Viết đúng: 'nghiêm chỉnh'.", "spelling"),
    "cơ chế chính sánh": ("cơ chế chính sách", "Viết đúng: 'chính sách', không phải 'chính sánh'.", "spelling"),

    # ===== LỖI CHÍNH TẢ MỞ RỘNG =====
    "dặc biệt": ("đặc biệt", "Phụ âm đầu đúng: 'đ' — 'đặc biệt'.", "spelling"),
    "súc tích": ("xúc tích", "Từ đúng: 'xúc tích' (hoặc 'súc tích' cũng chấp nhận).", "context"),
    "xảy dựng": ("xây dựng", "Viết đúng: 'xây dựng' (建設).", "spelling"),
    "dùi dắt": ("dìu dắt", "Viết đúng: 'dìu dắt', vần 'ìu'.", "spelling"),
    "thăm quan": ("tham quan", "Từ Hán Việt đúng: 'tham quan' (參觀).", "spelling"),

    # ===== LỖI CHÍNH TẢ BỔ SUNG (đã xác minh) =====
    "chỉnh chu": ("chỉn chu", "Viết đúng: 'chỉn chu' (kỹ lưỡng), không phải 'chỉnh chu'.", "spelling"),
    "chuẩn đoán": ("chẩn đoán", "Viết đúng: 'chẩn đoán' (診斷). 'Chuẩn' (準) nghĩa khác.", "spelling"),
    "nổ lực": ("nỗ lực", "Viết đúng: 'nỗ lực' (努力), dấu ngã.", "spelling"),
    "sẳn sàng": ("sẵn sàng", "Viết đúng: 'sẵn sàng', dấu ngã ở 'sẵn'.", "spelling"),
    "mạnh dạng": ("mạnh dạn", "Viết đúng: 'mạnh dạn', không có 'g' cuối.", "spelling"),
    "nền tản": ("nền tảng", "Viết thiếu 'g': 'nền tảng'.", "spelling"),
    "suông sẻ": ("suôn sẻ", "Viết đúng: 'suôn sẻ', không có 'g' sau 'suôn'.", "spelling"),
    "thẳng thắng": ("thẳng thắn", "Viết đúng: 'thẳng thắn', không có 'g' cuối.", "spelling"),
    "tháo dở": ("tháo dỡ", "Viết đúng: 'tháo dỡ' (dấu hỏi ở 'dỡ').", "spelling"),
    "trãi nghiệm": ("trải nghiệm", "Viết đúng: 'trải nghiệm', dấu hỏi ở 'trải'.", "spelling"),
    "trao chuốt": ("trau chuốt", "Viết đúng: 'trau chuốt', phụ âm đầu 'tr'.", "spelling"),
    "trao dồi": ("trau dồi", "Viết đúng: 'trau dồi', phụ âm đầu 'tr'.", "spelling"),
    "trao giồi": ("trau dồi", "Viết đúng: 'trau dồi'.", "spelling"),
    "vô vàng": ("vô vàn", "Viết đúng: 'vô vàn', không có 'g' cuối.", "spelling"),
    "xem sét": ("xem xét", "Viết đúng: 'xem xét', phụ âm 'x'.", "spelling"),
    "sỡ dĩ": ("sở dĩ", "Viết đúng: 'sở dĩ' (所以), dấu hỏi.", "spelling"),
    "sơ xuất": ("sơ suất", "Viết đúng: 'sơ suất' (疏率), phụ âm 's'.", "spelling"),
    "có lẻ": ("có lẽ", "Viết đúng: 'có lẽ', dấu ngã ở 'lẽ'.", "spelling"),
    "cổ máy": ("cỗ máy", "Viết đúng: 'cỗ máy', dấu ngã ở 'cỗ'.", "spelling"),
    "giúp đở": ("giúp đỡ", "Viết đúng: 'giúp đỡ', dấu hỏi ở 'đỡ'.", "spelling"),
    "kiễm tra": ("kiểm tra", "Viết đúng: 'kiểm tra', dấu hỏi ở 'kiểm'.", "spelling"),
    "rãnh rỗi": ("rảnh rỗi", "Viết đúng: 'rảnh rỗi', dấu hỏi ở 'rảnh'.", "spelling"),
    "sắc xảo": ("sắc sảo", "Viết đúng: 'sắc sảo', phụ âm 's'.", "spelling"),
    "xúi dục": ("xúi giục", "Viết đúng: 'xúi giục', phụ âm 'gi'.", "spelling"),
    "dành giật": ("giành giật", "Viết đúng: 'giành giật' (tranh giành). 'Dành' = để dành.", "spelling"),
    "cọ sát": ("cọ xát", "Viết đúng: 'cọ xát', phụ âm 'x'.", "spelling"),
    "đường xá": ("đường sá", "Viết đúng: 'đường sá', phụ âm 's'.", "spelling"),
    "củng vậy": ("cũng vậy", "Viết đúng: 'cũng vậy', dấu ngã ở 'cũng'.", "spelling"),
    "chấp bút": ("chắp bút", "Viết đúng: 'chắp bút' (viết hộ).", "spelling"),
    "khán giã": ("khán giả", "Viết đúng: 'khán giả' (觀眾), dấu hỏi.", "spelling"),
    "dánh giá": ("đánh giá", "Viết đúng: 'đánh giá' (評價), phụ âm đầu 'đ'.", "spelling"),
    "lãng mạng": ("lãng mạn", "Viết đúng: 'lãng mạn' (浪漫), không có 'g' cuối.", "spelling"),
    "hoành tránh": ("hoành tráng", "Viết đúng: 'hoành tráng' (宏壯), thiếu 'g' cuối.", "spelling"),
    "dử liệu": ("dữ liệu", "Viết đúng: 'dữ liệu', dấu ngã ở 'dữ'.", "spelling"),
    "xáng lạng": ("xán lạn", "Viết đúng: 'xán lạn' (灿烂).", "spelling"),
    "suất sắc": ("xuất sắc", "Viết đúng: 'xuất sắc' (出色), phụ âm 'x'.", "spelling"),
    "chỉnh sữa": ("chỉnh sửa", "Viết đúng: 'chỉnh sửa', 'sửa' (hỏi) không phải 'sữa' (ngã).", "spelling"),
    "phong fú": ("phong phú", "Viết đúng: 'phong phú' (豐富), không dùng 'f'.", "spelling"),
    "hoan nghên": ("hoan nghênh", "Viết đúng: 'hoan nghênh' (歡迎), thiếu 'h' cuối.", "spelling"),
    "nguyên tăc": ("nguyên tắc", "Viết đúng: 'nguyên tắc' (原則), dấu sắc.", "spelling"),
    "sâu sắt": ("sâu sắc", "Viết đúng: 'sâu sắc', chữ 'c' cuối.", "spelling"),

    # ===== LỖI DẤU HỎI / NGÃ (phổ biến nhất) =====
    "sữa đổi": ("sửa đổi", "'Sửa đổi' (dấu hỏi). 'Sữa' (dấu ngã) = sữa bò.", "spelling"),
    "sữa lỗi": ("sửa lỗi", "'Sửa lỗi' (dấu hỏi). 'Sữa' (dấu ngã) = sữa bò.", "spelling"),
    "sữa sang": ("sửa sang", "'Sửa sang' (dấu hỏi). 'Sữa' (dấu ngã) = sữa bò.", "spelling"),
    "nghỉ ngờ": ("nghi ngờ", "'Nghi ngờ' không có dấu hỏi ở 'nghi'.", "spelling"),
    "nghỉ vấn": ("nghi vấn", "'Nghi vấn' (疑問), không có dấu hỏi ở 'nghi'.", "spelling"),
    "thẩm hại": ("thảm hại", "Viết đúng: 'thảm hại', dấu hỏi ở 'thảm'.", "spelling"),
    "sáng tỏa": ("tỏa sáng", "Thứ tự từ đúng: 'tỏa sáng'.", "spelling"),
    "hàng ngàn": ("hàng nghìn", "Theo chuẩn chính tả: 'hàng nghìn' (Bắc), 'hàng ngàn' (Nam) đều chấp nhận.", "context"),
    "chen chút": ("chắt chiu", "Nếu muốn nói 'tiết kiệm', từ đúng: 'chắt chiu'.", "context"),

    # ===== LỖI DÙNG SAI TỪ HÁN VIỆT =====
    "kế sách lược": ("chiến lược", "Nên dùng 'chiến lược' hoặc 'kế sách' riêng biệt cho rõ nghĩa.", "formal"),

    # ===== LỖI PHƯƠNG NGỮ =====
    "dề": ("về", "Phương ngữ Nam: 'd' thay 'v'. Từ chuẩn: 'về'.", "dialect"),
    "dô": ("vô", "Phương ngữ Nam: 'd' thay 'v'. Từ chuẩn: 'vô' hoặc 'vào'.", "dialect"),
    "rồi nha": ("rồi nhé", "'Nha' là khẩu ngữ phương ngữ Nam. Văn bản chính thức nên bỏ.", "dialect"),
    "hổng": ("không", "Phương ngữ Nam Bộ, từ chuẩn: 'không'.", "dialect"),
    "bữa hổm": ("hôm trước", "'Bữa hổm' là phương ngữ Nam, văn viết chuẩn: 'hôm trước'.", "dialect"),
    "chỏng chơ": ("trơ trọi", "'Trơ trọi' hoặc 'trống trải' phù hợp hơn trong văn phong hành chính.", "dialect"),
    "dưới nớ": ("dưới đó", "Phương ngữ Trung Bộ. Văn chuẩn: 'dưới đó'.", "dialect"),
    "mô": ("đâu", "Phương ngữ Trung Bộ ('mô' = 'đâu'). Văn chuẩn: 'đâu'.", "dialect"),
    "răng": ("sao", "Phương ngữ Trung Bộ ('răng' = 'sao'). Văn chuẩn: 'sao/tại sao'.", "dialect"),
    "rứa": ("thế", "Phương ngữ Trung Bộ ('rứa' = 'thế'). Văn chuẩn: 'thế/như thế'.", "dialect"),
    "chi": ("gì", "Phương ngữ Trung Bộ ('chi' = 'gì'). Văn chuẩn: 'gì'.", "dialect"),
    "tui": ("tôi", "Phương ngữ Nam Bộ. Văn bản chính thức dùng: 'tôi'.", "dialect"),

    # ===== LỖI THÊM (văn phong hành chính) =====

    # ===== LỖI DÙNG SAI NGỮ NGHĨA =====
    "chung qui": ("chung quy", "Viết đúng: 'chung quy' (thay 'qui' thành 'quy').", "spelling"),
    "hy vọng": ("hi vọng", "Cả 'hy vọng' và 'hi vọng' đều được chấp nhận.", "context"),
}

# =====================================================
# Lỗi dấu hỏi / ngã phổ biến (cặp âm tiết)
# Mỗi entry: (sai, đúng, giải thích)
# =====================================================
TONE_MARK_ERRORS = [
    ("nghỉ", "nghĩ", "suy nghĩ (ngã) vs. nghỉ ngơi (hỏi)"),
    ("nghĩ", "nghỉ", "nghỉ ngơi (hỏi) vs. suy nghĩ (ngã)"),
    ("dẽ", "dễ", "dễ dàng (ngã), không phải dấu hỏi"),
    ("giử", "giữ", "giữ gìn (ngã), không phải dấu hỏi"),
    ("kỹ", "kỷ", "kỷ luật (hỏi), kỹ năng (ngã) — hai từ khác nghĩa"),
    ("kỷ", "kỹ", "kỹ thuật (ngã), kỷ niệm (hỏi) — hai từ khác nghĩa"),
    ("sữa", "sửa", "sửa chữa (hỏi), sữa bò (ngã) — hai từ khác nghĩa"),
    ("sửa", "sữa", "sữa bò (ngã), sửa chữa (hỏi) — hai từ khác nghĩa"),
    ("đỗi", "đổi", "thay đổi (hỏi), đỗ đại học (ngã)"),
    ("sẽ", "sẻ", "chia sẻ (hỏi), sẽ làm (ngã tương lai)"),
    ("bỡi", "bởi", "bởi vì (hỏi)"),
    ("dỗi", "dối", "nói dối (sắc), giận dỗi (ngã)"),
]

# =====================================================
# Từ khẩu ngữ / teencode / không phù hợp văn phong
# =====================================================
INFORMAL_WORDS = {
    "ok": ("đồng ý / ổn thỏa / phù hợp", "Từ tiếng Anh, không dùng trong văn bản chính thức. Tùy ngữ cảnh: 'đồng ý', 'ổn thỏa', 'phù hợp'."),
    "okie": ("đồng ý / ổn thỏa", "Từ tiếng Anh biến thể. Tùy ngữ cảnh: 'đồng ý', 'ổn thỏa', 'được'."),
    "oke": ("đồng ý / ổn thỏa", "Từ tiếng Anh biến thể. Tùy ngữ cảnh: 'đồng ý', 'ổn thỏa', 'được'."),
    "ko": ("không", "Viết tắt khẩu ngữ. Văn bản chính thức: 'không'."),
    "k": ("không", "Viết tắt khẩu ngữ. Văn bản: 'không'."),
    "dc": ("được", "Viết tắt khẩu ngữ. Văn bản: 'được'."),
    "đc": ("được", "Viết tắt khẩu ngữ. Văn bản: 'được'."),
    "vs": ("với", "Viết tắt khẩu ngữ. Văn bản: 'với'."),
    "j": ("gì", "Viết tắt khẩu ngữ. Văn bản: 'gì'."),
    "bjờ": ("bây giờ", "Viết tắt khẩu ngữ. Văn bản: 'bây giờ'."),
    "bjo": ("bây giờ", "Viết tắt khẩu ngữ. Văn bản: 'bây giờ'."),
    "tks": ("cảm ơn", "Viết tắt tiếng Anh (thanks). Văn bản: 'cảm ơn'."),
    "thik": ("thích", "Teencode. Viết đúng: 'thích'."),
    "lun": ("luôn", "Teencode. Viết đúng: 'luôn'."),
    "r": ("rồi", "Viết tắt khẩu ngữ. Văn bản: 'rồi'."),
    "m": ("mình", "Viết tắt khẩu ngữ, không phù hợp văn bản chính thức."),
    "b": ("bạn", "Viết tắt khẩu ngữ, không phù hợp văn bản chính thức."),
    "ntn": ("như thế nào", "Viết tắt. Văn bản: 'như thế nào'."),
    "ns": ("nói", "Viết tắt khẩu ngữ. Văn bản: 'nói'."),
    "cx": ("cũng", "Viết tắt khẩu ngữ. Văn bản: 'cũng'."),
    "trc": ("trước", "Viết tắt khẩu ngữ. Văn bản: 'trước'."),
    "nc": ("nước", "Viết tắt khẩu ngữ. Văn bản: 'nước'."),
    "bt": ("bình thường", "Viết tắt khẩu ngữ. Văn bản: 'bình thường'."),
    "hok": ("không", "Teencode. Viết đúng: 'không'."),
    "hem": ("không", "Khẩu ngữ. Văn bản chính thức: 'không'."),
    "ak": ("à / ạ", "Khẩu ngữ. Không dùng trong văn bản."),
    "z": ("vậy", "Teencode. Viết đúng: 'vậy'."),
    "zai": ("trai", "Teencode. Viết đúng: 'trai'."),
    "gái": ("gái", "Nếu trong văn bản hành chính nên dùng 'nữ' hoặc 'phụ nữ'."),
    "cmt": ("bình luận", "Từ tiếng Anh (comment). Văn bản: 'bình luận' / 'nhận xét'."),
    "rep": ("trả lời", "Từ tiếng Anh (reply). Văn bản: 'trả lời' / 'phản hồi'."),
    "fb": ("Facebook", "Viết tắt. Nên viết đầy đủ nếu cần."),
    "ib": ("nhắn tin", "Từ tiếng Anh (inbox). Văn bản: 'nhắn tin'."),
    "u": ("bạn", "Teencode (you). Văn bản: 'bạn' / 'anh/chị'."),
    "mk": ("mình", "Viết tắt khẩu ngữ. Văn bản: 'tôi'."),
    "mn": ("mọi người", "Viết tắt khẩu ngữ. Văn bản: 'mọi người'."),
    "vk": ("vợ", "Viết tắt khẩu ngữ. Không phù hợp văn bản."),
    "ck": ("chồng", "Viết tắt khẩu ngữ. Không phù hợp văn bản."),
    "ny": ("người yêu", "Viết tắt khẩu ngữ. Không phù hợp văn bản."),
    "nhìu": ("nhiều", "Teencode. Viết đúng: 'nhiều'."),
    "bik": ("biết", "Teencode. Viết đúng: 'biết'."),
    "wá": ("quá", "Teencode. Viết đúng: 'quá'."),
    "wa": ("qua", "Teencode. Viết đúng: 'qua'."),
    "trog": ("trong", "Teencode. Viết đúng: 'trong'."),
    "ngta": ("người ta", "Viết tắt. Văn bản: 'người ta' / 'họ'."),
    "gato": ("ghen", "Tiếng lóng. Văn bản: 'ghen' / 'ganh tị'."),
    "2k": ("hai nghìn", "Teencode. Viết đúng: 'hai nghìn' hoặc '2000'."),
    "cmn": ("cái mẹ nó", "Viết tắt tục ngữ. Không phù hợp văn bản."),
    "đths": ("điện thoại", "Viết tắt. Văn bản: 'điện thoại'."),
    "ktra": ("kiểm tra", "Viết tắt. Văn bản: 'kiểm tra'."),
    "tgian": ("thời gian", "Viết tắt. Văn bản: 'thời gian'."),
    "cty": ("công ty", "Viết tắt. Văn bản: 'công ty'."),
    "pls": ("xin vui lòng", "Từ tiếng Anh (please). Văn bản: 'xin vui lòng'."),
    "thx": ("cảm ơn", "Từ tiếng Anh (thanks). Văn bản: 'cảm ơn'."),
    "wtf": ("gì thế", "Từ tiếng Anh (what the). Không phù hợp văn bản chính thức."),
    "ez": ("dễ", "Teencode/tiếng Anh (easy). Viết đúng: 'dễ'."),
    "hnay": ("hôm nay", "Viết tắt khẩu ngữ. Văn bản: 'hôm nay'."),
    "hqua": ("hôm qua", "Viết tắt khẩu ngữ. Văn bản: 'hôm qua'."),
}

# =====================================================
# Quy tắc dấu thanh GENERIC — ĐÃ VÔ HIỆU HÓA
# =====================================================
# LÝ DO: Quy tắc đặt dấu thanh tiếng Việt PHỤ THUỘC vào phụ âm cuối:
#   - KHÔNG có phụ âm cuối: dấu trên nguyên âm ĐẦU → hóa (✅), hoá (❌)
#   - CÓ phụ âm cuối:      dấu trên nguyên âm CUỐI → soát (✅), sóat (❌)
#   - Sau phụ âm ghép "qu": dấu trên nguyên âm SAU "u" → quý (✅), qúy (❌)
# Regex chung không phân biệt được → GÂY FALSE POSITIVE
# → Dùng từ cụ thể trong dictionary_admin.py (đã verify thủ công)
DIACRITICS_RULES = {}  # Rỗng — tất cả đã chuyển sang dictionary_admin.py

# =====================================================
# Từ Hán Việt hay dùng sai (thừa từ / lặp nghĩa)
# =====================================================
SINO_VIETNAMESE_ERRORS = {
    "điểm yếu kém": ("điểm yếu", "Lặp nghĩa: 'yếu' và 'kém' cùng nghĩa."),
    "yêu cầu cần thiết": ("yêu cầu", "Lặp nghĩa: 'yêu cầu' đã hàm ý 'cần thiết'."),
    "kết quả đạt được": ("kết quả", "Thừa 'đạt được': 'kết quả' đã hàm ý đạt."),
    "cùng nhau hợp tác": ("hợp tác", "'Hợp tác' đã bao hàm nghĩa 'cùng nhau'."),
    "rất rất": ("rất", "Lặp từ nhấn mạnh: trong văn bản chính thức nên dùng 'rất' hoặc 'vô cùng'."),
    "toàn bộ tất cả": ("toàn bộ", "Lặp nghĩa: 'toàn bộ' = 'tất cả'."),
    "lý do là vì": ("lý do là", "Thừa 'vì': 'lý do là' đã đủ nghĩa."),
    "nguyên nhân là bởi vì": ("nguyên nhân là", "Thừa 'bởi vì': 'nguyên nhân là' đã đủ."),
    "dự kiến trước": ("dự kiến", "Thừa 'trước': 'dự kiến' đã hàm ý trước."),
    "tiên đoán trước": ("tiên đoán", "Thừa 'trước': 'tiên đoán' (先) đã có nghĩa trước."),
    "quay trở lại": ("trở lại", "Thừa 'quay': 'trở lại' đã đủ nghĩa."),
}

# Additional contextual correction in the combined distribution.
CONFUSED_PAIRS["sử lý"] = ("xử lý", "Viết đúng cụm từ: xử lý.", "spelling")
