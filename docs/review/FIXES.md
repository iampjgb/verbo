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
| All | No page errors. axe on the reader: before: `aria-required-children` x1 and `label-content-name-mismatch` x16. After: only `aria-required-children` on `#tabstrip` is left | Pass |

Not tested: a real phone, VoiceOver or TalkBack.
