/* Service worker: maakt installeren als app mogelijk en toont de laatst bekende agenda zonder verbinding.
   Altijd eerst het netwerk, en daarbij de HTTP-cache (10 min bij GitHub Pages) overslaan: zo zie je meteen de nieuwste versie.
   Alleen als er echt geen verbinding is: dezelfde pagina uit de reservekopie (nooit een ander bestand in plaats van het gevraagde). */
const CACHE = "ca-v4";
const SHELL = ["index.html", "info.html", "app.js", "manifest.webmanifest", "img/icon-192.png", "img/icon-512.png", "img/splash.jpg"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: "no-cache" })))).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin) return;
  const nav = r.mode === "navigate", key = nav && /\/$/.test(u.pathname) ? u.pathname + "index.html" : u.pathname;
  e.respondWith(
    fetch(r.url, { cache: "no-cache", credentials: "same-origin" })
      .then(res => { if (res.ok && res.type === "basic") { const copy = res.clone(); caches.open(CACHE).then(c => c.put(key, copy)); } return res; })
      .catch(() => caches.match(key, { ignoreSearch: true }).then(m => m || (nav ? caches.match("index.html", { ignoreSearch: true }) : Response.error())))
  );
});
