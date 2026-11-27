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

## New script block (added just before `</body>`)

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

The service worker loads the page network-first (`sw.js`, navigate handler), so users get the new `index.html` on their next online visit. A `VERSION` bump in `sw.js` is not needed.

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
| All | No page errors. axe on the reader: before: `aria-required-children` x1 and `label-content-name-mismatch` x16. After: only `aria-required-children` on `#tabstrip` is left | Pass |

Not tested: a real phone, VoiceOver or TalkBack.
