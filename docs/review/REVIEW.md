# Verbo UX and Accessibility Review (2026-11-28)

Baseline review of commit `2922233`. Three reviewer agents (Sonnet 5.5) each played one type of user. They ran the live app in headless Chrome, took screenshots, and ran axe-core. They also tested keyboard-only use, dark mode, offline mode and 200% zoom. An Opus session merged the 63 raw findings into the 30 issues below. Issue 31 was added later from Zee's own phone test and checked the serious ones against the code.

- **Beginner:** first-time Bible app user, phone. See `persona-reports/beginner.md` (B1 to B23).
- **Regular:** daily reader, phone and tablet. See `persona-reports/regular.md` (R1 to R20).
- **Advanced:** pastor or seminary student, desktop. See `persona-reports/advanced.md` (A1 to A20).

Not tested: a real phone, a real screen reader, the native share sheet and the install prompt.

**Status key:** FIXED = fixed on branch `review-fixes` (see FIXES.md). PARTIAL = part of it fixed. OPEN = not fixed yet.

## Scores (1 to 10)

| Area | Beginner | Regular | Advanced |
|---|---|---|---|
| Ease of use | 8 | 6 | 7 |
| UI/UX | 7.5 | 7 | 8 |
| Accessibility | 5.5 | 5 | 4 |
| Intuitiveness | 7 | 5 | 6 |
| Study-tool depth | n/a | n/a | 7 |

## Critical and high

| # | Status | Issue | Source | Suggested fix |
|---|---|---|---|---|
| 1 | FIXED (F1) | Phone popup Save stores a bookmark with no reference ("Bookmarked undefined"). After that, the Bookmarks page crashes, even after a reload. | R1 | `bm()` reads `data-key` or `data-ref`. Bad bookmarks are dropped on load. |
| 2 | FIXED (F2) | Phone popup Highlight and Note do nothing visible. Their UI is in `.panel`, which is hidden while `#vpop` shows. | R2, R3 | They now open the study sheet with the tool ready. |
| 3 | FIXED (F3) | Screen readers hear "Verse N" and never the verse text. | B1, R4, A6 | `aria-label` removed from verses. |
| 4 | PARTIAL (F6) | Dialogs do not take focus, trap Tab or have a name. Focus drops to the body after a verse is selected, and the study panel cannot be reached by Tab. | R5, R6, A3, A5, B8, B21 | Done: name, focus in, focus back on close. Open: trap Tab, `inert` on `#app`, focus into the panel after a verse is selected. |
| 5 | FIXED (F4) | Strong's search fails for every number under 1000 (G25, H430). The keys are zero-padded. | A1 | Pad to 4 digits before lookup. |
| 6 | OPEN | The parallel view misaligns 65 DRC Psalms (superscription counted as v1). It hides extra verses (Ps 51 DRC v20 and v21, WEB Rom 14:24-26). Moved verses are labelled "not in this translation". | A2, A7 | Per-version offset map for Psalm titles. Add rows for verses only in the compare version. Separate wording for "moved" and "absent", with a link. |
| 35 | FIXED (F11) | Chapter overview lacks the app's own parallels, Factbook, maps, journeys, cross references and the reader's own notes. | Zee | Setting, Connections, Words and topics and Your notes sections, hidden when empty. |
| 34 | FIXED (F10) | Study sets must be saved by hand, so offline study tools are missing until the user finds Settings. | Zee | All sets save automatically in the background; removed sets stay removed. |
| 33 | FIXED (F9) | Chapter overview data (commentary, key words, dictionary, people) never loads on a fresh visit. The loaders only redraw the reader and verse study. Existed before this branch. | Zee | Loaders now redraw the Chapter overview too. |
| 32 | FIXED (F9) | Chapter overview is a long article: 4 navigation rows, facts repeated 3 times, the outline buried, commentary fully open, "jewish" lowercased. About 11 phone screens. | Zee | Phone-first layout with At a glance, outline on top, closed sections and a section tab row. Interpretation only after "Write a study with Claude". Four-level type scale. Now about 3 screens. |
| 31 | FIXED (F8) | Comic mode is a dead end on phones. The Read/Study/Comic switcher is hidden, the comic version popover has no "Back to text", and More only appears after a comic exists. Outside Claude no comic can be made, so the user is stuck. Found by Zee on an iPhone after the persona reviews. | Zee | "Back to text" on the empty comic page and in the comic version popover. Open: bring back the mode switcher on phones. |
| 7 | OPEN | The app does not keep your place. The hash is rewritten to `#reader`, so reload, Back and links lose the chapter and verse. Scroll is lost. "Continue reading" is unreliable. Ranges are ignored. | A4, B15, R8, B23 | Write `#Book.Ch.V-V&tr=` with `replaceState` (scroll) and `pushState` (chapter or panel). Save the top visible verse. Always show Continue on Today. |

## Medium

| # | Status | Issue | Source | Suggested fix |
|---|---|---|---|---|
| 8 | PARTIAL (F7) | The welcome says "Tap Read at the bottom", but the tab is "Bible" and desktop has a sidebar. Escape does not mark the welcome as seen. The tour says "bookmark" and the menu says "Save". | B2, B14, B19, A17 | Done: device-aware wording, Escape fix. Open: one word for Save/Bookmark, and the Help text. |
| 9 | FIXED (F5) | Next and Previous fail silently at Genesis 1 and Revelation 22. | B4 | Toast added. Optional: disable the chevron as well. |
| 10 | OPEN | "Jhon 3:16" and "Mathew 5" dead-end. Enter in the picker does nothing. One letter plus Enter opens Ask AI. Verse results are in book order. | B5, B17, R12 | Fuzzy book names with "Did you mean". Enter opens the first match. Hide Go-to items under 2 characters. Rank by relevance. |
| 11 | OPEN | Offline, an unsaved WEB chapter shows KJV text under the WEB label. Error text says "published app" and "sample passages". "Marked as read" fires on failure. The Words tab spins forever. | R10, B6, A12 | Never show another version's text under the chosen label. Use plain error text. Skip mark-as-read on failure. Add saved badges in the version picker. |
| 12 | OPEN | When storage is full, saves fail silently and the UI still says "Highlighted". | R7 | Lasting warning plus Export. |
| 13 | OPEN | The floating prev/play/next pill covers text and is icon-only. Mid-chapter there is no next-chapter control. | B9, R18, A11 | Dock it, or show it only during audio. Add "Next: John 4" at the end of each chapter. |
| 14 | OPEN | Tap targets of 36 to 41px. Highlight swatches are 22px, and some links are 16px tall. | B10, R14, A17 | Minimum 44x44, using padding. |
| 15 | PARTIAL (F6) | Pill names differ from their visible text. `#tabstrip` fails `aria-required-children` (critical). There is an unlabelled Settings select, nameless plan-day checkboxes, a nested control on the map and an unnamed `#gsPop`. | B7, B8, A6, R16 | Done: pills, `#gsPop`. Open: tabstrip roles, the select, plan checkboxes, the map. |
| 16 | OPEN | Highlight meaning is colour-only. A bookmarked verse has no marker, and the popup always says "Save". | R13, R15 | Colour name in the accessible name. A ribbon and a "Saved" state. |
| 17 | OPEN | At about 200% zoom the book pill becomes "R" (simulated). The verse panel tab row is cut off. | B11, A11 | Ellipsis on the pills, overflow into the menu, fade or arrow on the tab row. |
| 18 | OPEN | New users land in Romans 8. The desktop verse panel opens on grammar codes. EN/TL changes only the verse of the day. | B3, B12, B13 | Start at John 1. Open the panel on "At a glance". Add language and search steps to the welcome. |
| 19 | OPEN | Multi-verse select is 3 taps deep. | R9 | Add "Select more" to the popup. |
| 20 | OPEN | Theme follows the OS only on first run. There is no Auto option. | R11 | Add Auto as the default. |
| 21 | OPEN | Genesis 51 drops the user on Today. John 3:99 opens a panel for a verse that does not exist. DRC says "Catholic" but has no deuterocanon. | A8, A9 | Nearest valid chapter with a reason. Reject verses past the end. Label DRC "66 books, Hebrew psalm numbers". |
| 22 | OPEN | Calvin (CCEL, Beveridge) and the CrossWire red letters are not credited in the app. Help lists 3 Bibles and says "prototype". Ctrl+C copies with no reference. | A13 | A Sources and licences page that mirrors the README. Add the reference and version to copied text. |
| 23 | OPEN | Lexicon text is one run-on block. Suffixes like H7225G are not explained. A G25 search lists unrelated Hebrew entries. | A14 | One sense per line, a suffix key, exact G/H matching. |
| 24 | OPEN | Shortcuts are undocumented (j/k, ?). Ctrl+T and Ctrl+W clash with the browser. There is no "/". | A10 | A Shortcuts page, "/" for search, replace the reserved keys. |

## Low

| # | Status | Issue | Source | Suggested fix |
|---|---|---|---|---|
| 25 | OPEN | The boxed "1" tab count looks like a notification. Desktop initials are hard-coded "DR". | B20, R17 | Tabs icon, hide at 1 tab, real initials. |
| 26 | OPEN | Chapters and plan days are marked read about 2 seconds after a jump to the end. | A16, R19 | Require reading time or a user scroll. |
| 27 | OPEN | The first tap on a verse highlighted by a jump clears it. The bottom nav is off-screen after the jump. | B16, B18 | Clear `ui.sel` after the jump. Keep the nav visible briefly. |
| 28 | OPEN | Hyphenation splits Bible words. The footnote label says WEB only. The era "United Kingdom" reads as the UK. | A15, A18 | Hyphenation off for scripture. Fix the label. Use "United Monarchy". |
| 29 | OPEN | The dark-mode verse number in the Aa preview has 3.26:1 contrast. A new note saves an empty `<h2>`. | B22, R20 | Lighter colour. Strip empty blocks. |
| 30 | OPEN | The first visit prefetches about 6 MB of KJV. `red.json` is in no offline pack. The iPhone widget ignores data-hashes.json. | A19, A20 | Defer on metered connections. Add `red.json` to a pack. Hash check in the widget. |

## Suggested order for the open items

1. Issue 4 (rest) and issues 14, 15, 16 and 17: finish the accessibility pass, then test with VoiceOver or TalkBack.
2. Issues 7, 13, 8 (rest) and 10: place, navigation and search.
3. Issues 6, 11, 12, 21 and 22: trust and data.
4. The rest.

## What works well

- **Speed:** first verse in 1.6 s, chapter switch 23 to 73 ms, Psalm 119 scrolls at 61 fps, search 0.2 to 0.6 s.
- **Search:** it accepts "jn 3 16", "Ps23" and "1 cor 13". It searches Tagalog, quoted phrases, and Greek and Hebrew.
- **Versions:** switching keeps your place, and missing verses such as Acts 8:37 in BSB are explained.
- **Study tools:** the interlinear has correct `lang` and right-to-left tags. The lexicon shows usage counts. Commentaries come with size warnings. Share copies a full citation.
- **Notes:** they escape HTML, handle 5,000 characters, and survive a reload and two open tabs.
- **Offline:** the shell, KJV and search work. An interrupted pack download resumes. data-hashes.json matches all 408 files.
- **Comfort:** dark mode passes axe contrast, text size goes to 32px, and reading plans work well.
