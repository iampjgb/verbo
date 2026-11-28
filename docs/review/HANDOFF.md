# Handoff: instructions for the next Claude session

This branch (`review-fixes`) was made by a Claude session on another account on 2026-11-28. Zee asked for it so that his main Claude account can pick up the work. Read this file first.

## What is on this branch

1. `docs/review/REVIEW.md`: the merged UX and accessibility review. It has 30 issues, each with a status (FIXED, PARTIAL, OPEN).
2. `docs/review/persona-reports/`: the three raw reports (beginner, regular, advanced). Paths in them point to a test machine that no longer exists.
3. `docs/review/FIXES.md`: every code change as exact BEFORE and AFTER text, with test results.
4. `docs/review/screenshots/`: before and after evidence for the main bugs.
5. `docs/review/tests/`: Playwright scripts that check each fix.
6. `index.html`: fixes F1 to F14, in separate commits. F9 is the Chapter overview redesign and F10 saves study sets by default. F11 turns the overview into a chapter deep dive. F12 fixes round 2 items 36 to 40 (speed, no jumping, sticky tabs, Back, map) and 37 (two tabs). F13 fixes items 41 and 43 to 47 (offline, prev/next, wording, study-tools bar, outline, credits). F14 fixes items 4, 10, 13, 14 and part of 42. Both were asked for by Zee. F8 (comic mode dead end) came from Zee's own iPhone test of the preview.

Base commit: `2922233` on `main`. Nothing on `main` was changed. The live GitHub Pages site is untouched until this branch is merged.

## How to apply it

**Case A. `main` has not changed since `2922233`.** Merge the pull request for this branch, or run:

```
git fetch origin review-fixes
git checkout main
git merge --no-ff origin/review-fixes
```

**Case B. `main` has new commits that touch `index.html`.** `index.html` is a single minified file, so a git merge will likely conflict on one long line. Do not resolve that by hand. Instead:

1. Take `main` as it is.
2. Copy `docs/review/` from this branch: `git checkout origin/review-fixes -- docs/review`.
3. Open `docs/review/FIXES.md` and apply each BEFORE to AFTER replacement to the current `index.html` with a script. Assert that each BEFORE string is found exactly once (the book pill has a different expected count, listed in FIXES.md). If a BEFORE string is missing, find the same code by its function name (`bm(e)`, `strongBlock`, `adjChapter`, `modal(`, `WELCOME2`) and adapt it.
4. Add the `<script id="verbo-review-fixes-2026-11-28">` block from FIXES.md just before `</body>`. Check that `A.hlToggle`, `A.noteModal`, `A.stOpen`, `S`, `ui` and `save` still exist under those names.
5. Run the tests (below). Then commit.

## How to test

```
python3 -m http.server 8110        # in the repo root
npm i axe-core@4                   # in docs/review/tests
pip install playwright && playwright install chromium
cd docs/review/tests
python3 test_fixes.py http://localhost:8110/
python3 test_strongs.py
python3 test_comic_escape.py
python3 test_chapter_overview.py "Romans|8"
python3 test_chapter_overview_states.py   # Meaning hidden / button / written
python3 test_overview_cold_load.py
python3 test_chapter_deep_dive.py
python3 test_f12_speed_place_tabs.py
python3 test_f12_no_jump.py
python3 test_f13_batch3.py
python3 test_f13_offline.py
python3 test_f14_medium.py
python3 test_f14_connections.py
python3 test_study_sets_default.py         # takes about a minute
```

Expected: every line in the FIXES.md test table passes, `page_errors => []`, and axe on the reader shows only `aria-required-children` (issue 15, still open).

## Suggested next work

Pick from the OPEN items in REVIEW.md in this order:
1. Finish the accessibility work: issue 4 (Tab trap, `inert`, focus into the panel after a verse is selected), then 14, 15, 16 and 17.
2. Issue 7 (deep links and keeping your place). It touches routing, so plan it first.
3. Issues 13, 10 and 11.
4. Issue 6 (parallel alignment). It needs a verse offset map for DRC Psalms. It is the largest change, so do it on its own branch.

Ask Zee before starting the larger items (6 and 7). They change how the app behaves, not only how it looks.

## Notes

- AI features (Ask AI, cloud sync) only work inside Claude. The reviewers did not count them as broken.
- `sw.js` `VERSION` was bumped on this branch so the update banner shows. In Case B, set `VERSION` to a new value again after reapplying the fixes (for example the first 10 characters of `sha1sum index.html`).
- `offline-packs.json` changed in F13 (cross references and red letters added to the "dict" set).
- Zee's writing style for any user-facing copy: short declarative sentences, plain words, no em-dashes.

## Preview

The branch can be previewed without deploying at https://raw.githack.com/iampjgb/verbo/review-fixes/index.html (tap "Open the page" on the first screen). It uses a different origin from the live site, so saved data does not carry over.
