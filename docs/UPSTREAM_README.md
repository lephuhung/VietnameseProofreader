# VN Grammar Assistant

Trợ lý kiểm tra chính tả và văn phong tiếng Việt — chạy hoàn toàn offline dưới dạng Microsoft Word Add-in.

## Tính năng

- **2-layer engine**: Layer 1 (từ điển + quy tắc) siêu nhanh, Layer 2 (NLP/underthesea) phân tích ngữ cảnh sâu
- **106 cặp từ nhầm lẫn** phổ biến (triển khai/triễn khai, nỗ lực/nổ lực, ...)
- **58 từ khẩu ngữ/teencode** (2k, cmn, ko, ...)
- **11 lỗi thừa từ Hán Việt** (kết quả đạt được, lý do là vì, ...)
- Kiểm tra chấm câu, viết hoa, phương ngữ
- 3 chế độ văn phong: Hành chính, Báo chí, Tự do
- Quét đoạn chọn hoặc toàn văn bản
- Sửa từng lỗi hoặc sửa tất cả một lần
- Bỏ qua (ignore) từ không muốn kiểm tra
- Từ điển tùy chỉnh (thêm cặp sai→đúng riêng)
- Giao diện sáng/tối
- System tray với auto-start cùng Windows

## Cấu trúc

```
Grammar/
├── server/                 # Python FastAPI backend
│   ├── main.py             # Server + system tray + API
│   ├── engine/
│   │   ├── dictionary.py   # Từ điển lỗi chính tả
│   │   ├── rules.py        # Layer 1: rule-based checker
│   │   ├── nlp_analyzer.py # Layer 2: NLP (underthesea)
│   │   └── analyzer.py     # Điều phối 2 layers
│   └── test_engine.py      # Unit tests
├── addin/                  # Word Add-in (Office.js)
│   ├── manifest.xml        # Add-in manifest
│   ├── index.html          # Giao diện
│   ├── app.js              # Logic frontend
│   ├── style.css           # Styles
│   ├── assets/             # Icons
│   └── lib/                # Office.js (offline)
├── tools/                  # Scripts hỗ trợ
│   ├── download_officejs.py
│   └── create_shortcut.ps1
├── build.bat               # Build exe (PyInstaller)
├── package.bat             # Đóng gói offline
├── install.bat             # Cài đặt add-in
└── uninstall.bat           # Gỡ cài đặt
```

## Yêu cầu

- Windows 10/11
- Microsoft Word 2016 trở lên (không hỗ trợ Compatibility Mode)
- Python 3.10+ (chỉ cần khi phát triển, không cần khi dùng bản build)

## Cài đặt từ source

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/VNGrammar.git
cd VNGrammar

# 2. Tạo virtual environment
cd server
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn underthesea pystray pillow pyinstaller

# 3. Chạy server
python main.py

# 4. Sideload add-in vào Word
# Mở Word → File → Options → Trust Center → Trust Center Settings
# → Trusted Add-in Catalogs → thêm đường dẫn đến thư mục addin/
# Restart Word → Insert → My Add-ins → Shared Folder → VN Grammar Assistant
```

## Cài đặt từ bản build (offline)

```bash
# 1. Build exe
package.bat

# 2. Copy thư mục dist/VNGrammar ra máy đích
# 3. Chạy install.bat (cần quyền Admin)
# 4. Mở Word → Insert → My Add-ins
```

## API Endpoints

| Method | Path | Mô tả |
|--------|------|--------|
| POST | `/check` | Kiểm tra văn bản |
| GET | `/health` | Health check |
| GET/POST/DELETE | `/ignore` | Quản lý danh sách từ bỏ qua |
| GET/POST/DELETE | `/custom-words` | Quản lý từ điển tùy chỉnh |
| GET/POST | `/settings` | Cài đặt engine |

## Lưu ý

- Add-in chỉ hoạt động với file `.docx` mới hoặc đã chuyển đổi khỏi Compatibility Mode (File → Info → Convert)
- Backend chạy trên `http://localhost:8000` (không cần HTTPS cho sideloaded add-in)

## License

MIT
