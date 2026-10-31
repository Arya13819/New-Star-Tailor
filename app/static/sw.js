// New Star Tailor — service worker.
// Caches the static shell and read-only public pages only. Never caches
// anything under /admin, /customer, /api, or any POST/mutating request —
// order/payment data must always come fresh from the server.
const CACHE_VERSION = "nst-v6";
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const PAGE_CACHE = `${CACHE_VERSION}-pages`;

const PRECACHE_URLS = [
  "/",
  "/services",
  "/about",
  "/gallery",
  "/contact",
  "/track-order",
  "/static/css/theme.css?v=6",
  "/static/css/premium.css?v=6",
  "/static/css/catalogue.css?v=6",
  "/static/js/premium.js?v=6",
  "/static/vendor/bootstrap/bootstrap.min.css",
  "/static/vendor/bootstrap/bootstrap.bundle.min.js",
  "/static/img/brand-star.svg",
  "/static/img/favicon.png?v=6",
  "/static/manifest.webmanifest",
];

const CACHEABLE_PAGE_PATHS = new Set(["/", "/services", "/about", "/gallery", "/contact", "/track-order"]);

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key.startsWith("nst-") && key !== STATIC_CACHE && key !== PAGE_CACHE)
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Never touch non-GET requests (order placement, payments, sign-in, etc.).
  if (request.method !== "GET") {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return;
  }

  // Never cache anything gated by auth or account-specific data.
  if (
    url.pathname.startsWith("/admin") ||
    url.pathname.startsWith("/customer") ||
    url.pathname.startsWith("/api") ||
    url.pathname.startsWith("/auth")
  ) {
    return;
  }

  if (url.pathname.startsWith("/static/")) {
    // Network-first, same as the page shell below: these are plain
    // filenames that change in place (no content hash), so cache-first
    // would keep serving a stale CSS/JS/image file indefinitely after a
    // deploy — only fall back to the cache when actually offline.
    event.respondWith(
      fetch(request)
        .then((res) => {
          const copy = res.clone();
          caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  if (CACHEABLE_PAGE_PATHS.has(url.pathname)) {
    // Network-first: shop details/pricing may change, so prefer fresh data
    // and only fall back to the cached shell when offline.
    event.respondWith(
      fetch(request)
        .then((res) => {
          const copy = res.clone();
          caches.open(PAGE_CACHE).then((cache) => cache.put(request, copy));
          return res;
        })
        .catch(() => caches.match(request))
    );
  }
});
