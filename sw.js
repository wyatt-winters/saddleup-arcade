/* Saddle Up Arcade: offline support. The page is network-first (fresh updates), art is cache-first. */
var V='arcade-4183cc70d5',ART='arcade-art-v8';
self.addEventListener('install',function(e){self.skipWaiting();e.waitUntil(caches.open(V).then(function(c){return c.addAll(['./','index.html','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png']);}));});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==V&&k!==ART;}).map(function(k){return caches.delete(k);}));}).then(function(){return self.clients.claim();}));});
self.addEventListener('fetch',function(e){
  var r=e.request,u;if(r.method!=='GET')return;try{u=new URL(r.url);}catch(x){return;}
  if(/supabase\.co$/.test(u.hostname))return;
  if(u.origin===location.origin&&(r.mode==='navigate'||/\/(index\.html)?$/.test(u.pathname))){
    e.respondWith(fetch(r).then(function(res){var cp=res.clone();caches.open(V).then(function(c){c.put('index.html',cp);});return res;}).catch(function(){return caches.match('index.html');}));return;}
  if(/filesafe\.space$|jsdelivr\.net$|googleapis\.com$|gstatic\.com$/.test(u.hostname)||u.origin===location.origin){
    e.respondWith(caches.open(ART).then(function(c){return c.match(r).then(function(hit){
      var net=fetch(r).then(function(res){if(res&&(res.ok||res.type==='opaque'))c.put(r,res.clone());return res;}).catch(function(){return hit;});
      return hit||net;});}));}
});
