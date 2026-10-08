# Third-party sources

## VNGrammar

- https://github.com/duconmang/VNGrammar
- Imported commit: `988fb4d587888bef7efef9bd5545a520dbda2c5d`
- Upstream README declares MIT; no standalone LICENSE file in this snapshot.
- Original README retained in `docs/UPSTREAM_README.md`.
- Engine, add-in, bundled Office.js and Windows scripts originate from this source. Existing author notices are retained. Microsoft Office.js is third-party software; upstream's MIT declaration does not replace Microsoft's applicable license terms.

## hunspell-vi

- https://github.com/vohoaiviet/hunspell-vi
- Imported commit: `3b7b60992b1901867d51b90a352e7d2afbbec762`
- Authors include Hồ Ngọc Đức, László Németh, Ivan Garcia and Minh Nguyễn.
- `dictionaries/README-en.txt` identifies original word-list terms as GPLv2 and references an original Copyright file not included here.
- OpenOffice packaging notice identifies GPLv3; its English and Vietnamese notices are preserved.
- Unmodified dictionaries, aff files, provenance READMEs, packaging notices and GPLv3 text are retained under `server/engine/data/hunspell`.
- Preserve these notices on redistribution; do not describe the combined distribution as MIT-only. Clarify upstream licensing before changing its distribution terms.

## Integration changes

Changes add dictionary loading, conservative suggestions, original-text offsets,
settings, regression tests and CLI. Integration changes are offered under GPLv3;
see `server/engine/data/hunspell/COPYING`. This statement applies to our changes,
not a relicensing of third-party components.
