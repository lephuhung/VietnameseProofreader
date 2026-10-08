"""
Từ điển mở rộng — Văn phong Hành chính
=========================================
Chỉ chứa các cặp sai/đúng **chắc chắn 100%** trong ngữ cảnh
văn bản hành chính, công vụ, doanh nghiệp.

NGUYÊN TẮC BIÊN SOẠN:
  1. Chỉ thêm từ KHÔNG BAO GIỜ đúng trong văn phong hành chính
  2. Không thêm từ đa nghĩa (VD: nghỉ/nghĩ — cả hai đều đúng tùy ngữ cảnh)
  3. Ưu tiên lỗi phổ biến, hay gặp trong thực tế
  4. Mỗi entry phải có giải thích rõ ràng
"""

# =====================================================
# NHÓM 1: Thuật ngữ Hán Việt hay viết sai trong văn bản hành chính
# (Đây là những từ LUÔN sai, không phụ thuộc ngữ cảnh)
# =====================================================
ADMIN_CONFUSED_PAIRS = {
    # --- 1.1 Sai phụ âm đầu/cuối ---
    "bổ xung":       ("bổ sung", "Viết đúng: 'bổ sung' (補充), phụ âm 's' không phải 'x'.", "spelling"),
    "sáp nhậm":      ("sáp nhập", "Viết đúng: 'sáp nhập' (插入), không phải 'sáp nhậm'.", "spelling"),
    "thăm tra":      ("thẩm tra", "Viết đúng: 'thẩm tra' (審查), dấu hỏi ở 'thẩm'.", "spelling"),
    "đề bạc":        ("đề bạt", "Viết đúng: 'đề bạt' (提拔), chữ 't' cuối.", "spelling"),
    "biện pháb":     ("biện pháp", "Viết đúng: 'biện pháp' (辦法), chữ 'p' cuối.", "spelling"),
    "kiểm sát":      ("kiểm soát", "Viết đúng: 'kiểm soát' (檢查), vần 'oát'. Lưu ý: 'kiểm sát' (檢察) là Viện kiểm sát — nghĩa khác.", "context"),
    "giám xát":      ("giám sát", "Viết đúng: 'giám sát' (監察), phụ âm 's'.", "spelling"),
    "chấp hàn":      ("chấp hành", "Viết đúng: 'chấp hành' (執行), thiếu chữ 'h'.", "spelling"),
    "phân bổ":       ("phân bổ", "Viết đúng: 'phân bổ' (分補). Hay bị viết sai thành 'phân bỗ'.", "spelling"),
    "tiêu chuẩng":   ("tiêu chuẩn", "Viết thừa 'g': 'tiêu chuẩn' (標準).", "spelling"),
    "phương hướn":   ("phương hướng", "Viết thiếu 'g': 'phương hướng' (方向).", "spelling"),
    "nguyên nhâm":   ("nguyên nhân", "Viết sai vần: 'nguyên nhân' (原因).", "spelling"),
    "thườg xuyên":   ("thường xuyên", "Viết thiếu 'n': 'thường xuyên'.", "spelling"),
    "liên quang":    ("liên quan", "Viết thừa 'g': 'liên quan' (聯關).", "spelling"),
    "kinh nghiện":   ("kinh nghiệm", "Viết sai vần: 'kinh nghiệm' (經驗).", "spelling"),
    "trách nhiện":   ("trách nhiệm", "Viết sai vần: 'trách nhiệm' (責任).", "spelling"),
    "khoảng khắc":   ("khoảnh khắc", "Viết đúng: 'khoảnh khắc', có chữ 'nh'.", "spelling"),
    "trương trình":  ("chương trình", "Viết đúng phụ âm: 'chương trình' (程式).", "spelling"),
    "chuyên nghành": ("chuyên ngành", "Viết thừa 'h': 'chuyên ngành'.", "spelling"),
    "khuyến cáu":    ("khuyến cáo", "Viết đúng vần: 'khuyến cáo' (勸告).", "spelling"),
    "chẩn đoáng":    ("chẩn đoán", "Viết thừa 'g': 'chẩn đoán' (診斷).", "spelling"),
    "nghị quết":     ("nghị quyết", "Viết đúng: 'nghị quyết' (議決).", "spelling"),
    "nghị quyếch":   ("nghị quyết", "Viết đúng vần: 'nghị quyết' (議決).", "spelling"),
    "luận cừ":       ("luận cứ", "Viết đúng: 'luận cứ' (論據).", "spelling"),
    "sản xuấ":       ("sản xuất", "Viết thiếu 't': 'sản xuất' (產出).", "spelling"),
    "đặc biệp":     ("đặc biệt", "Viết đúng chữ cuối: 'đặc biệt' (特別).", "spelling"),
    "vô cùn":        ("vô cùng", "Viết thiếu 'g': 'vô cùng'.", "spelling"),
    "tìn hình":      ("tình hình", "Viết đúng: 'tình hình' (情形).", "spelling"),
    "lĩnh vức":      ("lĩnh vực", "Viết đúng: 'lĩnh vực' (領域).", "spelling"),
    "nhân lức":      ("nhân lực", "Viết đúng: 'nhân lực' (人力).", "spelling"),
    "suất xắc":      ("xuất sắc", "Viết đúng: 'xuất sắc' (出色).", "spelling"),
    "giám đống":     ("giám đốc", "Viết đúng: 'giám đốc' (監督).", "spelling"),
    "khắc phúc":     ("khắc phục", "Viết đúng: 'khắc phục' (克服).", "spelling"),
    "tổ trức":       ("tổ chức", "Viết đúng: 'tổ chức' (組織).", "spelling"),
    "giải quết":     ("giải quyết", "Viết đúng: 'giải quyết' (解決).", "spelling"),
    "cuối củng":     ("cuối cùng", "Viết đúng vần: 'cuối cùng'.", "spelling"),
    "kết lựa":       ("kết luận", "Viết đúng: 'kết luận' (結論).", "spelling"),
    "trắc nhiệm":   ("trắc nghiệm", "Viết đúng: 'trắc nghiệm' (測驗), thiếu 'ng'.", "spelling"),
    "chức nắng":     ("chức năng", "Viết đúng dấu: 'chức năng' (職能).", "spelling"),
    "trang binh":    ("trang bị", "Viết đúng: 'trang bị' (裝備).", "spelling"),
    "phổ biếng":     ("phổ biến", "Viết thừa 'g': 'phổ biến' (普遍).", "spelling"),
    "hàng hỏa":      ("hàng hóa", "Viết đúng dấu sắc: 'hàng hóa' (sắc ở 'hóa').", "spelling"),

    # --- 1.2 Sai dấu thanh (hỏi/ngã) — chỉ những trường hợp LUÔN sai ---
    "phát triễn":    ("phát triển", "Dấu đúng: 'triển' (hỏi), không phải ngã.", "spelling"),
    "ảnh hưỡng":     ("ảnh hưởng", "Viết đúng dấu hỏi: 'ảnh hưởng' (影響).", "spelling"),
    "giãi quyết":    ("giải quyết", "Dấu đúng: 'giải' (hỏi), không phải ngã.", "spelling"),
    "giãm sát":      ("giám sát", "Viết đúng dấu sắc: 'giám sát' (監察).", "spelling"),
    "tích lủy":      ("tích lũy", "Dấu đúng: 'lũy' (ngã), không phải hỏi.", "spelling"),
    "thảm mỹ":       ("thẩm mỹ", "Viết đúng: 'thẩm mỹ' (審美), dấu hỏi ở 'thẩm'.", "spelling"),
    "dỗi dào":       ("dồi dào", "Viết đúng: 'dồi dào', không có dấu ngã.", "spelling"),
    "sửa sai":       ("sửa sai", "Viết đúng dấu hỏi: 'sửa sai'. Phân biệt: sửa (hỏi) ≠ sữa (ngã, là sữa bò).", "spelling"),
    "sẽ chia":       ("sẻ chia", "Viết đúng: 'sẻ chia' (dấu hỏi). 'Sẽ' (ngã) = tương lai.", "spelling"),
    "san sẽ":        ("san sẻ", "Viết đúng: 'san sẻ' (dấu hỏi), không phải ngã.", "spelling"),
    "chia xẻ":       ("chia sẻ", "Viết đúng phụ âm: 'chia sẻ', phụ âm 's'.", "spelling"),
    "chỉnh sách":    ("chính sách", "Viết đúng: 'chính sách' (政策), dùng 'í' không phải 'ỉ'.", "spelling"),
    "dử lý":         ("xử lý", "Viết đúng: 'xử lý' (處理), phụ âm 'x'.", "spelling"),
    "sảy ra":        ("xảy ra", "Viết đúng phụ âm: 'xảy ra', phụ âm 'x'.", "spelling"),
    "xẩy ra":        ("xảy ra", "Viết đúng dấu hỏi: 'xảy ra'.", "spelling"),
    "sai xót":       ("sai sót", "Viết đúng phụ âm: 'sai sót', phụ âm 's'.", "spelling"),
    "trờ nên":       ("trở nên", "Viết đúng dấu hỏi: 'trở nên'.", "spelling"),
    "tậm trung":     ("tập trung", "Viết đúng: 'tập trung' (集中).", "spelling"),
    "nổi dung":      ("nội dung", "Viết đúng: 'nội dung' (內容).", "spelling"),

    # --- 1.3 Qui → Quy (theo chính tả hiện hành, luôn sai) ---
    "qui phạm":      ("quy phạm", "Viết đúng: 'quy phạm' (qui → quy).", "spelling"),
    "qui chế":       ("quy chế", "Viết đúng: 'quy chế' (qui → quy).", "spelling"),
    "qui mô":        ("quy mô", "Viết đúng: 'quy mô' (qui → quy).", "spelling"),
    "qui cách":      ("quy cách", "Viết đúng: 'quy cách' (qui → quy).", "spelling"),
    "qui luật":      ("quy luật", "Viết đúng: 'quy luật' (qui → quy).", "spelling"),
    "qui ước":       ("quy ước", "Viết đúng: 'quy ước' (qui → quy).", "spelling"),
    "qui nạp":       ("quy nạp", "Viết đúng: 'quy nạp' (qui → quy).", "spelling"),

    # --- 1.4 Kĩ → Kỹ (theo chính tả hiện hành, luôn sai) ---
    "kĩ năng":       ("kỹ năng", "Viết đúng: 'kỹ năng' (kĩ → kỹ).", "spelling"),
    "kĩ thuật":      ("kỹ thuật", "Viết đúng: 'kỹ thuật' (kĩ → kỹ).", "spelling"),
    "kĩ sư":         ("kỹ sư", "Viết đúng: 'kỹ sư' (kĩ → kỹ).", "spelling"),
    "kĩ lưỡng":      ("kỹ lưỡng", "Viết đúng: 'kỹ lưỡng' (kĩ → kỹ).", "spelling"),

    # --- 1.5 Nghành → Ngành (thừa 'h', luôn sai) ---
    "nghành nghề":   ("ngành nghề", "Viết thừa 'h': 'ngành nghề'.", "spelling"),
    "nghành học":     ("ngành học", "Viết thừa 'h': 'ngành học'.", "spelling"),
    "nghành dọc":     ("ngành dọc", "Viết thừa 'h': 'ngành dọc'.", "spelling"),
    "nghành ngang":   ("ngành ngang", "Viết thừa 'h': 'ngành ngang'.", "spelling"),

    # --- 1.6 Quí → Quý (theo chính tả hiện hành, luôn dùng 'y') ---
    "quí":            ("quý", "Viết đúng: 'quý' (quí → quý).", "spelling"),
    "quí I":          ("quý I", "Viết đúng: 'quý I' (quí → quý).", "spelling"),
    "quí II":         ("quý II", "Viết đúng: 'quý II' (quí → quý).", "spelling"),
    "quí III":        ("quý III", "Viết đúng: 'quý III' (quí → quý).", "spelling"),
    "quí IV":         ("quý IV", "Viết đúng: 'quý IV' (quí → quý).", "spelling"),
    "quí 1":          ("quý 1", "Viết đúng: 'quý 1' (quí → quý).", "spelling"),
    "quí 2":          ("quý 2", "Viết đúng: 'quý 2' (quí → quý).", "spelling"),
    "quí 3":          ("quý 3", "Viết đúng: 'quý 3' (quí → quý).", "spelling"),
    "quí 4":          ("quý 4", "Viết đúng: 'quý 4' (quí → quý).", "spelling"),
    "quí vị":         ("quý vị", "Viết đúng: 'quý vị' (quí → quý).", "spelling"),
    "quí khách":      ("quý khách", "Viết đúng: 'quý khách' (quí → quý).", "spelling"),
    "quí cơ quan":    ("quý cơ quan", "Viết đúng: 'quý cơ quan' (quí → quý).", "spelling"),
    "quí đơn vị":     ("quý đơn vị", "Viết đúng: 'quý đơn vị' (quí → quý).", "spelling"),
    "quí báu":        ("quý báu", "Viết đúng: 'quý báu' (quí → quý).", "spelling"),
    "quí giá":        ("quý giá", "Viết đúng: 'quý giá' (quí → quý).", "spelling"),
    "quí trọng":      ("quý trọng", "Viết đúng: 'quý trọng' (quí → quý).", "spelling"),
    "quí hiếm":       ("quý hiếm", "Viết đúng: 'quý hiếm' (quí → quý).", "spelling"),
    "quí tộc":        ("quý tộc", "Viết đúng: 'quý tộc' (quí → quý).", "spelling"),

    # --- 1.7 Sai vị trí dấu thanh (từ cụ thể, an toàn) ---
    # Quy tắc: dấu thanh đặt trên nguyên âm CHÍNH của vần
    # "oa" → dấu trên 'o': hóa (ko phải hoá)
    # "oe" → dấu trên 'o': hòe (ko phải hoè)
    # "uy" → dấu trên 'u': thúy (ko phải thuý)
    # NGOẠI LỆ: sau "qu" thì dấu trên nguyên âm sau "u" (quý, quả — đã đúng)

    # --- oá → óa ---
    "hoá học":        ("hóa học", "Vị trí dấu đúng: 'hóa' (dấu trên 'o', nguyên âm chính).", "diacritics"),
    "hoá chất":       ("hóa chất", "Vị trí dấu đúng: 'hóa chất'.", "diacritics"),
    "hoá đơn":        ("hóa đơn", "Vị trí dấu đúng: 'hóa đơn'.", "diacritics"),
    "biến hoá":       ("biến hóa", "Vị trí dấu đúng: 'biến hóa'.", "diacritics"),
    "văn hoá":        ("văn hóa", "Vị trí dấu đúng: 'văn hóa'.", "diacritics"),
    "giáo hoá":       ("giáo hóa", "Vị trí dấu đúng: 'giáo hóa'.", "diacritics"),
    "khoá học":       ("khóa học", "Vị trí dấu đúng: 'khóa học'.", "diacritics"),
    "khoá luận":      ("khóa luận", "Vị trí dấu đúng: 'khóa luận'.", "diacritics"),
    "toà nhà":        ("tòa nhà", "Vị trí dấu đúng: 'tòa nhà'.", "diacritics"),
    "toà án":         ("tòa án", "Vị trí dấu đúng: 'tòa án'.", "diacritics"),
    "toà soạn":       ("tòa soạn", "Vị trí dấu đúng: 'tòa soạn'.", "diacritics"),
    "loà xoà":        ("lòa xòa", "Vị trí dấu đúng: 'lòa xòa'.", "diacritics"),
    "chói loá":       ("chói lóa", "Vị trí dấu đúng: 'chói lóa'.", "diacritics"),
    "xoá bỏ":         ("xóa bỏ", "Vị trí dấu đúng: 'xóa bỏ'.", "diacritics"),
    "đoá hoa":        ("đóa hoa", "Vị trí dấu đúng: 'đóa hoa'.", "diacritics"),
    "doá nạt":        ("dóa nạt", "Vị trí dấu đúng: 'dóa nạt'.", "diacritics"),

    # --- hoà → hòa ---
    "hoà bình":       ("hòa bình", "Vị trí dấu đúng: 'hòa bình'.", "diacritics"),
    "hoà giải":       ("hòa giải", "Vị trí dấu đúng: 'hòa giải'.", "diacritics"),
    "hoà hợp":        ("hòa hợp", "Vị trí dấu đúng: 'hòa hợp'.", "diacritics"),
    "hoà nhập":       ("hòa nhập", "Vị trí dấu đúng: 'hòa nhập'.", "diacritics"),
    "hoà thuận":      ("hòa thuận", "Vị trí dấu đúng: 'hòa thuận'.", "diacritics"),

    # --- uỷ → ủy, uý → úy ---
    "uỷ ban":         ("ủy ban", "Vị trí dấu đúng: 'ủy ban' (dấu trên 'u', nguyên âm chính).", "diacritics"),
    "uỷ quyền":       ("ủy quyền", "Vị trí dấu đúng: 'ủy quyền'.", "diacritics"),
    "uỷ viên":        ("ủy viên", "Vị trí dấu đúng: 'ủy viên'.", "diacritics"),
    "uỷ thác":        ("ủy thác", "Vị trí dấu đúng: 'ủy thác'.", "diacritics"),
    "uỷ nhiệm":       ("ủy nhiệm", "Vị trí dấu đúng: 'ủy nhiệm'.", "diacritics"),
    "huỷ bỏ":         ("hủy bỏ", "Vị trí dấu đúng: 'hủy bỏ'.", "diacritics"),
    "huỷ hoại":       ("hủy hoại", "Vị trí dấu đúng: 'hủy hoại'.", "diacritics"),
    "huỷ diệt":       ("hủy diệt", "Vị trí dấu đúng: 'hủy diệt'.", "diacritics"),
    "tuỷ":            ("tủy", "Vị trí dấu đúng: 'tủy' (tủy sống).", "diacritics"),
    "thuý":           ("thúy", "Vị trí dấu đúng: 'thúy'.", "diacritics"),
    "suý":            ("súy", "Vị trí dấu đúng: 'súy' (nguyên súy).", "diacritics"),
    "tuý":            ("túy", "Vị trí dấu đúng: 'túy' (say túy lúy).", "diacritics"),
    "phá huỷ":        ("phá hủy", "Vị trí dấu đúng: 'phá hủy'.", "diacritics"),
    "tiêu huỷ":       ("tiêu hủy", "Vị trí dấu đúng: 'tiêu hủy'.", "diacritics"),

    # --- oè → òe ---
    "khoẻ mạnh":      ("khỏe mạnh", "Vị trí dấu đúng: 'khỏe mạnh'.", "diacritics"),
}

# =====================================================
# NHÓM 2: Cụm từ thừa / lặp nghĩa — phổ biến trong văn hành chính
# (Những cặp này LUÔN cần rút gọn trong văn phong chuẩn)
# =====================================================
ADMIN_REDUNDANCY = {
    # --- Thừa từ (đã bao hàm nghĩa) ---
    "được mùa bội thu":     ("được mùa", "'Được mùa' đã bao hàm 'bội thu'."),
    "cùng nhau hợp tác":    ("hợp tác", "'Hợp tác' đã bao hàm nghĩa 'cùng nhau'."),
    "cùng phối hợp":        ("phối hợp", "'Phối hợp' đã bao hàm nghĩa 'cùng'."),
    "tiên phong đi đầu":    ("tiên phong", "'Tiên phong' đã có nghĩa 'đi đầu'."),
    "đầu tiên trước hết":   ("trước hết", "Lặp nghĩa: 'đầu tiên' = 'trước hết'."),
    "hoàn toàn tuyệt đối":  ("tuyệt đối", "Lặp nghĩa: 'hoàn toàn' = 'tuyệt đối'."),
    "đã từng":              ("từng", "Thừa 'đã': 'từng' đã hàm ý quá khứ."),
    "đang còn":             ("còn", "Thừa 'đang': trùng nghĩa thì hiện tại."),
    "suốt cả ngày":         ("suốt ngày", "Thừa 'cả': 'suốt ngày' đã rõ nghĩa."),
    "mỗi một":              ("mỗi", "'Mỗi' đã có nghĩa 'một'."),
    "vẫn còn tiếp tục":     ("vẫn tiếp tục", "Thừa 'còn': lặp nghĩa."),
    "ngày càng ngày càng":  ("ngày càng", "Lặp cụm từ: chỉ cần 'ngày càng'."),
    "chế tạo ra":           ("chế tạo", "Thừa 'ra': 'chế tạo' đã bao hàm."),
    "sáng tạo ra":          ("sáng tạo", "Thừa 'ra': 'sáng tạo' đã bao hàm."),
    "bị mắc phải":          ("mắc phải", "Thừa 'bị': 'mắc phải' đã bao hàm."),
    "rất tuyệt vời":        ("tuyệt vời", "'Tuyệt vời' đã là mức cao nhất."),
    "có thể có khả năng":   ("có thể", "Lặp nghĩa: 'có thể' = 'có khả năng'."),
    "đầy đủ hết":           ("đầy đủ", "Thừa 'hết': 'đầy đủ' đã bao hàm."),
    "hậu quả xấu":          ("hậu quả", "'Hậu quả' đã mang nghĩa tiêu cực."),
    "bị thiệt hại":         ("thiệt hại", "Thừa 'bị': 'thiệt hại' đã bao hàm."),

    # --- Lặp nghĩa phổ biến trong văn bản hành chính ---
    "triển khai thực hiện":     ("triển khai", "'Triển khai' đã bao hàm nghĩa 'thực hiện'. Nên chọn 1 trong 2."),
    "nghiên cứu xem xét":      ("xem xét", "Lặp nghĩa: nên dùng 'nghiên cứu' hoặc 'xem xét'."),
    "tổng hợp chung":          ("tổng hợp", "Thừa 'chung': 'tổng hợp' đã bao hàm."),
    "đạt được thành quả tốt":  ("đạt thành quả", "Thừa 'được' và 'tốt': 'thành quả' hàm ý tích cực."),
    "các đồng chí cán bộ":     ("cán bộ", "Thừa 'các đồng chí': nên dùng 'cán bộ' cho gọn."),
    "nhằm mục đích để":        ("nhằm", "Thừa từ: 'nhằm' đã bao hàm 'mục đích'."),
    "nguyên nhân là do":       ("nguyên nhân là", "Thừa 'do': 'nguyên nhân là' đã đủ."),
    "khoảng chừng":            ("khoảng", "Lặp nghĩa: 'khoảng' = 'chừng'."),
    "nâng cao chất lượng hơn": ("nâng cao chất lượng", "Thừa 'hơn': 'nâng cao' đã hàm ý so sánh."),
}

# =====================================================
# NHÓM 3: Thuật ngữ hành chính hay dùng sai
# (Đúng từ Hán Việt nhưng sai ngữ nghĩa)
# =====================================================
ADMIN_CONTEXT_ERRORS = {
    "yếu điểm": ("điểm yếu", "Lỗi nghĩa: 'yếu điểm' (要點) = điểm quan trọng. 'Điểm yếu' mới đúng nghĩa khuyết điểm.", "context"),
    "bàng quang": ("bàng quan", "'Bàng quang' (膀胱) = bọng đái. Đúng: 'bàng quan' (旁觀) = đứng ngoài nhìn.", "context"),
    "tham quan": ("tham quan", "'Tham quan' (參觀) đúng gốc Hán Việt, dùng trong văn bản chính thức.", "context"),
    "khuyết tật": ("khuyết tật", "Viết đúng: 'khuyết tật' (缺疾). Thường bị viết sai thành 'khuyến tật'.", "context"),
    "chứng thực": ("chứng thực", "Viết đúng: 'chứng thực' (證實). Phân biệt: 'chứng thực' ≠ 'công chứng'.", "context"),
}

# =====================================================
# NHÓM 4: Phương ngữ KHÔNG phù hợp văn phong hành chính
# (Chỉ thêm từ chắc chắn không bao giờ dùng trong văn bản chính thức)
# =====================================================
ADMIN_DIALECT = {
    "hổng có":    ("không có", "Phương ngữ Nam. Văn bản hành chính: 'không có'.", "dialect"),
    "hổng dám":   ("không dám", "Phương ngữ Nam. Văn bản: 'không dám'.", "dialect"),
    "hổng biết":  ("không biết", "Phương ngữ Nam. Văn bản: 'không biết'.", "dialect"),
    "dzậy":       ("vậy", "Phương ngữ Nam: 'dz' → 'v'. Văn bản: 'vậy'.", "dialect"),
    "dzui":       ("vui", "Phương ngữ Nam: 'dz' → 'v'. Văn bản: 'vui'.", "dialect"),
    "dui dẻ":     ("vui vẻ", "Phương ngữ Nam: 'd' → 'v'. Văn bản: 'vui vẻ'.", "dialect"),
    "trển":       ("trên", "Phương ngữ Trung/Nam. Văn bản: 'trên'.", "dialect"),
    "mình ên":    ("một mình", "Phương ngữ Nam. Văn bản: 'một mình'.", "dialect"),
}
