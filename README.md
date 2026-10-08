# VietnameseProofreader

Kiểm tra chính tả tiếng Việt offline: engine và Word Add-in từ VNGrammar kết hợp dữ liệu hunspell-vi.

## Điểm mới

- Nạp hai danh sách `vi-DauCu.dic` và `vi-DauMoi.dic` (mỗi danh sách khai báo 6.631 mục; hợp nhất và loại trùng khi chạy).
- Giữ bộ quy tắc chính tả, hành chính và NLP underthesea của VNGrammar. Hunspell bổ sung âm tiết không có trong từ điển, không thay thế quy tắc theo ngữ cảnh.
- Gợi ý bằng REP trong `.aff` và độ tương tự ký tự; **không phải toàn bộ thuật toán Hunspell**. Dữ liệu hiện tại không có affix flags nên đọc trực tiếp danh sách từ.
- Giữ vị trí lỗi trên văn bản gốc, kể cả Unicode NFD; API cung cấp cả offset Python và UTF-16.
- Lỗi từ từ điển có `auto_fix: false`: không đưa vào “Sửa tất cả”; người dùng duyệt gợi ý riêng.
- Bỏ qua URL, email, mã chứa số, chữ viết tắt HOA và danh sách tùy chỉnh.

## Chạy engine ngay (Python 3.10+, không cần cài thư viện)

```bash
git clone https://github.com/lephuhung/VietnameseProofreader.git
cd VietnameseProofreader
python server/cli.py "Tôi đang ngiêên cứu và sử lý hồ sơ."
python -m unittest discover -s tests -v
```

## Microsoft Word trên Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-windows.txt
python server/main.py
```

Backend dùng `http://localhost:8000`. Xem [hướng dẫn gốc](docs/UPSTREAM_README.md) và `install.bat` để sideload thư mục `addin`. Các script build Windows được giữ từ upstream; chưa xác minh cài add-in hoặc build EXE trên Windows trong môi trường phát triển này. Office.js được upstream đóng gói trong `addin/lib`; khả năng offline thực tế phụ thuộc Word và môi trường cài đặt.

## API

`POST /check` với JSON `{"text":"Tôi đang ngiêên cứu."}`. Backend desktop sử dụng cài đặt đã lưu qua `POST /settings`:

```json
{
  "hunspell_enabled": true,
  "hunspell_variant": "both",
  "hunspell_ignore_words": ["FastAPI", "Velociraptor"],
  "hunspell_skip_uppercase": true
}
```

`hunspell_variant`: `both` (mặc định), `old` (DauCu), `new` (DauMoi). `suggestions` chứa tối đa 5 gợi ý; `suggestion` là gợi ý đầu tiên để tương thích add-in cũ. Từ không có gợi ý giữ nguyên, không bị xóa. `position`/`length` đếm code point trong văn bản gốc; `position_utf16`/`length_utf16` dành cho ứng dụng JavaScript.

ONLYOFFICE có thể dùng chung engine qua API, nhưng **repo chưa có plugin ONLYOFFICE**. Không nên coi add-in Word là plugin ONLYOFFICE.

## Giới hạn

Danh sách Hunspell chứa âm tiết, không phải kho từ ghép hoặc mô hình ngữ nghĩa. Tên riêng, từ chuyên ngành, từ nước ngoài và từ hiếm có thể bị báo; hãy thêm vào danh sách bỏ qua. NLP là tùy chọn và dùng quy tắc/POS, không phải LLM. Cần đánh giá trên văn bản thực tế trước khi dùng tự động. Không gửi tài liệu ra dịch vụ AI bên ngoài.

## Nguồn và giấy phép

Xem [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). VNGrammar ghi MIT trong README nhưng không cung cấp file LICENSE riêng ở commit đã nhập. Dữ liệu hunspell-vi có thông báo GPL: giữ nguyên thông báo và bản GPLv3 trong thư mục dữ liệu. Không gán toàn bộ repo này là MIT. Lịch sử nguồn được ghi bằng URL và commit; repo này là bản kết hợp, không phải GitHub fork của cả hai nguồn.
