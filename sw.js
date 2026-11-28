/* Verbo service worker: the app opens offline, and Bible text you have read stays available. */
const VERSION = "65745305fe";
const SHELL = "verbo-shell-" + VERSION;
const DATA = "verbo-data-v1";      // Bible and library files: kept across app updates
const FONTS = "verbo-fonts-v1";

const SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/maskable-512.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png",
  "./offline-packs.json",
];
// Small files every page needs, saved on install
const CORE_DATA = ["bible/titles/ceb.json", "bible/titles/tl.json", "bible/fonts/journey.css", "bible/fonts/pixel.css", "bible/fonts/sketch.css", "bible/fact/facts.json"];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const shell = await caches.open(SHELL);
    await shell.addAll(SHELL_FILES);
    const data = await caches.open(DATA);
    await Promise.all(CORE_DATA.map(async (u) => { if (!(await data.match(u))) { try { await data.add(u); } catch (_) {} } }));
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith("verbo-shell-") && k !== SHELL) await caches.delete(k);
    await dropChangedData();
    await self.clients.claim();
  })());
});

// Saved study files are kept across updates, so any file whose content changed is dropped here
async function dropChangedData() {
  try {
    const res = await fetch("./data-hashes.json", { cache: "no-store" }); if (!res.ok) return;
    const now = await res.clone().json();
    const meta = await caches.open("verbo-meta");
    const prevRes = await meta.match("./__data-hashes");
    const prev = prevRes ? await prevRes.json() : null;
    const data = await caches.open(DATA);
    if (prev) { for (const k of Object.keys(now)) if (prev[k] && prev[k] !== now[k]) await data.delete("./" + k); }
    else { for (const k of ["bible/ilx/lex/H.json", "bible/ilx/lex/G.json"]) await data.delete("./" + k); }
    await meta.put("./__data-hashes", res);
  } catch (_) {}
}

self.addEventListener("message", (e) => {
  const m = e.data || {};
  if (m.type === "skipWaiting") self.skipWaiting();
  if (m.type === "savePack") e.waitUntil(savePack(m.id, m.files, e.source));
  if (m.type === "removePack") e.waitUntil(removePack(m.files, e.source, m.id));
  if (m.type === "packStatus") e.waitUntil(packStatus(m.packs, e.source));
});

async function savePack(id, files, client) {
  const c = await caches.open(DATA);
  let done = 0, failed = 0;
  for (const u of files) {
    try { if (!(await c.match(u))) await c.add(u); } catch (_) { failed++; }
    done++;
    if (client && (done % 3 === 0 || done === files.length)) client.postMessage({ type: "packProgress", id, done, total: files.length, failed });
  }
  if (client) client.postMessage({ type: "packDone", id, failed });
}
async function removePack(files, client, id) {
  const c = await caches.open(DATA);
  await Promise.all(files.map((u) => c.delete(u)));
  if (client) client.postMessage({ type: "packRemoved", id });
}
async function packStatus(packs, client) {
  const c = await caches.open(DATA);
  const out = {};
  for (const p of packs) { let n = 0; for (const u of p.files) if (await c.match(u)) n++; out[p.id] = n; }
  if (client) client.postMessage({ type: "packStatus", status: out });
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // the page itself: newest when online, saved copy when offline
  if (req.mode === "navigate") {
    e.respondWith((async () => {
      try {
        // always ask the server (a quick "has it changed?" check), so a new version shows on the next open
        const res = await fetch(req, { cache: "no-cache" });
        const c = await caches.open(SHELL); c.put("./index.html", res.clone());
        return res;
      } catch (_) {
        return (await caches.match("./index.html", { ignoreSearch: true })) || (await caches.match("./"));
      }
    })());
    return;
  }

  // Google Fonts: saved copy first, refreshed in the background
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(staleWhileRevalidate(req, FONTS));
    return;
  }

  if (url.origin !== location.origin) return;

  // Bible texts are saved by the app itself (IndexedDB), so they go straight to the network here
  if (/\/bible\/(kjv|bsb|asv|web|drc|adb|asd|ceb|occb|orig|xref|notes)\//.test(url.pathname)) return;
  // commentary, Hebrew/Greek, maps, library: these never change, so the saved copy is used and anything opened is kept
  if (url.pathname.includes("/bible/")) {
    e.respondWith((async () => {
      const c = await caches.open(DATA);
      const hit = await c.match(req, { ignoreSearch: true });
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) c.put(req, res.clone());
      return res;
    })());
    return;
  }

  // icons, manifest
  e.respondWith((async () => (await caches.match(req, { ignoreSearch: true })) || fetch(req))());
});

async function staleWhileRevalidate(req, name) {
  const c = await caches.open(name);
  const hit = await c.match(req);
  const net = fetch(req).then((res) => { if (res.ok || res.type === "opaque") c.put(req, res.clone()); return res; }).catch(() => hit);
  return hit || net;
}

/* Daily reading reminder. Chrome on Android can wake an installed app about once a day
   (periodic background sync); other browsers get the reminder when the app opens. */
async function remindCheck() {
  try {
    const c = await caches.open("verbo-meta");
    const r = await c.match("./__remind"); if (!r) return;
    const cfg = await r.json(); if (!cfg || !cfg.on) return;
    const now = new Date(), p2 = (n) => String(n).padStart(2, "0"), day = `${now.getFullYear()}-${p2(now.getMonth() + 1)}-${p2(now.getDate())}`;
    const [h, m] = String(cfg.time || "07:00").split(":").map(Number);
    if (now.getHours() * 60 + now.getMinutes() < h * 60 + m) return;
    if (cfg.lastShown === day || cfg.readDay === day) return;
    cfg.lastShown = day;
    await c.put("./__remind", new Response(JSON.stringify(cfg), { headers: { "content-type": "application/json" } }));
    await self.registration.showNotification(cfg.title || "Time for today's reading", { body: cfg.body || "Open Verbo to read today's chapter.", tag: "verbo-remind", icon: "icons/icon-192.png", badge: "icons/icon-192.png", data: { url: "./?a=read" } });
  } catch (e) {}
}
self.addEventListener("periodicsync", (e) => { if (e.tag === "verbo-remind") e.waitUntil(remindCheck()); });
self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || "./";
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((cs) => {
    for (const c of cs) { if ("focus" in c) { c.postMessage({ type: "remind-open" }); return c.focus(); } }
    return self.clients.openWindow(url);
  }));
});
