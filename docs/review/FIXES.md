# Fixes applied on branch `review-fixes` (2026-11-28)

All changes are in `index.html`. Every change is an exact text replacement, plus one new `<script>` block added just before `</body>`. If `index.html` has changed on `main` since commit `2922233`, reapply each fix by searching for the BEFORE text. Each BEFORE string appears exactly once unless a count is given.

Test results are at the bottom. Re-run the tests with `docs/review/tests/test_fixes.py` (see HANDOFF.md).

---

## F1. Phone popup Save made a corrupt bookmark (review issue 1, Critical)

**Cause.** The phone verse popup (`#vpop`, built in `placePop`) puts the verse in `data-ref`. `A.bm()` reads only `e.dataset.key`, so it saved `{t:...}` with no `ref`. After that, the Bookmarks page crashed on `undefined.replace`.

BEFORE
```js
bm(e){const t=e.dataset.key;
```
AFTER
```js
bm(e){const t=e.dataset.key||e.dataset.ref;if(!t)return;
```

**Cleanup for users who already hit the bug.** This is in the new script block (see below). On load it drops bookmarks with no `ref`, then saves.

## F2. Phone popup Highlight and Note did nothing (review issue 2, High)

**Cause.** `hlToggle` and `noteModal` open their UI inside `.panel`. On phones, the CSS rule `@media (max-width:899px){html.vpop-on .panel{display:none!important}}` hides that panel while the popup is open.

**Fix.** This is in the new script block. When the popup is open, Highlight sets `ui.hlOpen=true` and Note sets `ui.qnOpen=true`. Both then call `A.stOpen()`, which closes the popup and opens the study sheet with the colour row or note box ready. Note also focuses `#qnText`. Desktop behaviour does not change.

## F3. Screen readers did not read the verse text (review issue 3, High)

BEFORE (inside the verse template, single-version reader)
```js
 aria-label="Verse ${D}"
```
AFTER: removed (empty string). The verse name now comes from its own text. It starts with the verse number in `<sup>`.

## F4. Strong's search failed for numbers under 1000 (review issue 5, High)

**Cause.** The concordance keys in `bible/ilx/conc/*.json` are zero-padded (`G0025`). The lookup used the typed key (`G25`).

BEFORE
```js
function strongBlock(key,q){const refs=conc[key];
```
AFTER
```js
function strongBlock(key,q){/^[GH]\d{1,3}$/.test(key)&&(key=key[0]+key.slice(1).padStart(4,"0"));const refs=conc[key];
```
After the fix, G25 gives 110 verses (this matches the word popup), H430 gives 2248 and H1 gives 1060.

Still open (not fixed here): a G25 search also lists unrelated Hebrew entries. See review issue 23.

## F5. Next and Previous failed silently at Genesis 1 and Revelation 22 (review issue 9)

BEFORE
```js
if(n<1){if(a===0)return;
```
AFTER
```js
if(n<1){if(a===0)return toast("This is the first chapter of the Bible.");
```
BEFORE
```js
if(a===BOOKS.length-1)return;
```
AFTER
```js
if(a===BOOKS.length-1)return toast("This is the last chapter of the Bible.");
```

## F6. Accessible names and dialog focus (part of review issues 4 and 15)

Book pill. The name now starts with the visible text (Voice Control can then match "Romans 8"). There are 2 occurrences with `e` and 1 with `a`.

BEFORE
```js
aria-label="Choose book and chapter">${esc(e.book)} ${e.ch}
```
AFTER
```js
aria-label="${esc(e.book)} ${e.ch}, choose book and chapter">${esc(e.book)} ${e.ch}
```
(The same change applies to `${esc(a.book)} ${a.ch}`.)

Translation pill. The visible text ("KJV") is now its name, and the old label became a tooltip.

BEFORE `data-action="trOpen" aria-label="Choose translation">`
AFTER `data-action="trOpen" title="Choose translation">`

Dialogs. The dialog gets a name from its title, focus moves into it, and focus returns to the button that opened it on close.

BEFORE
```js
function modal(e,t,a){$("#modal").classList.remove("sheet"),
```
AFTER
```js
let modalRet=null;function modal(e,t,a){$("#modalBg").classList.contains("show")||(modalRet=document.activeElement),$("#modal").setAttribute("aria-label",String(e||"Dialog").replace(/<[^>]*>/g,"").trim()||"Dialog"),$("#modal").classList.remove("sheet"),
```
BEFORE
```js
setTimeout(()=>{const s=$("#modal input,#modal textarea");s&&s.focus()},30)}function closeModal(){$("#modalBg").classList.remove("show")}
```
AFTER
```js
setTimeout(()=>{const s=$("#modal input,#modal textarea")||$("#modal button,#modal [href],#modal [tabindex]");s&&s.focus()},30)}function closeModal(){$("#modalBg").classList.remove("show");const r=modalRet;modalRet=null;r&&r.isConnected&&r.focus&&setTimeout(()=>r.focus(),0)}
```

Search popup name:

BEFORE `<div class="gs-pop" id="gsPop" role="listbox"></div>`
AFTER `<div class="gs-pop" id="gsPop" role="listbox" aria-label="Search suggestions"></div>`

Still open (not fixed here): the Tab trap inside dialogs, `inert` on the page behind, focus after a verse is selected (review issue 4), and `#tabstrip` roles (review issue 15).

## F7. Welcome copy and Escape (review issue 8)

BEFORE
```js
"Tap <b>Read</b> at the bottom, then the book name at the top to pick any book and chapter."
```
AFTER
```js
(innerWidth<900?"Tap <b>Bible</b> at the bottom":"Click <b>Bible</b> on the left")+", then the book name at the top to pick any book and chapter."
```
Escape on the welcome sheet now saves `verbo.welcomed`, so it does not come back on every reload. This is in the new script block.

## F8. Comic mode had no way back to the text on phones (review issue 31, High)

Found by Zee on an iPhone while testing the preview (`screenshots/before/F8-comic-dead-end-iphone.png`).

**Cause.** On phones the Read/Study/Comic switcher (`.rmodes`) is hidden by an injected style (`.rmodes{display:none!important}`). "Back to text" exists only in the translation sheet (`A.trOpen`) and the reader More sheet (`A.readerMore`). In comic mode the version pill opens a different popover (`cmTrPop`), and the More button appears only after a comic exists. Outside Claude no comic can be made, so the user is stuck. Prev and Next also stay in comic mode. A verse popup (`#vpop`) from a deep link could also stay open on top of the comic page.

**Fix.** Added to the script block:

```js
  /* F8: comic mode had no way back to the text on phones. Add "Back to text" to the comic version sheet and to the empty comic page */
  A.cmBackText=()=>{typeof closePop=="function"&&closePop(),A.trMode({dataset:{v:"read"}})};
  const _cto=A.cmTrOpen;_cto&&(A.cmTrOpen=function(){const r=_cto.apply(this,arguments);try{const b=document.getElementById("pop");b&&!b.querySelector(".cm-back-mi")&&b.insertAdjacentHTML("afterbegin",'<button class="mi vx-tri cm-back-mi" data-action="cmBackText"><b>'+icon("book",15)+'</b><span>Back to text</span></button>')}catch(x){}return r});
  const _mr=MOUNT.reader;MOUNT.reader=()=>{_mr&&_mr();if(S.reading.view==="comic"){const v=document.getElementById("vpop");v&&v.remove(),document.documentElement.classList.remove("vpop-on")}const e=document.querySelector(".cm-empty");e&&!e.querySelector(".cm-back")&&e.insertAdjacentHTML("beforeend",'<button class="btn primary cm-back" data-action="cmBackText" style="margin-top:16px">'+icon("book",16)+'Read '+esc(S.reading.book)+' '+S.reading.ch+' as text</button>')};
```

Result: the empty comic page shows a "Read Romans 8 as text" button. The comic version popover starts with "Back to text". A stale verse popup is removed when the comic view mounts.

Still open: the hidden Read/Study/Comic switcher on phones. Consider showing it again, or adding a mode item to the header menu.

## F9. Chapter overview redesign, phone first

Asked for by Zee after the review, in two rounds. The old page was a Wikipedia-style article of about 11 phone screens.

**Round 1, structure**
- Phones now have one prev/next row. Before, there were four ways to leave before the title.
- The repeated facts, the "names 2 people and 0 places" sentence and the info box are gone.
- Matthew Henry's outline is the first section. Each row jumps to its verse in the reader, with no popup or sheet covering the text.
- Commentary sections start closed. Open/closed state survives re-renders.
- People, Places, Events and Cross references inside Commentary are hidden on this page, because they repeated the People section or were empty.
- The section tab row stays at the top while scrolling and follows the section in view.

**Round 2, AI-only interpretation and type**
- The generic "Meaning / Interpretation" block (Find the meaning, Guard against) is removed. A "Meaning" section appears only when Claude has written a study for the chapter (`S.genStudies[normRef(ref)]`). It is labelled "Written by Claude on (date). Check it against the text."
- Inside Claude (`SAMPLE` set) and with no study yet, "Meaning" shows one "Write a study with Claude" button (`data-action="genStudy"`), then a progress line while Claude writes. Outside Claude nothing is shown.
- The three generic "Questions to start with" stay as one closed "Reading questions" row.
- Type scale, four levels: title in the app's display font (`--display`, Lora) 32px; section headings in `--display` 21px; body Inter 16px/1.5; meta Inter 13px grey in sentence case. All-caps labels and source pills are removed. Sources are one grey line under the section or in Sources at the end.
- Fewer boxes: At a glance and the outline use thin dividers. Reading questions and every commentary section share one accordion style. The key verse is a pull quote with an accent rule. "Read Romans 8" is full width on phones, and Guided study is a quiet text button.
- Note: in this app `--serif` is set to Inter. Use `--display` for serif headings.

**Round 3, from Zee's iPhone (2026-11-28)**
- At a glance took most of the first screen (long values such as "Traditionally attributed to Moses; many scholars see sources compiled over time"). It is now a compact label/value list at 14px. Long values are shortened: text after ";" or "(" is dropped, "Traditionally attributed to X" becomes "X (traditionally)", and "Composition date debated" becomes "Debated". Top spacing is tighter.
- Commentary, key words, dictionary, topics and People stayed as grey placeholders on a fresh load. Cause (it existed before this branch): the data loaders only redraw on the reader and verse study pages. Fixed in source:

BEFORE
```js
gdRedraw=()=>{(ui.page==="reader"||ui.page==="verse-study")&&refresh()}
```
AFTER
```js
gdRedraw=()=>{(ui.page==="reader"||ui.page==="verse-study"||ui.page==="chapter")&&refresh()}
```
BEFORE
```js
const fbRedraw=()=>{["factbook","reader","verse-study"].includes(ui.page)&&refresh()}
```
AFTER
```js
const fbRedraw=()=>{["factbook","reader","verse-study","chapter"].includes(ui.page)&&refresh()}
```
Tested by opening Genesis 1's overview straight from Today with a 2-second delay on every study file. All sections filled in, with no placeholders left.

**Source edits outside the script block**

BEFORE (audience lowercasing, it produced "jewish")
```js
t.audience.replace(/^./,a=>a.toLowerCase())
```
AFTER
```js
t.audience.replace(/^(The|A|An|All|Some|Those|These)\b/,a=>a.toLowerCase())
```

BEFORE (key verses picked up a whole-chapter study as a "verse")
```js
const s=getStudy(`${ref}:${v}`);s&&!keys.includes(s.key)&&keys.push(s.key)
```
AFTER
```js
const s=getStudy(`${ref}:${v}`);s&&s.key.includes(":")&&!keys.includes(s.key)&&keys.push(s.key)
```

**How.** `MOUNT.chapter` rebuilds the page after `PAGES.chapter` renders, using its existing sections. The CSS is in `<style id="verbo-cov-2026-11-28">`, added by the script block under the `/* F9 */` comment.

**Tested:** Romans 8, Acts 13, Psalms 23, Obadiah 1, Genesis 1 and Revelation 22, on phone and desktop, in light and dark. Three Meaning states were checked: outside Claude (hidden), inside Claude with no study (button), and with a written study (shown with its label). No page errors. axe shows no violations on the page in light or dark. Romans 8 on a phone went from 9,125px to about 2,300px.

Still open: many chapters show only one key verse (data). The real "Write a study with Claude" run was not tested, because it needs the app running inside Claude.

## F10. Study sets are saved by default

Asked for by Zee. Before, all five sets (Hebrew and Greek, footnotes and dictionary, people and places, Matthew Henry, more commentaries; about 144 MB) had to be saved by hand in Settings.

**How (script block, `/* F10 */`).**
- After the service worker reports what is saved, the app saves every set that is not complete, one at a time, through the existing `A.pwaSave`. The per-set "saved" toasts are muted (`p.auto`). One toast says what is happening: "Saving study sets for offline use (144 MB)...".
- It waits 8 seconds after start, needs to be online, and skips when the browser reports Data Saver or a 2G connection. iPhones do not report the connection type, so on an iPhone it can run on mobile data.
- It runs on every launch until all sets are complete. This also refills sets the system cleared to free space.
- If the user taps Remove, the set id goes into `localStorage["verbo.packsRemoved"]` and is never downloaded again automatically. Tapping Save takes it back off that list.
- Saved sets live in the `verbo-data-v1` cache, which app updates keep, so the `VERSION` bumps do not delete them.

**Tested:** fresh install, all 5 sets saved in about 54 s on the test server with one toast; then removing Matthew Henry and reloading did not download it again.

Trade-off to decide: 144 MB starts downloading on first open, even on mobile data on iPhones. A "Wi-Fi only" choice is not possible on iPhone because Safari does not report the connection type.

## F11. Chapter deep dive

Asked for by Zee: bring the app's parallels, Factbook, maps, dictionary and related data into the Chapter overview, and reorganise it.

**Order and tabs:** Outline · Meaning (only after Claude writes it) · Key verses · Setting · Connections · Words · Commentary · Notes (or Questions). Empty sections are hidden, and their tabs too.

- **Setting** (new; replaces People): events in the chapter with traditional dates (labelled "Dates are traditional dates and approximate"), a small map of the places mentioned (tap: full chapter map), journeys that pass through the chapter (for example Paul's first journey in Acts 13), then People and Places chips that open Factbook cards. Uses `fbData`, `atlasSVG`, `jmFor`, `fbChip`, `fbEvRow`.
- **Connections** (new): from `window.PARALLELS`, the same story in other books, quoted in other books, and the same teaching elsewhere (tap: the parallels page with "Read them together"). Then the top 8 cross references for the whole chapter. Each verse's top 8 references are scored 8 down to 1 and summed, references inside the same chapter are skipped, and each row shows the verse it comes from and a one-line preview. Tap: peek.
- **Words and topics:** key words (Hebrew or Greek), Easton's dictionary and Nave's topics moved out of Commentary.
- **Commentary:** Matthew Henry, Calvin (and Spurgeon for Psalms when the guide offers it).
- **Your notes** (new): your highlights (with colour dot and colour name for screen readers), bookmarks and notes for this chapter, then the Reading questions.
- **Header:** a "Words of Jesus: N verses" row for chapters with red letters (from `bible/fact/red.json`).
- Long lists show a few rows and "Show all N". Data loads only when the page is drawn, and the loaders redraw the overview when it arrives.

**Tested:** Acts 13, Matthew 26, Romans 8 (with sample highlights and a bookmark), Genesis 1, Psalms 23 and 1 Kings 18 on a phone. No page errors; axe clean in light and dark on Matthew 26.

Still open: some Factbook events have no year, and two Acts 13 events overlap ("First missionary journey begins" and "First Missionary Journey"); this is in the data. Parallels coverage is hand-picked, so many chapters have no parallels.

## F12. Overview speed and stability, sticky tabs, keeping your place, map, two tabs (round 2 items 36 to 40 and 37)

All in the script block under `/* F12 */`, plus three source edits.

- **36, speed.** Two causes. (1) The lexicon, concordance and stats loaders have no in-flight check, so each redraw fetched them again (12 times each). A small `fetch` wrapper now shares one request per `bible/` file while it is in flight. (2) Every arriving file called `refresh()`. On the Chapter overview, background refreshes (`render(true)`) are now coalesced into one redraw per 150 ms. Page changes still draw at once. `gdRedraw` and `fbRedraw` call `window.covRefresh` on this page. Result on Acts 13: 17 redraws down to 4, and no file fetched more than twice.
- **36, no jumping.** While you scroll, the section at the top of the screen and its offset are remembered. After each redraw, `MOUNT.chapter` puts that section back where it was. Test: with every file delayed 1.5 s, Commentary stayed at the same screen position for 10 s while the Outline and Key verses were added above it.
- **38, sticky tabs.** On phones the tab row sticks below the top bar (`--cov-tb`, measured from `.topbar`) while the bar is shown, and at the very top when `.app.bars-hidden` hides it.
- **39, keeping your place.** The same anchor restores your position after Back. `chBook` and `chNum` were added to `BK_KEYS`, so Back reopens the same chapter overview. A `bkBack` wrapper stops the "back to reader" shortcut (`ui.fromRead`) from skipping the overview when you came from it. Tested with in-app Back and browser Back from a parallel: you land on the same section at the same spot. A fresh "Chapter overview" tap still starts at the top.
- **40, map.** `A.covMap` passes the chapter as `ui.atRef` and no longer changes `S.reading`. Source edits: `atlasPage` uses `ui.atRef||S.reading`, and `A.fbAtlasCh` clears `ui.atRef`.
- **37, two tabs.** A `storage` listener on `LS_KEY` (`biblestudy.v1`) takes the other tab's saved items (highlights, bookmarks, notes, plans and so on) and keeps this tab's reading position. Note bodies kept in IndexedDB ("lite" saves) are kept from memory. Shows "Updated with changes from another Verbo tab." once. Tested: a highlight made in tab 2, then a bookmark saved in tab 1. Both are stored.

## F13. Offline gaps, prev/next across books, plain wording, study-tools bar, outline parsing, credits (round 2 items 41 and 43 to 47)

- **41, offline.** `offline-packs.json`: the "dict" set is now "Footnotes, dictionary and cross references". It adds the 6 cross-reference files (`bible/xref/c0.json` to `c5.json`, 3.9 MB) and `bible/fact/red.json`. Users who already saved it will see it as part-saved, and F10 completes it on the next launch. When offline and a file is not saved yet, the overview shows "Not saved on this device yet. Connect to the internet once and it will be saved for offline use." instead of a spinner. Not changed: the "Partly saved" percentage in Offline library, which counts Bible versions, not study sets.
- **43, outline parsing.** Accepts ";" lists ("24–30, 36–43" for Matthew 13), capitalises fragments ("Sufferings" in Isaiah 53, a split in Henry's own data), and builds an outline from Henry's section ranges and the first sentence of each section when he has no outline list (Psalms 119: 22 sections).
- **44, prev/next.** Built from `BOOKS`, so it crosses books (Matthew 28 to Mark 1, Exodus 1 to Genesis 50) and works for one-chapter books (Obadiah 1: Amos 9 and Jonah 1).
- **45, plain wording.** "Key words in Greek" or "Hebrew", "Bible dictionary" and "Topics" instead of "Easton" and "Nave". Strong's codes are hidden on this page (tap a word for full detail). Dictionary and topic chips are sorted A to Z and capped at 15 with "Show all". The cross-reference note no longer names the ranking source (it moved to Sources). The Questions section has a heading.
- **46, study-tools bar.** The auto-save notice is now a bar: "Saving Bible study tools for offline use (N MB). You can keep reading." with Not now (pauses for 24 hours, says so). After a complete first run: "Bible study tools saved. They now work without the internet."
- **47, credits.** The overview's Sources lists Matthew Henry, Calvin (Beveridge, CCEL), Spurgeon, Theographic (CC BY-SA 4.0) with OpenBible.info and Natural Earth, OpenBible.info cross references (CC BY), STEPBible lexicons (CC BY 4.0), Easton, Nave and the CrossWire red letters. The app-wide Help page (item 22) is still open.

## F14. Dialog focus, misspelled books, the floating control, tap targets, connections (items 4, 10, 13, 14 and 42)

Script block `/* F14 */`, plus source edits to the parallels list and the cross-reference ranking in F11.

- **4, dialogs.** While `#modalBg` is shown, `#app` is `inert` and `aria-hidden`, and Tab and Shift+Tab cycle inside the dialog. Tested: 40 Tab presses, 0 left the dialog. On close the page is active again and focus returns to the opener (F6). Focus already moves into the study panel after a verse is chosen with Enter.
- **10, misspelled books.** `window.fuzzyBook` finds the closest book name (edit distance, a swap counts as one edit; 1 edit for short names, 2 for longer; same first letter; no tie). Used only in search, not in `parseRef`, so notes and links are not affected. The book picker now offers "John" for "Jhon", "Matthew 5" for "Mathew 5" and "Revelation 21" for "Revelations 21", and Enter opens the first one. Global search shows "Did you mean: Open John 3:16" for "Jhon 3:16". The verse search box (`vsBooks`) also falls back to it.
- **13, floating control.** On phones the prev/play/next pill hides while you read and shows near the end of the chapter or while audio plays. Every chapter now ends with labelled buttons ("‹ John 2" and "John 4 ›") that cross books. Desktop is unchanged.
- **14, tap targets.** On touch screens: header icons and pills are at least 44px (38px wide on screens under 380px, so a long book name still fits, the same as before), highlight swatches are 44px, and the Chapter overview and Guided study links and breadcrumbs are 44px tall.
- **42, connections.** New parallels: "Jesus predicts his betrayal" (Matthew 26:20-25, Mark 14:17-21, Luke 22:21-23, John 13:21-30) and "Micaiah warns Ahab" (1 Kings 22:1-28, 2 Chronicles 18:1-27). Cross references now skip chapters already listed as parallels and give links across the Old and New Testaments 1.6 times the weight. Isaiah 53 now lists 1 Peter 3:18, 2 Corinthians 5:21 and Galatians 3:13 first. Psalms 22 shows Matthew 27:46 under "Quoted in other books". Hebrews 2:12 is still not listed, because it is not in the quotes list.

## F15. Section sheet on the Chapter overview

Asked for by Zee: tapping an outline row left the overview for the reader. Now it opens a bottom sheet (a centred panel on desktop) and the overview stays where it was.

- **What opens it:** outline rows, key verse references, and highlight or bookmark rows in "Your notes". Notes still open the note.
- **What it shows:** the section reference as the title (split ranges such as "Matthew 13:24–30, 36–43" show both parts with "…" between them), the outline label, the verses in your current version (KJV if that version is not loaded; long sections are clipped with "Show all N verses"), and Matthew Henry's comment on the section the first verse falls in, clipped with "Show more". A stray range at the start of some Henry sections (", 36–43 This parable…") is removed.
- **Buttons:** a footer that stays visible: Previous section, Read in context, Next section. Only "Read in context" leaves the overview. It opens the reader at the first verse with no popup or sheet covering it. Key verses and notes have no previous or next.
- **Closing:** X, tap outside, Escape, or swipe down on the header. Focus returns to the row you tapped, and the overview scroll position is unchanged.
- **How:** `A.covSec`, `A.covSecStep`, `A.covRead` and `covDraw` in the script block under `/* F15 */`. It uses the app's `modal()` sheet, so the F6 and F14 focus handling applies. The outline ranges are kept in `window.covOL` while the page builds.

## F16. Bookmark and highlight markers, read timing, Auto theme (items 16, 26 and 20)

Script block `/* F16 */`, plus two source edits.

- **16.** The verse popup now shows "Saved" (with `aria-pressed`) when the verse is bookmarked. The app already draws a small bookmark icon at the end of a bookmarked verse (`svg.bmk`, named "Bookmarked"); it is now filled in the accent colour so it is easier to see. Highlighted verses get `aria-describedby` pointing to hidden text such as "Highlighted blue.", so the colour is no longer the only signal. Nothing is added to the verse text, so copying is unchanged.
- **26.** A chapter is marked read only after real reading time: 1.5 s per verse, at least 15 s and at most 60 s. If you reach the end sooner, it is marked when the time is up and you are still on that chapter. Source edit in `pgWatchEnd`: the observer also checks `window.covReadOk`. Tested: jumping to the end of Philemon did not mark it after 4 s, and did after the time was up. Plan days (R19) were not changed.
- **20.** Settings > Theme now has Auto, Light and Dark. Auto follows the device and changes live. Light or Dark (or the theme button) turns Auto off. Existing users whose theme matches their device start on Auto; others keep their choice. Stored as `S.themeAuto`. Source edit: the Settings theme row.

## New script block (added just before `</body>`)

The block below is the F1, F2 and F7 part. F8 adds the lines shown in the F8 section to the same block.

```html
<script id="verbo-review-fixes-2026-11-28">
/* Review fixes 2026-11-28. See docs/review/FIXES.md */
(function(){
  if(typeof A==="undefined")return;
  /* F1: drop bookmarks saved without a reference by the old phone popup bug */
  try{const b=S.bookmarks||[],ok=b.filter(x=>x&&typeof x.ref==="string"&&x.ref);ok.length!==b.length&&(S.bookmarks=ok,save(),typeof refresh=="function"&&refresh())}catch(e){}
  /* F2: on phones, Highlight and Note in the verse popup open the study sheet with the tool ready */
  const inPop=()=>!!document.getElementById("vpop");
  const _hl=A.hlToggle;A.hlToggle=function(){if(inPop()&&ui.sel){ui.hlOpen=!0;return A.stOpen()}return _hl.apply(this,arguments)};
  const _nm=A.noteModal;A.noteModal=function(e){if(inPop()&&ui.sel){ui.qnOpen=!0,A.stOpen(),setTimeout(()=>{const t=document.getElementById("qnText");t&&t.focus()},80);return}return _nm.apply(this,arguments)};
  /* F7: Escape on the welcome sheet counts as seen */
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&document.querySelector(".wel-scrim")){try{localStorage.setItem("verbo.welcomed","1")}catch(x){}}},!0);
})();
</script>
```

## Release step: bump `VERSION` in `sw.js`

`VERSION` in `sw.js` changed from `bcb3c4b585` to a new value with each change on this branch (now the first 10 characters of the SHA-1 of the final `index.html`) (the first 10 characters of the SHA-1 of the new `index.html`; any new value works). This is required. The "A new version of Verbo is ready. Update" banner only appears when the `sw.js` file changes. Without the bump, installed users would get no banner and could keep the old offline copy. Tested by simulating a user on the old version and then deploying the new one: the banner appeared, and Update loaded the new code (`screenshots/after/update-banner.png`).


## F17. Your study, AI wording, red letters on by default (asked for by Zee)

- The Chapter overview has a "Your study" section. It gathers the reader's highlights, bookmarks, notes and tags for the chapter, their Guided study answers and quiz results, and any AI-made explanations, studies, comics and chats about the chapter.
- AI content is labelled "Made with AI" or "Written by AI". The app no longer shows any product name for the AI. Code names such as `window.claude` are unchanged.
- Words of Jesus in red is now on by default. The check changed from `S.reading.wj` to `S.reading.wj!==false`, in `markRed()` and in the Aa panel. A user who turned it off keeps it off, because the toggle stores `false`.

## F18. Atlas: Follow the Journey (asked for by Zee)

New `<script id="verbo-atlas-2026-11-28">` before `</body>`, plus a new data file `bible/fact/atlas.json` and a terrain image `bible/fact/relief_paul1.jpg`. It is a new screen, so there is no BEFORE text. The source is also in the commit message.

What it does:
- New page `atlas` (`nav("atlas",{atJ:"paul1"})`). It opens from the journey page ("Follow the journey, stop by stop") and from the Chapter overview of Acts 13 and 14.
- One journey so far: Paul's first journey, 15 stops (out to Derbe and back).
- Map: Verbo's own coastlines and rivers, shaded relief clipped to land, engraved sea, italic region names, numbered cities, a 50-mile scale bar. Route and buttons use the app theme color. Three looks: old map (default), plain, and a night map when the app is in dark mode.
- Playback: Previous, Play/Pause, Next, a progress bar. The current leg draws itself in. Done legs are solid, sea legs dashed, later legs faint. Arrows show direction. Reduced motion turns the animation off.
- Stop card: stop number, road or sea and miles from the last stop, a short note, the first verses of the passage, Read (opens the reader at that passage), and facts: where it is today, ancient names, periods, and links to the Pleiades and OpenBible records.
- Uncertain sites: Derbe has a dashed ring, a "?" and a "Site uncertain" badge. The other proposed sites are marked with an x when Derbe is the current stop.
- Phone: map on top, bottom sheet with a handle (tap or swipe to open). Tablet: same, taller map. Desktop: map with a 400px sidebar that also lists the Outbound and Return stops.
- Map: drag, wheel, pinch, zoom buttons, fit button. Tap a city to go to it. Keyboard: Left and Right arrows, K to play.
- Offline: atlas.json and the terrain image are in the "People, places and maps" offline set. Without the file the page says it could not load and offers Try again.

Data (`atlas.json`), kept apart from the drawing code:
- OpenBible.info Bible Geocoding (CC BY 4.0): modern site and confidence for each place. Derbe: Kerti Hüyük 860, Devri Şehri 49, Güdelisin -122 (OpenBible's own scores).
- Pleiades (CC BY 3.0): place ID, ancient names, periods. Matched through Wikidata using `isawnyu/pleiades_wikidata`. Seleucia (658483), Attalia (638778) and Iconium (648647) were matched by hand.
- Theographic (CC BY-SA 4.0): the route lines and stop positions, as before.
- Terrain: shaded relief by Tom Patterson (public domain), cropped and tinted.
- Not used yet: Itiner-e Roman roads (CC BY 4.0). Its download sites could not be reached from the build machine. Routes still follow Theographic lines and are labelled approximate.

Tests: `docs/review/tests/test_atlas.py`. 73 checks on phone, tablet and desktop, plus the overview entry, dark mode and the offline message. All pass. axe on the Atlas is clean.


## F19. Atlas: all 12 journeys (asked for by Zee)

- `atlas.json` now holds all 12 journeys: Abram (two), Jacob, the Exodus, Naomi and Ruth, the exile to Babylon, Mary and Joseph to Bethlehem, the flight into Egypt, and Paul's four journeys. Each has an ordered list of stops with a passage and a short note. The itineraries were written by hand from the Bible text (`docs/review/tests/atlas-data/itin.py`). Paul's second and third journeys needed this because the stop list in the route data is not in order.
- Route lines come from Theographic. A script fits them to each leg, measures miles and marks sea legs. Where no route line joins two stops, a straight line is drawn: Corinth to Cenchreae, and Forum of Appius to Three Taverns.
- Stops that the Bible does not name (for example Babylon and Mari on Abram's route, or Jericho for Ruth) are marked "Not named in the Bible" and drawn as dotted circles. Moab is marked "Region".
- Places matched to OpenBible.info: 64 of 67. Aleppo, Mari and Pelusium are not Bible places. Places matched to Pleiades: 46. The card leaves out the Pleiades facts when there is no match.
- The Exodus shows its debated note under the title. Uncertain sites (Rameses, the sea crossing, Marah, Elim, Rephidim, Mount Sinai, Kadesh-barnea, Ur, Beersheba, Bethel, Derbe and others) show "Site uncertain" and other proposed sites.
- Labels are placed automatically so they do not overlap. A place whose name does not fit shows its number only. Region and sea names come from the app's existing list and are dropped where they would collide.
- Terrain: one lower-detail image for the whole Bible world (`relief_all.jpg`), plus a detailed image for each region (Aegean, Italy, Levant, Mesopotamia). On very small maps (Ruth, Bethlehem) the terrain is faded, because the source is too coarse at that zoom.
- A journey picker at the end of the sidebar switches between journeys.
- The offline set "People, places and maps" grew by about 0.8 MB.
- Fixes found while testing: the zoom-in icon was removed by the redraw, and a name ending in " S" or " P" lost two letters.

Tests: `test_atlas.py` now also opens all 12 journeys and checks stops, legs, labels, the Region and Not named badges, the debated note and the picker. 91 checks, all pass.

---

## Test results (headless Chrome, 2026-11-28)

| Fix | Check | Result |
|---|---|---|
| F1 | Phone popup Save stores `{ref:"John 3:3"}`; Bookmarks page opens | Pass |
| F1 | Corrupt `{t:...}` bookmark is removed on reload | Pass |
| F2 | Popup Highlight shows swatches; tapping gold saves the highlight | Pass |
| F2 | Popup Note shows the note box with focus in `#qnText` | Pass |
| F3 | Verse `span.v` has no `aria-label` | Pass |
| F4 | G25 → 110 verses, H430 → 2248, H1 → 1060, G3056 still works | Pass |
| F5 | Toasts at Genesis 1 (previous) and Revelation 22 (next) | Pass |
| F6 | Pill name "Revelation 22, choose book and chapter"; dialog named "Translation", focus inside, focus back on the pill after Escape | Pass |
| F7 | Desktop says "Click Bible on the left"; Escape sets `verbo.welcomed` | Pass |
| F8 | Comic mode (Romans 8, BSB, phone): the empty-page button and the popover item both return to text (39 verses shown) | Pass |
| F9 | Chapter overview on 6 chapters, phone and desktop, light and dark; outline tap opens the reader with no popup; Meaning hidden outside Claude, button inside Claude, shown with label once written; axe clean | Pass |
| F9 | Cold load of Genesis 1 overview with slow data: all sections fill in | Pass |
| F10 | Fresh install saves all 5 study sets automatically; a removed set stays removed after reload | Pass |
| F11 | Deep dive on 6 chapters: Setting, Connections, Words, Your notes appear only when they have data; map, journeys, parallels, cross references and Words of Jesus work; axe clean | Pass |
| F12 | Acts 13: 4 redraws, no repeated lexicon fetches; tabs sit below the top bar; Back from a parallel (in-app and browser) returns to the same spot; map keeps the reading position and Back returns to the overview; two tabs keep both edits; no jumping while data loads | Pass |
| F13 | Outlines for Matthew 13, Isaiah 53, Psalms 119; prev/next across books and for Obadiah; plain Words names, no codes, chips capped; offline messages instead of spinners; bar with Not now | Pass |
| F14 | 0 of 40 Tabs leave a dialog; "Jhon", "Mathew 5" and "Revelations 21" found and Enter opens them; "Jhon 3:16" gets Did you mean; floating control hidden mid-chapter, labelled end buttons; header targets 44px, same layout at 360px; new parallels for John 13 and 2 Chronicles 18 | Pass |
| F15 | Romans 8, Matthew 13, Psalms 119 on phone and desktop: sheet opens with verses and Henry, Next steps through sections, Escape closes and keeps the scroll position and focus, Read in context opens the reader; key verse and note rows open the sheet; axe clean | Pass |
| F16 | Popup says Saved for a bookmarked verse; highlight colour is described; Philemon not marked read after 4 s, marked after the time; Auto follows the device, Light stays Light | Pass |
| F17 | Fresh user sees red letters in Matthew 5; after turning them off and reloading they stay off | Pass |
| F18 | Atlas on phone, tablet and desktop: route progress, playback, sheet, timeline, tap a city, keyboard, Read, map styles, Derbe uncertainty, Pleiades link, overview entry, dark map, offline message; axe clean | Pass |
| F19 | All 12 journeys open with the right number of stops and legs; Exodus labels and debated note; Moab is Region; Jericho is Not named; picker switches journey | Pass |
| All | No page errors. axe on the reader: before: `aria-required-children` x1 and `label-content-name-mismatch` x16. After: only `aria-required-children` on `#tabstrip` is left | Pass |

Not tested: a real phone, VoiceOver or TalkBack.
