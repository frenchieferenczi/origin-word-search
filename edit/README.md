# Editing this game

`index.html` is a single-file claude.ai/design bundle: fonts, React and the page runtime are
packed in a manifest, and the game itself is one JSON-encoded HTML island
(`<script type="__bundler/template">`). To change the puzzle you edit the readable copy here
and re-pack it. Everything else in `index.html` stays byte-for-byte the same.

```
 edit/template.html ──(you edit)──┐
                                  ▼
 index.html (current) ──► edit/bundle.py ──► index.html (new)
                          swaps ONLY the        │
                          template island       ▼
                                         edit/test_content.py
                                    (every week + byte-exact re-pack)
                                                │ pass
                                                ▼
                                    push to main ─► GitHub Pages ─► Google Site embed
```

## Weekly rotation

The puzzle changes by itself every Monday. `edit/template.html` holds two blocks:

- `DEFAULT`: the October PT Month puzzle, shown until the first scheduled Monday.
- `SCHEDULE`: one entry per week, each with a `start` date (a Monday, `YYYY-MM-DD`).

```
 viewer opens the page
        │
        ▼
 today (viewer's local date, or ?date=YYYY-MM-DD)
        │
        ▼
 last SCHEDULE entry with start <= today ──none yet──► DEFAULT (October)
        │
        ▼
 that week's puzzle  (after the last entry, the last week stays up)
```

Preview any week by adding `?date=2026-12-28` (any date) to the game's GitHub Pages URL (the
Google Site embed doesn't pass it through). Nothing needs to be
pushed on Mondays; one push carries all 16 weeks.

## Steps

1. Edit `edit/template.html`. Each `SCHEDULE` entry has `start`, `title`, `banner`, `done` (the
   message after all words are found) and `words` (16 entries; `word` is the grid text, max 15
   letters; `label` is the display text). To change the October puzzle, edit `DEFAULT`.
2. Re-pack: `python3 edit/bundle.py index.html edit/template.html index.html`, then copy
   `index.html` over `Pelvic Floor Word Search.html`.
3. Test: `python3 -m unittest discover -s edit -v` (must pass before pushing). It checks every
   week: 16 unique words that fit the grid, no word repeated across weeks, the grid fill places
   every word, Mondays exactly 7 days apart, and which week shows on the boundary days.
4. Push to `main`. GitHub Pages serves it and the Today at Origin Games page picks it up, no Site edit.

## Design choices and boundaries

- Only the template island is rewritten. The encoder matches the bundle's own escaping
  (`</` becomes `<\u002F`) so an unchanged template re-packs to identical bytes; the test checks this.
- The week is picked from the viewer's own clock; nothing is fetched. `?date=` only changes
  which puzzle shows, and anything that isn't `YYYY-MM-DD` is ignored.
- No data, tracking or network calls are added. The page is public, so content stays non-sensitive:
  no patient or staff names.
- `Pelvic Floor Word Search.html` is a duplicate of `index.html`. Copy `index.html` over it after
  re-packing; a test keeps the two in sync.
- Grid fill retries up to 50 times until every word is placed (the original could silently drop a
  word, leaving the puzzle impossible to finish).
