"""Offline Vietnamese dictionary checker using hunspell-vi word lists.

No inflection flags occur in the bundled dictionaries. Suggestions use edit
similarity plus REP substitutions, not the complete Hunspell algorithm.
"""
import re
import unicodedata
from difflib import get_close_matches
from functools import lru_cache
from pathlib import Path
from .rules import IGNORED_WORDS, match_capitalization
DATA = Path(__file__).resolve().parent / 'data' / 'hunspell'
TOKEN = re.compile(r'[^\W\d_]+', re.UNICODE)
PROTECTED = re.compile(r'https?://\S+|\b\S+@\S+\b|\b\w*\d\w*\b')

@lru_cache(maxsize=3)
def load_words(variant='both'):
    if variant not in ('both', 'old', 'new'):
        raise ValueError('hunspell_variant must be both, old or new')
    names = {'both': ('vi-DauCu', 'vi-DauMoi'), 'old': ('vi-DauCu',), 'new': ('vi-DauMoi',)}[variant]
    words = set()
    for name in names:
        lines = (DATA / (name + '.dic')).read_text(encoding='utf-8').splitlines()
        words.update(unicodedata.normalize('NFC', line.split('/')[0]).lower() for line in lines[1:] if line.strip())
    return frozenset(words)

@lru_cache(maxsize=4096)
def suggestions(word, variant):
    words = load_words(variant)
    candidates = []
    for line in (DATA / 'vi-DauMoi.aff').read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] == 'REP':
            wrong, right = parts[1:]
            start = 0
            while (pos := word.find(wrong, start)) >= 0:
                candidate = word[:pos] + right + word[pos+len(wrong):]
                if candidate in words and candidate not in candidates:
                    candidates.append(candidate)
                start = pos+1
    for candidate in get_close_matches(word, sorted(words), n=5, cutoff=0.65):
        if candidate not in candidates:
            candidates.append(candidate)
    return tuple(candidates[:5])

def check_hunspell(text, settings=None, existing_errors=()):
    settings = settings or {}
    variant = settings.get('hunspell_variant', 'both')
    words = load_words(variant)
    ignored = {unicodedata.normalize('NFC', w).lower() for w in IGNORED_WORDS}
    ignored.update(unicodedata.normalize('NFC', w).lower() for w in settings.get('hunspell_ignore_words', []))
    protected = [m.span() for m in PROTECTED.finditer(text)]
    covered = [(e['position'], e['position']+len(e['word'])) for e in existing_errors]
    errors = []
    for match in TOKEN.finditer(text):
        original = match.group()
        word = original.lower()
        if word in words or word in ignored or len(word) < 2:
            continue
        if any(match.start() < end and match.end() > start for start, end in protected+covered):
            continue
        if settings.get('hunspell_skip_uppercase', True) and original.isupper():
            continue
        choices = [match_capitalization(original, s) for s in suggestions(word, variant)]
        # No automatic deletion when no replacement is available.
        errors.append({'word': original, 'suggestion': choices[0] if choices else original,
                       'suggestions': choices, 'reason': 'Âm tiết chưa có trong từ điển hunspell-vi; hãy kiểm tra ngữ cảnh.',
                       'type': 'spelling', 'position': match.start(), 'source': 'hunspell',
                       'auto_fix': False})
    return errors
