# Integration design and validation

Goal: use VNGrammar's existing Word workflow and contextual rules with the
larger hunspell-vi syllable lists, retaining offline operation.

1. Preserve upstream source and pinned provenance.
2. Add a cached dictionary checker under `server/engine/hunspell_checker.py`.
   Load both accent styles by default; use REP and character similarity for
   suggestions; skip protected tokens and rule-covered spans.
3. Integrate into Layer 1, retain Layer 2, map NFC offsets to original input,
   and expose desktop settings. Disable bulk corrections for dictionary guesses.
4. Add regression tests and runnable CLI. Keep Windows packaging unchanged:
   the existing `--add-data engine;engine` includes the new data directory.
5. Run unittest discovery, upstream smoke script, Python compilation and JS
   syntax checks. Windows Word sideload/build and underthesea are not verified
   here. ONLYOFFICE needs a separate plugin in future work.
