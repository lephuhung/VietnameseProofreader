import threading
import signal
import sys
import pystray
from PIL import Image, ImageDraw
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import logging
import json

# Detect base directory: PyInstaller (.exe) vs chạy trực tiếp
if getattr(sys, 'frozen', False):
    # Chạy từ .exe (PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Chạy trực tiếp python
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cấu hình logging — hỗ trợ noconsole mode
if sys.stdout is None or sys.stderr is None:
    # PyInstaller --noconsole: log vào file thay vì console
    log_file = os.path.join(BASE_DIR, "vngrammar.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        filename=log_file,
        filemode='w'
    )
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger("vngrammar")

# Import Hybrid Engine
from engine.analyzer import analyze

# ============================================================
#  CẤU HÌNH SETTINGS (lưu vào file JSON)
# ============================================================
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "layer1_enabled": True,
    "hunspell_enabled": True,
    "hunspell_variant": "both",
    "hunspell_ignore_words": [],
    "hunspell_skip_uppercase": True,
    "layer2_enabled": True,
    "check_punctuation": True,
    "check_capitalization": True,
    "check_informal": True,
    "check_dialect": True,
    "check_redundancy": True,
    "writing_style": "administrative",  # administrative, journalism, free
    "max_sentence_length": 50,
}

def load_settings() -> dict:
    """Đọc config từ file, nếu chưa có thì tạo mặc định."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            # Merge với default (phòng trường hợp thêm key mới)
            merged = {**DEFAULT_SETTINGS, **saved}
            return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """Lưu config ra file."""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

current_settings = load_settings()

# ============================================================
#  FASTAPI SETUP
# ============================================================
app = FastAPI(title="Vietnamese Grammar Assistant Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/check")
async def check_grammar(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")
        
        result = analyze(text, settings=current_settings)
        logger.info(f"Analyzed {len(text)} chars: {result['stats']}")
        return result
    except Exception as e:
        logger.error(f"Error in /check: {e}", exc_info=True)
        # Trả về kết quả rỗng thay vì crash 500
        return {
            "errors": [],
            "stats": {"layer1_errors": 0, "layer2_errors": 0, "total_time_ms": 0},
            "error_message": str(e)
        }

@app.get("/settings")
async def get_settings():
    """Trả về cài đặt hiện tại cho frontend."""
    return {"status": "success", "settings": current_settings}

@app.post("/settings")
async def update_settings(request: Request):
    """Cập nhật cài đặt từ frontend."""
    global current_settings
    data = await request.json()
    
    # Chỉ cập nhật các key hợp lệ
    for key in DEFAULT_SETTINGS:
        if key in data:
            current_settings[key] = data[key]
    
    save_settings(current_settings)
    logger.info(f"Settings updated: {current_settings}")
    return {"status": "success", "settings": current_settings}

# ============================================================
#  CUSTOM WORDS API — Từ điển tùy chỉnh của người dùng
# ============================================================
CUSTOM_WORDS_FILE = os.path.join(BASE_DIR, "custom_words.json")

def load_custom_words():
    if os.path.exists(CUSTOM_WORDS_FILE):
        with open(CUSTOM_WORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_custom_words(words):
    with open(CUSTOM_WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

def _reload_custom_to_engine():
    """Nạp từ điển tùy chỉnh vào engine."""
    from engine.rules import ALL_CONFUSED_PAIRS
    words = load_custom_words()
    for entry in words:
        ALL_CONFUSED_PAIRS[entry["wrong"]] = (
            entry["correct"],
            entry.get("reason", "Từ tùy chỉnh của người dùng."),
            "spelling"
        )

# Nạp custom words khi khởi động
_reload_custom_to_engine()

@app.get("/custom-words")
async def get_custom_words():
    return {"status": "success", "words": load_custom_words()}

@app.post("/custom-words")
async def add_custom_word(request: Request):
    data = await request.json()
    wrong = data.get("wrong", "").strip()
    correct = data.get("correct", "").strip()
    reason = data.get("reason", "Từ tùy chỉnh của người dùng.").strip()
    
    if not wrong or not correct:
        return {"status": "error", "message": "Cần nhập cả từ sai và từ đúng."}
    if wrong.lower() == correct.lower():
        return {"status": "error", "message": "Từ sai và từ đúng không được giống nhau."}
    
    words = load_custom_words()
    # Kiểm tra trùng
    for w in words:
        if w["wrong"].lower() == wrong.lower():
            return {"status": "error", "message": f"Từ '{wrong}' đã có trong từ điển."}
    
    words.append({"wrong": wrong, "correct": correct, "reason": reason})
    save_custom_words(words)
    _reload_custom_to_engine()
    logger.info(f"Custom word added: '{wrong}' → '{correct}'")
    return {"status": "success", "words": words}

@app.delete("/custom-words")
async def delete_custom_word(request: Request):
    data = await request.json()
    wrong = data.get("wrong", "").strip().lower()
    
    words = load_custom_words()
    words = [w for w in words if w["wrong"].lower() != wrong]
    save_custom_words(words)
    _reload_custom_to_engine()
    logger.info(f"Custom word deleted: '{wrong}'")
    return {"status": "success", "words": words}

# ============================================================
#  WHITELIST API — Từ ghép phương ngữ hợp lệ
# ============================================================
USER_WHITELIST_FILE = os.path.join(BASE_DIR, "user_whitelist.json")

def load_user_whitelist():
    if os.path.exists(USER_WHITELIST_FILE):
        with open(USER_WHITELIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_whitelist(data):
    with open(USER_WHITELIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _reload_whitelist():
    """Nạp lại whitelist vào engine."""
    from engine.rules import DIALECT_COMPOUND_WHITELIST
    user_wl = load_user_whitelist()
    for key, vals in user_wl.items():
        key_lower = key.lower()
        if key_lower in DIALECT_COMPOUND_WHITELIST:
            for v in vals:
                if v.lower() not in DIALECT_COMPOUND_WHITELIST[key_lower]:
                    DIALECT_COMPOUND_WHITELIST[key_lower].append(v.lower())
        else:
            DIALECT_COMPOUND_WHITELIST[key_lower] = [v.lower() for v in vals]

@app.get("/whitelist")
async def get_whitelist():
    from engine.rules import DIALECT_COMPOUND_WHITELIST
    return {"status": "success", "whitelist": DIALECT_COMPOUND_WHITELIST, "user": load_user_whitelist()}

@app.post("/whitelist")
async def add_whitelist(request: Request):
    data = await request.json()
    dialect_word = data.get("dialect_word", "").strip().lower()
    compound = data.get("compound", "").strip().lower()
    
    if not dialect_word or not compound:
        return {"status": "error", "message": "Cần nhập từ phương ngữ và từ ghép."}
    
    user_wl = load_user_whitelist()
    if dialect_word not in user_wl:
        user_wl[dialect_word] = []
    if compound not in user_wl[dialect_word]:
        user_wl[dialect_word].append(compound)
    
    save_user_whitelist(user_wl)
    _reload_whitelist()
    logger.info(f"Whitelist added: '{compound}' for dialect '{dialect_word}'")
    return {"status": "success", "user_whitelist": user_wl}

@app.delete("/whitelist")
async def delete_whitelist(request: Request):
    data = await request.json()
    dialect_word = data.get("dialect_word", "").strip().lower()
    compound = data.get("compound", "").strip().lower()
    
    user_wl = load_user_whitelist()
    if dialect_word in user_wl and compound in user_wl[dialect_word]:
        user_wl[dialect_word].remove(compound)
        if not user_wl[dialect_word]:
            del user_wl[dialect_word]
    
    save_user_whitelist(user_wl)
    _reload_whitelist()
    return {"status": "success", "user_whitelist": user_wl}

# ============================================================
#  IGNORE LIST API — Từ người dùng chọn bỏ qua
# ============================================================
IGNORED_WORDS_FILE = os.path.join(BASE_DIR, "ignored_words.json")

def load_ignored_words():
    if os.path.exists(IGNORED_WORDS_FILE):
        try:
            with open(IGNORED_WORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_ignored_words(words):
    with open(IGNORED_WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

def _reload_ignored():
    """Nạp lại ignored list vào engine."""
    from engine import rules
    rules.IGNORED_WORDS = set(w.lower() for w in load_ignored_words())

# Nạp lần đầu
_reload_ignored()

@app.get("/ignore")
async def get_ignored():
    return {"status": "success", "ignored": load_ignored_words()}

@app.post("/ignore")
async def add_ignored(request: Request):
    data = await request.json()
    word = data.get("word", "").strip()
    if not word:
        return {"status": "error", "message": "Cần nhập từ cần bỏ qua."}

    words = load_ignored_words()
    if word.lower() not in [w.lower() for w in words]:
        words.append(word)
        save_ignored_words(words)
        _reload_ignored()
        logger.info(f"Ignored word added: '{word}'")
    return {"status": "success", "ignored": words}

@app.delete("/ignore")
async def remove_ignored(request: Request):
    data = await request.json()
    word = data.get("word", "").strip().lower()

    words = load_ignored_words()
    words = [w for w in words if w.lower() != word]
    save_ignored_words(words)
    _reload_ignored()
    logger.info(f"Ignored word removed: '{word}'")
    return {"status": "success", "ignored": words}

# Phục vụ frontend
if getattr(sys, 'frozen', False):
    addin_dir = os.path.join(BASE_DIR, 'addin')
else:
    addin_dir = os.path.join(os.path.dirname(BASE_DIR), 'addin')

# Serve index.html explicitly (so API routes at / don't get overridden)
from fastapi.responses import FileResponse

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(addin_dir, "index.html"))

@app.get("/index.html")
async def serve_index_html():
    return FileResponse(os.path.join(addin_dir, "index.html"))

# Mount static files for CSS/JS/assets (AFTER API routes)
app.mount("/", StaticFiles(directory=addin_dir), name="addin")

# ============================================================
#  SYSTEM TRAY
# ============================================================
def create_image():
    """Tạo icon đẹp hơn cho System Tray."""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Nền tròn gradient (xanh ngọc)
    dc.ellipse([2, 2, size-2, size-2], fill='#10B981')
    
    # Chữ VN trắng ở giữa
    dc.text((size//4, size//4), "VN", fill="white", font_size=22)
    return image

icon_instance = None

# --- Startup shortcut helpers ---
def _startup_shortcut_path():
    """Trả về đường dẫn shortcut trong Startup folder."""
    startup = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    return os.path.join(startup, "VNGrammar.lnk")

def _is_autostart_enabled():
    return os.path.exists(_startup_shortcut_path())

def _toggle_autostart(icon, item):
    """Bật/tắt khởi động cùng Windows."""
    shortcut = _startup_shortcut_path()
    if os.path.exists(shortcut):
        os.remove(shortcut)
        logger.info("Auto-start: TẮT")
    else:
        # Tạo shortcut bằng PowerShell (tương tự create_shortcut.ps1)
        try:
            import subprocess
            if getattr(sys, 'frozen', False):
                exe = sys.executable
            else:
                exe = os.path.abspath(os.path.join(BASE_DIR, '..', 'dist', 'VNGrammar', 'VNGrammar.exe'))
            ps_cmd = f'''
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("{shortcut}")
$sc.TargetPath = "{exe}"
$sc.WorkingDirectory = "{os.path.dirname(exe)}"
$sc.Description = "VN Grammar Assistant"
$sc.WindowStyle = 7
$sc.Save()
'''
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd],
                           capture_output=True, timeout=10)
            logger.info("Auto-start: BẬT")
        except Exception as e:
            logger.warning(f"Không thể tạo shortcut: {e}")
    # Rebuild menu để cập nhật checkbox
    _rebuild_tray_menu()

# --- Writing style switch ---
def _set_writing_style(style_key):
    def action(icon, item):
        current_settings["writing_style"] = style_key
        save_settings(current_settings)
        logger.info(f"Văn phong đã chuyển sang: {style_key}")
        _rebuild_tray_menu()
    return action

def _is_style_checked(style_key):
    def check(item):
        return current_settings.get("writing_style", "administrative") == style_key
    return check

# --- Quản lý từ điển (tkinter GUI) ---
def _open_dictionary_manager(icon, item):
    """Mở cửa sổ quản lý từ điển + từ bỏ qua."""
    import threading
    threading.Thread(target=_show_dict_window, daemon=True).start()

def _show_dict_window():
    """Tkinter window hiển thị custom words + ignored words."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        logger.warning("tkinter không khả dụng.")
        return

    win = tk.Tk()
    win.title("VN Grammar — Quản lý từ điển")
    win.geometry("520x600")
    win.resizable(False, True)
    try:
        win.iconbitmap(default='')  # Suppress default tk icon
    except Exception:
        pass

    style = ttk.Style()
    style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
    style.configure("Item.TLabel", font=("Segoe UI", 10))

    # ---- Tab control ----
    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ==== TAB 1: Từ điển tùy chỉnh ====
    tab_custom = ttk.Frame(notebook)
    notebook.add(tab_custom, text="  Từ điển tùy chỉnh  ")

    # Add form
    add_frame = ttk.Frame(tab_custom)
    add_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
    ttk.Label(add_frame, text="Từ sai:").pack(side=tk.LEFT)
    entry_wrong = ttk.Entry(add_frame, width=15)
    entry_wrong.pack(side=tk.LEFT, padx=4)
    ttk.Label(add_frame, text="→").pack(side=tk.LEFT)
    entry_correct = ttk.Entry(add_frame, width=15)
    entry_correct.pack(side=tk.LEFT, padx=4)

    def add_custom():
        w, c = entry_wrong.get().strip(), entry_correct.get().strip()
        if not w or not c:
            return
        words = load_custom_words()
        if any(x["wrong"].lower() == w.lower() for x in words):
            messagebox.showinfo("Trùng", f"'{w}' đã có trong từ điển.")
            return
        words.append({"wrong": w, "correct": c, "reason": "Từ tùy chỉnh."})
        save_custom_words(words)
        _reload_custom_to_engine()
        entry_wrong.delete(0, tk.END)
        entry_correct.delete(0, tk.END)
        refresh_custom_list()

    ttk.Button(add_frame, text="Thêm", command=add_custom, width=6).pack(side=tk.LEFT, padx=4)

    # List
    custom_list_frame = ttk.Frame(tab_custom)
    custom_list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
    custom_tree = ttk.Treeview(custom_list_frame, columns=("wrong", "correct"), show="headings", height=12)
    custom_tree.heading("wrong", text="Từ sai")
    custom_tree.heading("correct", text="Từ đúng")
    custom_tree.column("wrong", width=200)
    custom_tree.column("correct", width=200)
    custom_scroll = ttk.Scrollbar(custom_list_frame, orient=tk.VERTICAL, command=custom_tree.yview)
    custom_tree.configure(yscrollcommand=custom_scroll.set)
    custom_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    custom_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_custom_list():
        custom_tree.delete(*custom_tree.get_children())
        for w in load_custom_words():
            custom_tree.insert("", tk.END, values=(w["wrong"], w["correct"]))

    def delete_custom():
        sel = custom_tree.selection()
        if not sel:
            return
        wrong_val = custom_tree.item(sel[0])["values"][0]
        words = [w for w in load_custom_words() if w["wrong"].lower() != str(wrong_val).lower()]
        save_custom_words(words)
        _reload_custom_to_engine()
        refresh_custom_list()

    ttk.Button(tab_custom, text="Xóa mục đã chọn", command=delete_custom).pack(pady=(0, 8))
    refresh_custom_list()

    # ==== TAB 2: Từ đã bỏ qua ====
    tab_ignored = ttk.Frame(notebook)
    notebook.add(tab_ignored, text="  Từ đã bỏ qua  ")

    ignored_list_frame = ttk.Frame(tab_ignored)
    ignored_list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    ignored_tree = ttk.Treeview(ignored_list_frame, columns=("word",), show="headings", height=15)
    ignored_tree.heading("word", text="Từ/cụm từ đã bỏ qua")
    ignored_tree.column("word", width=400)
    ignored_scroll = ttk.Scrollbar(ignored_list_frame, orient=tk.VERTICAL, command=ignored_tree.yview)
    ignored_tree.configure(yscrollcommand=ignored_scroll.set)
    ignored_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    ignored_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_ignored_list():
        ignored_tree.delete(*ignored_tree.get_children())
        for w in load_ignored_words():
            ignored_tree.insert("", tk.END, values=(w,))

    def delete_ignored():
        sel = ignored_tree.selection()
        if not sel:
            return
        word_val = str(ignored_tree.item(sel[0])["values"][0])
        words = [w for w in load_ignored_words() if w.lower() != word_val.lower()]
        save_ignored_words(words)
        _reload_ignored()
        refresh_ignored_list()

    ttk.Button(tab_ignored, text="Gỡ bỏ qua mục đã chọn", command=delete_ignored).pack(pady=(0, 8))
    refresh_ignored_list()

    # ---- Status bar ----
    status_text = f"Từ điển: {len(load_custom_words())} mục  |  Bỏ qua: {len(load_ignored_words())} mục"
    ttk.Label(win, text=status_text, font=("Segoe UI", 9), foreground="gray").pack(pady=(0, 6))

    win.mainloop()

# --- Build tray menu ---
def _rebuild_tray_menu():
    """Rebuild menu khi thay đổi settings."""
    global icon_instance
    if not icon_instance:
        return

    menu = pystray.Menu(
        pystray.MenuItem('Trạng thái: Đang chạy ✓', lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Văn phong', pystray.Menu(
            pystray.MenuItem('Hành chính', _set_writing_style('administrative'),
                             checked=_is_style_checked('administrative'), radio=True),
            pystray.MenuItem('Báo chí', _set_writing_style('journalism'),
                             checked=_is_style_checked('journalism'), radio=True),
            pystray.MenuItem('Tự do', _set_writing_style('free'),
                             checked=_is_style_checked('free'), radio=True),
        )),
        pystray.MenuItem('Quản lý từ điển', _open_dictionary_manager),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Khởi động cùng Windows',
                         _toggle_autostart,
                         checked=lambda item: _is_autostart_enabled()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Phiên bản 1.0.0', lambda: None, enabled=False),
        pystray.MenuItem('Thoát', quit_action),
    )
    icon_instance.menu = menu
    icon_instance.update_menu()

def setup_tray():
    """Khởi tạo System Tray (chạy trên daemon thread)."""
    global icon_instance

    menu = pystray.Menu(
        pystray.MenuItem('Trạng thái: Đang chạy ✓', lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Văn phong', pystray.Menu(
            pystray.MenuItem('Hành chính', _set_writing_style('administrative'),
                             checked=_is_style_checked('administrative'), radio=True),
            pystray.MenuItem('Báo chí', _set_writing_style('journalism'),
                             checked=_is_style_checked('journalism'), radio=True),
            pystray.MenuItem('Tự do', _set_writing_style('free'),
                             checked=_is_style_checked('free'), radio=True),
        )),
        pystray.MenuItem('Quản lý từ điển', _open_dictionary_manager),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Khởi động cùng Windows',
                         _toggle_autostart,
                         checked=lambda item: _is_autostart_enabled()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Phiên bản 1.0.0', lambda: None, enabled=False),
        pystray.MenuItem('Thoát', quit_action),
    )

    image = create_image()
    icon_instance = pystray.Icon("VNGrammar", image, "VN Grammar Assistant v1.0.0 — by thanh007", menu)
    icon_instance.run()

def quit_action(icon, item):
    """Thoát hệ thống."""
    icon.stop()
    logger.info("Đang tắt VN Grammar Assistant...")
    os._exit(0)

# ============================================================
#  MAIN — Khởi động
# ============================================================
if __name__ == '__main__':
    # Fix: PyInstaller --noconsole set sys.stdout=None → print() crash
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')
    
    print("============================================")
    print("  VN Grammar Assistant - Core Engine")
    print("  Hybrid Local Engine v1.0.0")
    print("  (c) 2026 by thanh007")
    print("============================================")
    
    # Chạy System Tray trên daemon thread (không chặn Ctrl+C)
    tray_thread = threading.Thread(target=setup_tray, daemon=True)
    tray_thread.start()
    logger.info("System Tray icon đã khởi động.")
    
    # Chạy API Server ở MAIN thread (xử lý Ctrl+C tốt)
    # Office Add-in cho phép http://localhost (không cần SSL cho sideloaded add-in)
    kwargs = {
        "host": "localhost",
        "port": 8000,
        "log_level": "info",
    }
    logger.info(f"HTTP Server khởi động tại http://localhost:{kwargs['port']}")

    try:
        config = uvicorn.Config(app, **kwargs)
        server = uvicorn.Server(config)
        server.run()
    except KeyboardInterrupt:
        logger.info("Đã tắt server bằng Ctrl+C.")
    finally:
        logger.info("Thoát VN Grammar Assistant.")
        os._exit(0)  # Force exit ngay, tránh pystray block
