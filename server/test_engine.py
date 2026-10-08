"""Quick test cho Hybrid Engine v2 (có Layer 2 Disambiguation)"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.analyzer import analyze
import json

# Các câu test — tập trung vào ngữ cảnh
test_cases = [
    # Test 1: "ok" sau động từ → nên gợi ý "ổn thỏa"
    ("Dự án này dc triễn khai ok", "Layer 2 sẽ refine 'ok' → 'ổn thỏa' (sau động từ)"),
    
    # Test 2: nhiều loại lỗi khác nhau 
    ("Vô hình chung anh ấy đã sáng tạo ra một giải pháp rất tuyệt vời cho cơ chế chính sánh mới",
     "Nhiều loại: spelling + redundancy + context"),
    
    # Test 3: phương ngữ
    ("Bữa hổm tui dề nhà rồi nha, hổng có j đâu",
     "Phương ngữ + viết tắt"),
    
    # Test 4: câu chuẩn
    ("Văn bản này hoàn toàn chuẩn chỉnh về mặt chính tả và ngữ pháp.",
     "Câu chuẩn, không có lỗi"),
    
    # Test 5: lỗi chấm câu
    ("Hôm nay trời đẹp,chúng tôi đi chơi .Thật vui",
     "Lỗi chấm câu: thiếu cách sau phẩy, thừa cách trước chấm"),
]

print("=" * 70)
print("  HYBRID ENGINE v2 TEST (Layer 2 Disambiguation)")
print("=" * 70)

for i, (text, description) in enumerate(test_cases, 1):
    print(f"\n{'─' * 70}")
    print(f"  Test {i}: {description}")
    print(f"  Input: \"{text}\"")
    print(f"{'─' * 70}")
    
    result = analyze(text)
    stats = result['stats']
    
    print(f"  ⏱  L1={stats.get('layer1_time_ms',0)}ms ({stats.get('layer1_errors',0)} lỗi) | "
          f"L2={stats.get('layer2_time_ms',0)}ms ({stats.get('layer2_errors',0)} lỗi) | "
          f"NLP={'ON' if stats.get('layer2_available') else 'OFF'}")
    
    if result['errors']:
        for err in result['errors']:
            label = err.get('label', '?')
            color = err.get('color', '')
            ai_mark = " 🤖" if err.get('reason', '').startswith('[AI') else ""
            print(f"  [{label}] \"{err['word']}\" → \"{err['suggestion']}\"{ai_mark}")
            print(f"         {err['reason']}")
    else:
        print(f"  ✅ Không tìm thấy lỗi.")

print(f"\n{'=' * 70}")
print("  TEST HOÀN TẤT")
print(f"{'=' * 70}")
