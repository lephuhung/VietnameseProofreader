"""Run the combined engine without a desktop or third-party dependencies."""
import argparse
import json
import sys
from engine.analyzer import analyze
parser = argparse.ArgumentParser(description='Kiểm tra chính tả tiếng Việt offline')
parser.add_argument('text', nargs='?', help='Văn bản; bỏ trống để đọc stdin')
parser.add_argument('--variant', choices=['both', 'old', 'new'], default='both')
parser.add_argument('--nlp', action='store_true', help='Bật underthesea nếu đã cài')
if __name__ == '__main__':
    args = parser.parse_args()
    text = args.text if args.text is not None else sys.stdin.read()
    print(json.dumps(analyze(text, {'layer2_enabled': args.nlp, 'hunspell_variant': args.variant}), ensure_ascii=False, indent=2))
