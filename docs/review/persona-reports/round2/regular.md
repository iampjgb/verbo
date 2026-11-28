# Verbo round 2: regular daily reader review

Branch `review-fixes`, index.html sha1 prefix 7e76489b97 (matches `VERSION` in sw.js). Tested on Chrome with Playwright. Phone 390x844 with touch was primary. Tablet 820x1180 and desktop 1366x900 were spot checks. Screenshots and scripts are in (local test folder, not in repo)  and its scripts/ folder.

## 1. Summary

- Daily reading is solid. F1 to F8 all hold on a phone. The overview is much better: 3,100 to 4,900 px per chapter, a clear Outline first, and a working "Your notes" section.
- The overview breaks the daily loop in two places. Back from a tapped item loses your scroll position. The sticky section tabs vanish under the top bar when you scroll up.
- Offline gaps are silent: cross references, Words of Jesus and Key words never load offline, even after F10 saved all five sets. Two tabs overwrite each other's highlights.
- Scores (1 to 10): ease of use 7, UI/UX 7, accessibility 6, intuitiveness 6, Chapter overview 7.

## 2. Findings

Severity: High, Medium, Low. "Confirms #n" means an open item from open-items.txt that is still present.

| ID | Sev | Area | What happened | Steps | Evidence | Concrete fix |
|---|---|---|---|---|---|---|
| R2-1 NEW | High | Overview, sticky tabs | Scrolling up shows the app top bar, and the sticky tab row sits at `top:0` behind it. The tabs disappear on every upward scroll. Same on tablet. Desktop is fine (tab row at y=56). | Phone: open Romans 8 overview, scroll down 1500 px, scroll up 300 px. Tab top = 0, top bar = 0..56. | 11-wheelup.png; tablet 40-tablet-mid.png (top bar shown, no tabs) | CSS at index.html line 1690 (`.cov-tabs`): set `top:var(--topbar-h,56px)` and add `html.tb-hidden .cov-tabs{top:0}` driven by the same class or scroll handler that hides the top bar. Or stop hiding the top bar on this page. |
| R2-2 NEW (extends #7) | High | Overview, return position | Returning from a parallel, Factbook card or a note lands at scroll 0. From a verse tap, one Back closes the verse popup and a second Back returns at scroll 0. Cross-reference peek is fine (modal; scroll stays 1308). | Scroll to Connections or Notes, tap a parallel row. Back or in-app back. Scroll 1113 -> 0. Same for Factbook chip (955 -> 0) and a "Your notes" row (2520 -> 0). | Playwright log: parallel y0=1113, after back y=0 | In `cov()` (script block, `MOUNT.chapter` wrapper near line 1857) keep `covScroll[ref]=main.scrollTop` on `pagehide`/before nav (hook `A.parOpen`, `A.covNote`, `A.covGo`, `fbChip` click), and restore in the MOUNT wrapper after build with `requestAnimationFrame(()=>main.scrollTo(0,y))`. Accordion state already survives, so reuse the same module-level Map. |
| R2-3 NEW | Medium | Overview, in-app back | After tapping a People chip, the in-app back arrow goes to the People A-Z list the user never saw. A second tap reaches the overview. Browser Back goes straight to the overview. The two disagree. A note row also goes overview -> note editor -> Notes list -> overview. | Overview Romans 8 > Jesus Christ chip > top-left back arrow. | 17-fb-card.png, 18-fb-back1.png | In the `bkBack` handler, when the previous history entry is the overview, call `history.back()` instead of pushing a parent page. For `A.covNote` (line ~1769) open the note with `ui.noteId` set and `ui.back='chapter'` so the arrow returns to the overview. |
| R2-4 NEW | Medium | Overview, book edges | Prev and Next stop at book ends. Matthew 28 has no "Mark 1". Matthew 1 has no "Malachi 4". Single-chapter books show no row at all. The reader moves across books (F5), so this is inconsistent. | `A.chOv` on Matthew 28, Matthew 1, Obadiah 1. | `.cov-pn` count 1, 1 and 0 | In `cov()` build `prev`/`next` from BOOKS order using `bookOrder`, not from the original `.wk-pn` buttons. Label with the book name, for example "Mark 1". |
| R2-5 NEW | Medium | Overview, offline | Offline after F10 completes, the overview still loses: Cross references (the XREF files are in no pack, so the block is silently absent), "Words of Jesus" (`red.json` is in no pack, confirms #30), and Key words on first open (shimmer, no error, confirms #11 for this page). Outline vanishes with no hint when the Matthew Henry set is not saved. Matthew Henry shows a clear message but also offers a "Read full commentary, a few MB" button that cannot work offline. | Fresh context, wait 66 s for auto-save, `set_offline(True)`, reload, open Acts 13 overview, open Key words and Matthew Henry. Cross references absent. | 31-offline-words.png, 34-offline-full.png; `offline-packs.json` has no xref file | Add `bible/xref/*` and `fact/red.json` to the `places` pack in offline-packs.json. In `covConnections`, when `bookFailed("XREF",book)` show a one-line "Cross references need a connection". Add a timeout and "Could not load. Retry." to Key words. Hide the "full commentary" button when `!navigator.onLine`. |
| R2-6 NEW | Medium | F10 messages | After all five sets are saved (66 s on localhost, "done"), Account > Offline library still says "Partly saved 9%, 66 of 732 files". F10 auto-saves study sets but not the Bible texts, so a commuter sees a job that looks unfinished and has no hint that "Download now" is a different download. Remove (Settings) has no confirm or undo and is 36 px tall. The toast says "Keep using the app" but sits mid-screen over text and verse sheets for several seconds. | Wait for auto-save, Account > Offline library. Settings > Offline > Remove on Matthew Henry. | 35-account-menu.png, 36-offline-library.png, 38 (no dialog) | Rename the card "Bible texts" and say study sets are separate, or fold both into one "Offline" card. Add an undo toast on Remove (`toast(..., {undo})`). Put the toast at the top or bottom edge above the nav (`#toast` CSS). Make `.pack-row` buttons 44 px. |
| R2-7 NEW | High | Data, two tabs | Last writer wins. Tab 2 adds a highlight, tab 1 (unaware, no `storage` listener) then adds its own and saves its whole state. A fresh tab shows only tab 1's data. Tab 2's highlight is lost. Tab 1's overview never updates either. | Two pages in one context. Tab 2: highlight 8:10. Tab 1: highlight 8:20. Open a third page: has 8:20, not 8:10. | Playwright: third page sees `['Romans 8:1','Romans 8:5','Romans 8:28','Romans 8:20']`. `grep` finds 0 `addEventListener("storage"`. | In `save()`, re-read `localStorage` first and merge by key (highlights, bookmarks, notes by id with newest `t`), or add `addEventListener("storage",e=>{if(e.key==="biblestudy.v1"){reload S; refresh()}})` so each tab adopts the other's change before saving. |
| R2-8 NEW | Medium | Overview, Setting map | Matthew 26 mini map: Bethany, Gethsemane and Mount of Olives labels print on top of each other into a smudge. Galilee sits under Nazareth and is hidden. The "Open the chapter map" pill covers part of the map. The Last Supper chapter shows Nazareth prominently. | Open Matthew 26 overview > Setting > Map. | 22-mt26-map.png | In `atlasSVG({focus:geo,mini:!0})` skip labels for places within about 24 px of an already labelled one, label only the top 3 by verse count, and drop the pill to a corner icon. Exclude places only named as an epithet ("Jesus of Nazareth"). |
| R2-9 NEW | Low | Overview, Events | The note says "Dates are traditional dates and approximate", but Matthew 26 rows show no dates at all. Acts 13 shows two near duplicate rows ("First missionary journey begins" and "First Missionary Journey"). | Matthew 26 and Acts 13 > Setting > Events. | 21-mt26-set1.png, 30-offline-acts13.png | Show the note only if at least one row has a year (`.cov-ev .fb-yr:not(:empty)`). De-duplicate events by lowercase name in `covSetting`. |
| R2-10 NEW | Low | Overview, polish | (a) "Show all 6" is centered, "Show all 9" is left-aligned. (b) Words accordions are boxed rounded cards, Commentary accordions are flat divider rows, so two styles sit side by side. (c) Accordion labels repeat the heading ("Commentary > Commentary · Matthew Henry"). (d) Sources text appears twice: under Commentary and in Sources. (e) Your notes rows are grouped highlights, bookmarks, notes, not in verse order; the bookmark and note icons touch "v. 15" while highlight dots have a gap; highlight dots are pale. (f) Accordion open state and "Show all" are kept in memory only and keyed by label, so they carry across chapters and reset on reload. | See screenshots. | 10-ov-s03.png, 10-ov-s04.png, 21-mt26-set2.png | CSS near line 1700: one `.cov-morebtn` alignment; apply the `.cov details.cov-q` style to `#cov-words`; strip "Commentary · " in the summary text; remove the source note under `#wk-com`; sort `rows` in `covMine` by verse number; give `.cov-vr svg` `margin-right:6px`; save `covOpen` to `localStorage` if wanted. |
| R2-11 NEW | Low | Reader sheet | On phone, with a verse selected low in the chapter, the study sheet (note box) covers the selected verse. Verse 31 was hidden behind the sheet while writing a note. The colour row in the sheet has no names, and "Share" is clipped at the right edge. | Select v31, Note. | 07-note-typed.png, 05-hl-sheet.png | After `stOpen`, scroll the selected `span.v` to the top quarter of the visible area (`scrollIntoView({block:"start"})` plus `scroll-margin-top`) on phones. |
| R2-12 | Low | Part A verdict | "Your notes" works: it shows 3 highlights, 1 bookmark, 1 note with correct counts. Highlight and bookmark rows open the correct verse (v28 selected). The note row opens the correct note. Removing a highlight in the reader updates the overview count (3 to 2) and rows. Rows for highlights show the verse text, the note row shows the note text (no verse text). | Described in text. | 12-tab-notes.png | Optional: show the verse reference and a faint verse snippet for the note row too. |

### F1 to F8 on phone (Part B)

| Fix | Result |
|---|---|
| F1 popup Save | Pass. `S.bookmarks` = `{ref:"Romans 8:15"}`. Overview and bookmarks load. |
| F2 popup Highlight and Note | Pass. The sheet opens with swatches or a focused `#qnText`. Gold, blue, green saved. Note saved. See R2-11 for the sheet covering the verse. |
| F3 verse text for screen readers | Pass in code (`span.v` has no `aria-label`). Not tested with a real screen reader. |
| F4 Strong's G25 | Pass. "Word study G25" opens the Bible words page. The result list still shows unrelated Hebrew (H775, H2977G): confirms #23. |
| F5 chapter ends | Pass. Toasts "This is the last chapter of the Bible." and "This is the first chapter of the Bible." |
| F6 dialog focus | Pass. The dialog is named "Translation", focus moves in and returns to the pill. Tab still escapes the dialog (7 of 30 Tab presses left it): confirms #4. |
| F7 welcome | Pass. Text says "Tap Bible at the bottom". Escape sets `verbo.welcomed`, no repeat after reload. |
| F8 comic back | Pass. Empty comic page shows "Read Romans 8 as text". It returned to text with 39 verses. |
| Update banner | Pass by code. `VERSION` in sw.js is "7e76489b97", which equals the first 10 chars of the sha1 of index.html. Any later edit to index.html needs a new bump. I did not re-run the banner simulation. |

### Part C: open items a daily user meets

| Item | Still present? | Severity | Concrete fix |
|---|---|---|---|
| 4 | Yes. Tab leaves the dialog (7/30). Focus after verse select not retested. | Medium | In `modal()` add a keydown trap (Tab and Shift+Tab wrap inside `#modal`) and set `inert` on `#main` and the nav while `#modalBg.show`. |
| 7 | Yes. Hash is always `#reader`. After reload the chapter returns (John 3) but the verse selection and scroll are lost (scroll 0). Back to the first entry leaves the old page on screen. | High | Save `S.reading.v` and `scrollTop` on `pagehide` and restore in `MOUNT.reader`. Write `#reader=John.3.16` with `replaceState` and handle it in `fromHash`. |
| 10 | Yes. "Jhon 3:16" gives "No book matches" and shows the old picker. Enter does nothing. | Medium | In `pkQ` input handler add fuzzy match (Levenshtein 1 to 2 on book names and abbreviations) and make Enter pick the first match or the typed chapter. |
| 11 | Yes for the Key words spinner and the "Read full commentary" offer offline (see R2-5). Unsaved WEB text offline not retested. | Medium | See R2-5. |
| 14 | Yes. Swatches 34 px, Highlight and Remove buttons 36 to 40 px, Settings Remove 36 px. | Medium | `min-width/height:44px` on `[data-action=hl]`, `.pack-row button`, `[data-action=hlToggle]`. |
| 15 | Partly. Pills fixed. Not rechecked: `#tabstrip`, nameless plan checkboxes. | Low | As in the open item. |
| 16 | Yes. Colours have no names in the sheet. The popup still says "Save" for a bookmarked verse. A bookmark marker svg exists in the verse markup, visibility unconfirmed. | Medium | In `placePop` show "Saved" with a filled icon when `S.bookmarks` has the ref. Add `title` and `aria-label` ("Gold") to swatches. |
| 20 | Not tested. | n/a | Skipped. |
| 23 | Yes (G25 list shows H775 and H2977G). | Low | In the strong search, match only the same prefix letter when the query starts with G or H. |
| 25 | Yes. The boxed "1" tab count is visible on every page. | Low | Hide the count when only one tab is open. |
| 30 | Yes. `red.json` and XREF are in no pack. | Medium | See R2-5. |

Skipped (not tested, or not met in daily use): 6, 8 (fixed part only), 12, 13, 17, 18, 19, 21, 22, 24, 26, 27, 28, 29. Item 13 (floating play pill) and 19 (multi-select) were not exercised. Items 12, 17, 21, 22, 24 and 29 need special setups I did not run.

## 3. Top 5 to fix next (daily users)

1. R2-2 and R2-3: keep the overview scroll position on return, and make in-app back match browser Back.
2. R2-1: sticky section tabs are hidden under the top bar on any upward scroll (phone and tablet).
3. R2-7: two tabs or windows overwrite each other's highlights, bookmarks and notes (data loss).
4. R2-5 and R2-6: offline gaps (cross references, Words of Jesus, Key words) and the misleading "Offline library 9%".
5. #10: search and picker dead-end on typos and Enter (confirmed again).

## 4. What works well

- The overview order is right for daily use: Outline first, each row jumps straight to the verse with no popup, sections empty out cleanly (no empty headings on Obadiah, Psalms 119, 3 John, Nahum 2).
- Type hierarchy is clear: Lora title and section headings, 16 px body, grey 13 px meta. First screen is compact. Light touch of dividers instead of boxes.
- "Your notes" is accurate and live. Counts are right, tap targets are 44 px tall, and highlight, bookmark and note rows open the right verse or note. Removing a highlight updates it.
- Tabs scroll to the section and leave the heading visible. Rapid Prev and Next taps (10 in a row) never left a stale or doubled page. No page errors in any run.
- Cross reference rows show a one-line verse preview, and the peek opens as a modal without losing scroll.
- Open accordions stay open across re-render and chapter changes.
- F10 behaves as written. Five sets saved in about 66 s with one toast, and a removed set (`verbo.packsRemoved = ["mh"]`) stayed removed after reload and 30 s of waiting. Offline, the Setting, Connections (parallels), Key words, Matthew Henry and Calvin all loaded once saved.
- Offline text for an unvisited chapter (Jeremiah 10 KJV) opened offline.
- Clear offline message for Matthew Henry that points to Settings.
