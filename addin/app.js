let backendUrl = ""; // Relative URL — frontend & API cùng server
let currentErrors = []; // Lưu lỗi hiện tại cho Fix All

// ============================================================
//  THEME ENGINE — Tự phát hiện theme Word + cho phép toggle
// ============================================================
function detectOfficeTheme() {
    try {
        // Office.js cung cấp context.document.officeTheme
        // nhưng cách đáng tin cậy nhất là kiểm tra CSS class của body
        const bodyBg = window.getComputedStyle(document.body).backgroundColor;
        
        // Nếu Office inject class chỉ theme
        if (document.body.classList.contains('office-theme-dark') ||
            document.body.classList.contains('ms-bgColor-neutralDark')) {
            return 'dark';
        }

        // Parse background color để phán đoán
        if (bodyBg) {
            const match = bodyBg.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
            if (match) {
                const brightness = (parseInt(match[1]) * 299 + parseInt(match[2]) * 587 + parseInt(match[3]) * 114) / 1000;
                return brightness < 128 ? 'dark' : 'light';
            }
        }
    } catch (e) { /* fallback */ }
    
    // Fallback: dùng prefers-color-scheme của hệ điều hành
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    const sunIcon = document.getElementById('icon-sun');
    const moonIcon = document.getElementById('icon-moon');
    
    if (sunIcon && moonIcon) {
        if (theme === 'dark') {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        } else {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }
    }
    
    // Lưu preference
    try { localStorage.setItem('vngrammar-theme', theme); } catch(e) {}
}

function initTheme() {
    // Ưu tiên: 1) User đã chọn trước đó, 2) Theme Word, 3) OS preference
    let saved = null;
    try { saved = localStorage.getItem('vngrammar-theme'); } catch(e) {}
    
    const theme = saved || detectOfficeTheme();
    applyTheme(theme);
    
    // Toggle button
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    }
    
    // Theo dõi thay đổi từ OS
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            let saved = null;
            try { saved = localStorage.getItem('vngrammar-theme'); } catch(ex) {}
            if (!saved) {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
}

// ============================================================
//  OFFICE.JS INITIALIZATION
// ============================================================
Office.onReady((info) => {
    initTheme();
    initSettings();
    
    if (info.host === Office.HostType.Word) {
        document.getElementById("status-box").innerHTML = "Đã kết nối với Word.";
        document.getElementById("run").onclick = scanSelectedText;
        document.getElementById("check-all").onclick = scanAllText;
        document.getElementById("fix-all").onclick = fixAll;
        checkConnection();
    }
});

// ============================================================
//  SETTINGS PANEL
// ============================================================
function initSettings() {
    const toggleBtn = document.getElementById("settings-toggle");
    const panel = document.getElementById("settings-panel");
    
    // Toggle mở/đóng panel
    toggleBtn.addEventListener("click", () => {
        const isOpen = panel.style.display !== "none";
        panel.style.display = isOpen ? "none" : "block";
        toggleBtn.classList.toggle("active", !isOpen);
    });
    
    // Gắn event cho Custom Words
    const cwAddBtn = document.getElementById("cw-add");
    if (cwAddBtn) cwAddBtn.addEventListener("click", addCustomWord);
    // Enter key trên input
    ["cw-wrong", "cw-correct"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("keydown", (e) => { if (e.key === "Enter") addCustomWord(); });
    });
    
    // Tải settings + custom words + ignored words từ server
    loadSettingsFromServer();
    loadCustomWords();
    loadIgnoredWords();
    
    // Gắn event listeners cho tất cả controls
    const checkboxMap = {
        "set-layer1": "layer1_enabled",
        "set-layer2": "layer2_enabled",
        "set-informal": "check_informal",
        "set-dialect": "check_dialect",
        "set-punctuation": "check_punctuation",
        "set-capitalization": "check_capitalization",
        "set-redundancy": "check_redundancy",
    };
    
    for (const [elementId, settingKey] of Object.entries(checkboxMap)) {
        const el = document.getElementById(elementId);
        if (el) {
            el.addEventListener("change", () => {
                saveSettingToServer(settingKey, el.checked);
            });
        }
    }
    
    // Radio buttons cho writing_style
    document.querySelectorAll('input[name="writing_style"]').forEach(radio => {
        radio.addEventListener("change", () => {
            saveSettingToServer("writing_style", radio.value);
        });
    });
}

async function loadSettingsFromServer() {
    try {
        const response = await fetch(`${backendUrl}/settings`);
        const data = await response.json();
        if (data.status === "success" && data.settings) {
            applySettingsToUI(data.settings);
        }
    } catch (e) {
        // Server chưa chạy, dùng mặc định
    }
}

function applySettingsToUI(settings) {
    const checkboxMap = {
        "set-layer1": "layer1_enabled",
        "set-layer2": "layer2_enabled",
        "set-informal": "check_informal",
        "set-dialect": "check_dialect",
        "set-punctuation": "check_punctuation",
        "set-capitalization": "check_capitalization",
        "set-redundancy": "check_redundancy",
    };
    
    for (const [elementId, settingKey] of Object.entries(checkboxMap)) {
        const el = document.getElementById(elementId);
        if (el && settings[settingKey] !== undefined) {
            el.checked = settings[settingKey];
        }
    }
    
    // Radio writing_style
    if (settings.writing_style) {
        const radio = document.querySelector(`input[name="writing_style"][value="${settings.writing_style}"]`);
        if (radio) radio.checked = true;
    }
}

async function saveSettingToServer(key, value) {
    try {
        await fetch(`${backendUrl}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ [key]: value })
        });
    } catch (e) {
        // Fail silently
    }
}

// ============================================================
//  CUSTOM WORDS — Từ điển tùy chỉnh
// ============================================================
async function loadCustomWords() {
    try {
        const response = await fetch(`${backendUrl}/custom-words`);
        const data = await response.json();
        if (data.status === "success") renderCustomWords(data.words);
    } catch (e) { /* ignore */ }
}

function renderCustomWords(words) {
    const list = document.getElementById("cw-list");
    if (!list) return;
    list.innerHTML = words.map(w => `
        <div class="cw-item">
            <span class="cw-item-text">
                <span class="cw-wrong">${escapeHtml(w.wrong)}</span> → 
                <span class="cw-correct">${escapeHtml(w.correct)}</span>
            </span>
            <button class="cw-del-btn" onclick="deleteCustomWord('${escapeAttr(w.wrong)}')" title="Xóa">✕</button>
        </div>
    `).join('');
}

async function addCustomWord() {
    const wrongEl = document.getElementById("cw-wrong");
    const correctEl = document.getElementById("cw-correct");
    const wrong = wrongEl.value.trim();
    const correct = correctEl.value.trim();
    
    if (!wrong || !correct) return;
    
    try {
        const response = await fetch(`${backendUrl}/custom-words`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wrong, correct })
        });
        const data = await response.json();
        if (data.status === "success") {
            renderCustomWords(data.words);
            wrongEl.value = '';
            correctEl.value = '';
        } else {
            alert(data.message || "Lỗi khi thêm từ.");
        }
    } catch (e) {
        alert("Không thể kết nối server.");
    }
}

async function deleteCustomWord(wrong) {
    try {
        const response = await fetch(`${backendUrl}/custom-words`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wrong })
        });
        const data = await response.json();
        if (data.status === "success") renderCustomWords(data.words);
    } catch (e) { /* ignore */ }
}

// ============================================================
//  IGNORED WORDS — Danh sách từ đã bỏ qua
// ============================================================
async function loadIgnoredWords() {
    try {
        const response = await fetch(`${backendUrl}/ignore`);
        const data = await response.json();
        if (data.status === "success") renderIgnoredWords(data.ignored);
    } catch (e) { /* ignore */ }
}

function renderIgnoredWords(words) {
    const list = document.getElementById("ignored-list");
    if (!list) return;
    if (!words || words.length === 0) {
        list.innerHTML = '<div class="cw-empty">Chưa có từ nào bị bỏ qua.</div>';
        return;
    }
    list.innerHTML = words.map(w => `
        <div class="cw-item">
            <span class="cw-item-text">${escapeHtml(w)}</span>
            <button class="cw-del-btn" onclick="removeIgnoredWord('${escapeAttr(w)}')" title="Gỡ bỏ qua">✕</button>
        </div>
    `).join('');
}

async function removeIgnoredWord(word) {
    try {
        const response = await fetch(`${backendUrl}/ignore`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word })
        });
        const data = await response.json();
        if (data.status === "success") renderIgnoredWords(data.ignored);
    } catch (e) { /* ignore */ }
}

// ============================================================
//  CONNECTION CHECK
// ============================================================
async function checkConnection() {
    const statusEl = document.getElementById("connection-status");
    document.getElementById("status-box").innerHTML = "Đang kiểm tra kết nối Core Engine...";

    try {
        const response = await fetch(`${backendUrl}/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: "test" })
        });

        if (response.ok) {
            statusEl.innerHTML = `<span class="status-dot online"></span><span>Core Engine hoạt động</span>`;
            document.getElementById("status-box").innerHTML = "Sẵn sàng phân tích văn bản tiếng Việt.";
        } else {
            throw new Error("Bad response");
        }
    } catch (e) {
        statusEl.innerHTML = `<span class="status-dot offline"></span><span>Mất kết nối Core Engine</span>`;
        document.getElementById("status-box").innerHTML = "Vui lòng kiểm tra ứng dụng VNGrammar trên máy tính.";
    }
}

// ============================================================
//  NORMALIZE TEXT — Loại bỏ ký tự ẩn Word thêm vào
// ============================================================
function normalizeWordText(text) {
    return text
        .replace(/\u00A0/g, ' ')      // Non-breaking space → space
        .replace(/\uFEFF/g, '')       // BOM
        .replace(/\u000B/g, '\n')     // Vertical tab → newline
        .replace(/\u0007/g, '')       // Bell char (Word table cells)
        .replace(/\u0013/g, '')       // Field begin
        .replace(/\u0014/g, '')       // Field separator
        .replace(/\u0015/g, '')       // Field end
        .replace(/\r\n/g, '\n')      // CRLF → LF
        .replace(/\r/g, '\n')        // CR → LF
        .replace(/[ \t]+\n/g, '\n')  // Trailing whitespace
        .trim();
}

// ============================================================
//  WORD DOCUMENT SCANNING
// ============================================================
async function scanSelectedText() {
    // Xóa highlight vàng cũ trước khi quét lại
    await clearHighlights();
    
    return runWordAction(async (context) => {
        const selection = context.document.getSelection();
        selection.load("text");
        await context.sync();

        let text = normalizeWordText(selection.text);
        if (!text) {
            document.getElementById("status-box").innerHTML = "Vui lòng bôi đen đoạn văn bản cần kiểm tra.";
            return;
        }

        document.getElementById("status-box").innerHTML = "Đang phân tích ngữ cảnh...";
        await analyzeText(text);
    });
}

async function scanAllText() {
    // Xóa highlight vàng cũ trước khi quét lại
    await clearHighlights();
    
    return runWordAction(async (context) => {
        const docBody = context.document.body;
        docBody.load("text");
        await context.sync();

        let text = normalizeWordText(docBody.text);
        if (!text) {
            document.getElementById("status-box").innerHTML = "Văn bản đang trống.";
            return;
        }

        document.getElementById("status-box").innerHTML = "Đang quét toàn bộ văn bản...";
        await analyzeText(text);
    });
}

// Xóa tất cả highlight vàng cũ
async function clearHighlights() {
    try {
        await Word.run(async (context) => {
            const body = context.document.body;
            body.load('font');
            await context.sync();
            body.font.highlightColor = null;
            await context.sync();
        });
    } catch(e) { /* ignore */ }
}

// Reset toàn bộ định dạng: xóa highlight + đưa màu chữ về đen
async function resetFormatting() {
    const btn = document.getElementById('reset-format');
    const origText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Đang reset...';
    
    try {
        await Word.run(async (context) => {
            const body = context.document.body;
            body.load('font');
            await context.sync();
            
            // Xóa highlight vàng
            body.font.highlightColor = null;
            // Reset màu chữ về mặc định (đen)
            body.font.color = 'black';
            await context.sync();
        });
        document.getElementById("status-box").innerHTML = "Đã reset định dạng văn bản về mặc định.";
    } catch(e) {
        document.getElementById("status-box").innerHTML = "Lỗi khi reset định dạng.";
    }
    
    btn.disabled = false;
    btn.innerHTML = `<svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182M2.985 19.644l3.181-3.183" /></svg> Reset định dạng`;
}

async function runWordAction(callback) {
    try {
        await Word.run(callback);
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("status-box").innerHTML = `Lỗi Word API: ${error.message}`;
    }
}

// ============================================================
//  BACKEND COMMUNICATION
// ============================================================
async function analyzeText(text) {
    // Lưu text đã gửi để tính occurrence index
    window._lastScannedText = text;
    
    try {
        const response = await fetch(`${backendUrl}/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();
        
        // Tính occurrence index cho mỗi lỗi dựa trên position
        if (data.errors) {
            data.errors.forEach(err => {
                if (err.position !== undefined && err.position !== null) {
                    // Đếm số lần từ xuất hiện trước position này
                    const wordLower = err.word.toLowerCase();
                    const textLower = text.toLowerCase();
                    let count = 0;
                    let searchPos = 0;
                    while (searchPos <= err.position) {
                        const found = textLower.indexOf(wordLower, searchPos);
                        if (found === -1 || found > err.position) break;
                        if (found === err.position) { err._occurrenceIndex = count; break; }
                        count++;
                        searchPos = found + 1;
                    }
                    if (err._occurrenceIndex === undefined) err._occurrenceIndex = count;
                } else {
                    err._occurrenceIndex = 0;
                }
            });
        }
        
        renderResults(data);
    } catch (e) {
        document.getElementById("status-box").innerHTML = "Không thể kết nối với Core Engine.";
        const statusEl = document.getElementById("connection-status");
        statusEl.innerHTML = `<span class="status-dot offline"></span><span>Mất kết nối</span>`;
    }
}

// ============================================================
//  RENDER RESULTS
// ============================================================
function renderResults(data) {
    const resultBox = document.getElementById("results");
    resultBox.innerHTML = "";

    if (data.status === "success" && data.errors && data.errors.length > 0) {
        document.getElementById("status-box").innerHTML = `Phát hiện <b>${data.errors.length}</b> vấn đề.`;

        // Lưu lỗi hiện tại cho Fix All
        currentErrors = data.errors.slice();
        
        // Hiện nút Sửa tất cả + Reset định dạng
        const fixAllBtn = document.getElementById("fix-all");
        fixAllBtn.style.display = "flex";
        document.getElementById("reset-format").style.display = "flex";
        fixAllBtn.disabled = false;
        fixAllBtn.innerHTML = `
            <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.049.58.025 1.194-.14 1.743" />
            </svg>
            Sửa tất cả (${data.errors.length} lỗi)
        `;

        // Stats bar (hiển thị thông tin Layer 1 / Layer 2)
        if (data.stats) {
            const statsBar = document.createElement("div");
            statsBar.className = "stats-bar";
            const l2Status = data.stats.layer2_available
                ? `<span class="stat-dot" style="background:#10B981"></span> NLP: ${data.stats.layer2_errors} lỗi`
                : `<span class="stat-dot" style="background:#EF4444"></span> NLP: tắt`;
            statsBar.innerHTML = `
                <span class="stat-item"><span class="stat-dot" style="background:#3B82F6"></span> Rules: ${data.stats.layer1_errors} lỗi</span>
                <span class="stat-item">${l2Status}</span>
                <span class="stat-item">${data.stats.total_time_ms}ms</span>
            `;
            resultBox.appendChild(statsBar);
        }

        data.errors.forEach((err) => {
            const card = document.createElement("div");
            card.className = "error-card";
            
            // Dynamic border color theo loại lỗi
            const borderColor = err.color || "#EF4444";
            card.style.borderLeftColor = borderColor;
            
            // Badge label + color
            const label = err.label || "Lỗi";
            const isAiRefined = err.reason && err.reason.startsWith("[AI ngữ cảnh]");
            const reasonText = isAiRefined ? err.reason.replace("[AI ngữ cảnh] ", "") : err.reason;
            const aiBadge = isAiRefined ? `<span class="ai-badge">AI</span>` : "";
            
            // Click card → nhảy đến vị trí lỗi trong Word
            card.style.cursor = 'pointer';
            card.addEventListener('click', (e) => {
                // Không trigger khi click vào nút sửa hoặc bỏ qua
                if (e.target.closest('.fix-btn') || e.target.closest('.ignore-btn')) return;
                navigateToError(err.word, card, err._occurrenceIndex || 0);
            });
            
            card.innerHTML = `
                <span class="error-badge" style="background:${borderColor}">${escapeHtml(label)}</span>${aiBadge}
                <h4>
                    <span class="incorrect">${escapeHtml(err.word)}</span>
                    <svg class="arrow-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                    </svg>
                    <span class="correct">${escapeHtml(err.suggestion)}</span>
                </h4>
                <p>${escapeHtml(reasonText)}</p>
                <div class="card-actions">
                    <button class="fix-btn" onclick="replaceText(this, '${escapeAttr(err.word)}', '${escapeAttr(err.suggestion)}', ${err._occurrenceIndex || 0})">
                        <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:14px;height:14px">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Z" />
                        </svg>
                        Sửa
                    </button>
                    <button class="ignore-btn" onclick="ignoreWord(this, '${escapeAttr(err.word)}')">
                        <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:14px;height:14px">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12c1.292 4.338 5.31 7.5 10.066 7.5.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                        </svg>
                        Bỏ qua
                    </button>
                </div>
            `;
            resultBox.appendChild(card);
        });
    } else {
        document.getElementById("status-box").innerHTML = "Văn bản chuẩn, không phát hiện lỗi.";
        const successCard = document.createElement("div");
        successCard.className = "success-card";
        successCard.innerHTML = `
            <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:24px;height:24px;margin:0 auto 6px;display:block;color:var(--success)">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            Không tìm thấy lỗi chính tả hoặc ngữ pháp.
        `;
        resultBox.appendChild(successCard);

        // Ẩn nút Sửa tất cả + Reset
        document.getElementById("fix-all").style.display = "none";
        document.getElementById("reset-format").style.display = "none";
        currentErrors = [];

        // Hiện stats khi không có lỗi
        if (data.stats) {
            const statsBar = document.createElement("div");
            statsBar.className = "stats-bar";
            statsBar.style.marginTop = "8px";
            statsBar.innerHTML = `
                <span class="stat-item">Quét hoàn tất: ${data.stats.total_time_ms}ms</span>
                <span class="stat-item"><span class="stat-dot" style="background:${data.stats.layer2_available ? '#10B981' : '#EF4444'}"></span> NLP: ${data.stats.layer2_available ? 'bật' : 'tắt'}</span>
            `;
            resultBox.appendChild(statsBar);
        }
    }
}

// ============================================================
//  NAVIGATE TO ERROR — Click card → nhảy đến vị trí lỗi
// ============================================================
async function navigateToError(errorWord, card, occurrenceIndex) {
    // Highlight card đang active
    document.querySelectorAll('.error-card.active').forEach(c => c.classList.remove('active'));
    card.classList.add('active');
    const idx = occurrenceIndex || 0;
    
    try {
        await Word.run(async (context) => {
            const searchOpts = { matchCase: false };
            if (!errorWord.includes(' ')) searchOpts.matchWholeWord = true;
            const results = context.document.body.search(errorWord, searchOpts);
            context.load(results);
            await context.sync();
            
            // Dùng đúng occurrence index thay vì luôn items[0]
            const targetIdx = Math.min(idx, results.items.length - 1);
            if (results.items.length > 0 && targetIdx >= 0) {
                results.items[targetIdx].select();
                results.items[targetIdx].font.highlightColor = "Yellow";
                await context.sync();
                
                // Bỏ highlight sau 2 giây
                setTimeout(async () => {
                    try {
                        await Word.run(async (ctx) => {
                            const r = ctx.document.body.search(errorWord, searchOpts);
                            ctx.load(r);
                            await ctx.sync();
                            const ti = Math.min(idx, r.items.length - 1);
                            if (r.items.length > 0 && ti >= 0) {
                                r.items[ti].font.highlightColor = "None";
                                await ctx.sync();
                            }
                        });
                    } catch (e) { /* ignore */ }
                }, 2000);
            }
        });
    } catch (e) {
        // Fail silently
    }
}

// ============================================================
//  IGNORE WORD — Bỏ qua lỗi này vĩnh viễn
// ============================================================
async function ignoreWord(btnElement, word) {
    const card = btnElement.closest('.error-card');
    try {
        const resp = await fetch(`${backendUrl}/ignore`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ word: word }),
        });
        const data = await resp.json();
        if (data.status === "success") {
            // Animate card ra và xóa
            card.style.transition = "opacity 0.3s, transform 0.3s";
            card.style.opacity = "0";
            card.style.transform = "translateX(100%)";
            setTimeout(() => {
                card.remove();
                // Cập nhật số lỗi còn lại
                const remaining = document.querySelectorAll('.error-card').length;
                if (remaining === 0) {
                    document.getElementById("status-box").innerHTML = "Văn bản chuẩn, không phát hiện lỗi.";
                    document.getElementById("fix-all").style.display = "none";
                    document.getElementById("reset-format").style.display = "none";
                } else {
                    document.getElementById("status-box").innerHTML = `Tìm thấy ${remaining} gợi ý.`;
                }
                // Xóa khỏi currentErrors
                currentErrors = currentErrors.filter(e => e.word.toLowerCase() !== word.toLowerCase());
            }, 300);
        }
    } catch (err) {
        console.error("Ignore error:", err);
    }
}

// ============================================================
//  WORD TEXT REPLACEMENT
// ============================================================
async function replaceText(btnElement, wrongWord, correctWord, occurrenceIndex) {
    // Tìm card cha chứa nút bấm
    const card = btnElement.closest('.error-card');
    const idx = occurrenceIndex || 0;
    
    await Word.run(async (context) => {
        const searchOpts = { matchCase: false };
        // matchWholeWord không dùng cho pattern có dấu câu/khoảng trắng
        if (!wrongWord.includes(' ') && /^[\p{L}]+$/u.test(wrongWord)) {
            searchOpts.matchWholeWord = true;
        }
        const results = context.document.body.search(wrongWord, searchOpts);
        context.load(results);
        await context.sync();

        // Dùng đúng occurrence index
        const targetIdx = Math.min(idx, results.items.length - 1);
        if (results.items.length > 0 && targetIdx >= 0) {
            results.items[targetIdx].insertText(correctWord, Word.InsertLocation.replace);
            // Xóa highlight vàng nếu có
            results.items[targetIdx].font.highlightColor = null;
            results.items[targetIdx].font.color = "#10B981";
            await context.sync();

            // Fade-out rồi xóa card khỏi DOM
            if (card) {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '0';
                card.style.transform = 'translateX(20px)';
                card.style.maxHeight = card.scrollHeight + 'px';
                
                setTimeout(() => {
                    card.style.maxHeight = '0';
                    card.style.padding = '0';
                    card.style.marginBottom = '0';
                    card.style.borderWidth = '0';
                }, 200);
                
                setTimeout(() => {
                    card.remove();
                    updateErrorCount();
                }, 500);
            }

            document.getElementById("status-box").innerHTML = `Đã sửa: <b>${escapeHtml(wrongWord)}</b> thành <b>${escapeHtml(correctWord)}</b>.`;
        } else {
            document.getElementById("status-box").innerHTML = `Không tìm thấy từ <b>${escapeHtml(wrongWord)}</b> trong văn bản.`;
        }
    });
}

// ============================================================
//  FIX ALL — Sửa tất cả lỗi một lần
// ============================================================
async function fixAll() {
    const fixAllBtn = document.getElementById("fix-all");
    fixAllBtn.disabled = true;
    
    // Lọc chỉ những lỗi có gợi ý đơn (không chứa '/')
    const fixable = currentErrors.filter(err => err.auto_fix !== false && !err.suggestion.includes('/'));
    const skipped = currentErrors.filter(err => err.auto_fix === false || err.suggestion.includes('/'));
    
    if (fixable.length === 0) {
        document.getElementById("status-box").innerHTML = "Không có lỗi nào có thể tự động sửa. Vui lòng sửa thủ công.";
        fixAllBtn.disabled = false;
        return;
    }
    
    let fixed = 0;
    let failed = 0;
    
    document.getElementById("status-box").innerHTML = `Đang sửa 0/${fixable.length}...`;
    
    // Sửa tuần tự từng lỗi — từ cuối document lên đầu để tránh position shift
    const sorted = [...fixable].sort((a, b) => (b.position || 0) - (a.position || 0));
    
    for (const err of sorted) {
        try {
            await Word.run(async (context) => {
                const searchOpts = { matchCase: false };
                if (!err.word.includes(' ') && /^[\p{L}]+$/u.test(err.word)) {
                    searchOpts.matchWholeWord = true;
                }
                const results = context.document.body.search(err.word, searchOpts);
                context.load(results);
                await context.sync();
                
                const idx = err._occurrenceIndex || 0;
                const targetIdx = Math.min(idx, results.items.length - 1);
                if (results.items.length > 0 && targetIdx >= 0) {
                    results.items[targetIdx].insertText(err.suggestion, Word.InsertLocation.replace);
                    results.items[targetIdx].font.color = "#10B981";
                    await context.sync();
                    fixed++;
                } else {
                    failed++;
                }
            });
        } catch (e) {
            failed++;
        }
        
        // Cập nhật progress
        document.getElementById("status-box").innerHTML = `Đang sửa ${fixed + failed}/${fixable.length}...`;
        
        // Xóa card tương ứng khỏi DOM
        const cards = document.querySelectorAll('.error-card');
        for (const card of cards) {
            const incorrectEl = card.querySelector('.incorrect');
            if (incorrectEl && incorrectEl.textContent === err.word) {
                card.style.transition = 'all 0.2s ease';
                card.style.opacity = '0';
                card.style.maxHeight = '0';
                card.style.padding = '0';
                card.style.borderWidth = '0';
                setTimeout(() => card.remove(), 250);
                break;
            }
        }
        
        // Delay nhỏ để Word API xử lý kịp
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    // Hoàn tất
    fixAllBtn.style.display = "none";
    currentErrors = [];
    
    let message = `Đã sửa ${fixed}/${fixable.length} lỗi thành công.`;
    if (skipped.length > 0) {
        message += ` ${skipped.length} lỗi cần chọn gợi ý thủ công.`;
    }
    if (failed > 0) {
        message += ` ${failed} lỗi không tìm thấy trong văn bản.`;
    }
    document.getElementById("status-box").innerHTML = message;
    
    // Cập nhật lại giao diện
    setTimeout(() => updateErrorCount(), 300);
}

function updateErrorCount() {
    const resultBox = document.getElementById("results");
    const remainingCards = resultBox.querySelectorAll('.error-card');
    const count = remainingCards.length;
    
    if (count === 0) {
        // Đã sửa hết! Hiện thông báo hoàn thành
        document.getElementById("status-box").innerHTML = "Đã sửa tất cả các lỗi.";
        document.getElementById("fix-all").style.display = "none";
        currentErrors = [];
        
        // Xóa stats bar cũ và thay bằng success card
        resultBox.innerHTML = '';
        const successCard = document.createElement("div");
        successCard.className = "success-card";
        successCard.style.animation = 'fadeIn 0.3s ease';
        successCard.innerHTML = `
            <svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:24px;height:24px;margin:0 auto 6px;display:block;color:var(--success)">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            Tất cả lỗi đã được sửa thành công!
        `;
        resultBox.appendChild(successCard);
    } else {
        document.getElementById("status-box").innerHTML = `Còn <b>${count}</b> vấn đề cần sửa.`;
    }
}

// ============================================================
//  UTILITIES
// ============================================================
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function escapeAttr(str) {
    return str
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/`/g, '\\`')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}
