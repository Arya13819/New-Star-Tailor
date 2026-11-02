// PHP deployment caches static assets only; forms and account data stay online.
const CACHE='nst-laravel-v2';
const ASSETS=['/static/css/atelier.css?v=20261102','/static/css/theme.css?v=6','/static/css/premium.css?v=6','/assets/css/php-ui.css?v=1','/static/vendor/bootstrap/bootstrap.min.css','/static/vendor/bootstrap/bootstrap.bundle.min.js','/static/img/brand-star.svg','/static/manifest.webmanifest'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('nst-')&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
 const req=event.request,url=new URL(req.url);
 if(req.method!=='GET'||url.origin!==location.origin||(!url.pathname.startsWith('/static/')&&!url.pathname.startsWith('/assets/')))return;
 event.respondWith(fetch(req).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(req,copy));}return response;}).catch(()=>caches.match(req)));
});
