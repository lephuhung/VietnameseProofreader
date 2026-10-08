import sys, unittest, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from engine.analyzer import analyze
class HunspellTests(unittest.TestCase):
    def check(self, text, **settings):
        return analyze(text, {'layer2_enabled': False, **settings})['errors']
    def test_typo_positions(self):
        es = [e for e in self.check('Tôi đang ngiêên cứu và ngiêên cứu.') if e.get('source') == 'hunspell']
        self.assertEqual([e['position'] for e in es], [9, 23])
        self.assertTrue(all('nghiên' in e['suggestions'] for e in es))
    def test_valid(self):
        self.assertFalse([e for e in self.check('Tôi đang nghiên cứu tài liệu.') if e.get('source') == 'hunspell'])
    def test_disabled(self):
        self.assertFalse([e for e in self.check('ngiên', hunspell_enabled=False) if e.get('source') == 'hunspell'])
    def test_accents(self):
        self.assertFalse([e for e in self.check('hóa hoá', hunspell_variant='both') if e.get('source') == 'hunspell'])
    def test_offsets(self):
        text = '😀 ' + unicodedata.normalize('NFD', 'Tôi') + ' ngiên'
        e = next(e for e in self.check(text) if e.get('source') == 'hunspell')
        self.assertEqual(text[e['position']:e['position']+e['length']], 'ngiên')
        self.assertEqual(e['position_utf16'], e['position']+1)
    def test_rules(self):
        es = self.check('Đề nghị sử lý hồ sơ và triễn khai.')
        self.assertTrue(any('xử lý' in e['suggestion'] for e in es))
        self.assertTrue(any('triển khai' in e['suggestion'] for e in es))
        self.assertFalse(any(e.get('source') == 'hunspell' and e['word'] == 'triễn' for e in es))
    def test_technical(self):
        self.assertFalse([e for e in self.check('XYZ ABC https://example.com a@xyz.com', hunspell_ignore_words=['XYZ']) if e.get('source') == 'hunspell'])
