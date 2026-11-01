"""Builds the installable web app (PWA) from /tmp/work/arcade_embed.html into /tmp/work/app/dist."""
import os,shutil,re,json,base64,time,hashlib
D='/tmp/work/app/dist';shutil.rmtree(D,ignore_errors=True);os.makedirs(D+'/icons')
for f in os.listdir('/tmp/work/app/icons'):shutil.copy('/tmp/work/app/icons/'+f,D+'/icons/'+f)
emb=open('/tmp/work/arcade_embed.html',encoding='utf-8').read()
a="function immOn(){try{return IMMERSIVE&&window.innerWidth>=900&&!(window.matchMedia&&matchMedia('(hover: none) and (pointer: coarse)').matches);}catch(e){return false;}}"
assert emb.count(a)==1;emb=emb.replace(a,"function immOn(){return true;}")
# app: keep clear of the iPhone Dynamic Island / notch and home bar. The arcade box sits inside the safe area
for a,b in [("if(immOn()) h=window.innerHeight||document.documentElement.clientHeight||h;","if(immOn()) h=bleed.getBoundingClientRect().height||window.innerHeight||h;"),
            ("var FULL_BLEED=true;","var FULL_BLEED=false;"),("var UNCLIP=true;","var UNCLIP=false;")]:
  assert emb.count(a)==1,a;emb=emb.replace(a,b)
# app: hide the Full screen button (the app is already full screen)
a="if(TRIM_INNER) src=src.replace('</head>',"
assert emb.count(a)==1
emb=emb.replace(a,"src=src.replace('</head>','<style>#fsBtn{display:none!important}html.fs .wrap{padding:0!important;max-width:none!important}html.fs .frames iframe{border-radius:0!important}</style></head>');\n  "+a)
# app: every game edge to edge (no outer margin, square corners)
a="if(K.css)s=s.replace('</head>',"
assert emb.count(a)==1
GCSS="html.fs .wrap{padding:0!important;max-width:none!important}html.fs .felt{border-radius:0!important;border-left-width:0!important;border-right-width:0!important;border-top-width:0!important;border-bottom-width:0!important}"
emb=emb.replace(a,"s=s.replace('</head>','<style id=\\'su-app\\'>"+GCSS+"</style></head>');"+a)
ver=hashlib.sha1(emb.encode()).hexdigest()[:10]
html='''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,interactive-widget=resizes-content">
<title>Saddle Up Arcade</title>
<meta name="description" content="Casino tables, mahjong, dominoes, Boomtown Tycoon and more. Play free with friends.">
<meta name="theme-color" content="#0b1222">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Arcade">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icons/favicon-64.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>html,body{margin:0;height:100%;background:#0f172a;overflow:hidden;overscroll-behavior:none;-webkit-text-size-adjust:100%}
#idf-bleed{position:fixed!important;top:env(safe-area-inset-top,0px)!important;right:env(safe-area-inset-right,0px)!important;bottom:env(safe-area-inset-bottom,0px)!important;left:env(safe-area-inset-left,0px)!important;width:auto!important;height:auto!important;padding:0!important;margin:0!important}\n#idf-frame{height:100%!important}</style>
</head><body>
'''+emb+'''
<script>if('serviceWorker' in navigator){addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>
</body></html>
'''
open(D+'/index.html','w',encoding='utf-8').write(html)
man={"name":"Saddle Up Arcade","short_name":"Arcade","description":"Casino tables, mahjong, dominoes, Boomtown Tycoon and more.",
 "start_url":"./","scope":"./","display":"fullscreen","display_override":["fullscreen","standalone"],"orientation":"any",
 "background_color":"#0b1222","theme_color":"#0b1222","categories":["games","entertainment"],
 "icons":[{"src":"icons/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/icon-512.png","sizes":"512x512","type":"image/png"},
          {"src":"icons/maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}
json.dump(man,open(D+'/manifest.webmanifest','w'),indent=1)
sw=r'''/* Saddle Up Arcade: offline support. The page is network-first (fresh updates), art is cache-first. */
var V='arcade-%s',ART='arcade-art-v1';
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
'''%ver
open(D+'/sw.js','w').write(sw)
open(D+'/vercel.json','w').write(json.dumps({"headers":[{"source":"/sw.js","headers":[{"key":"Cache-Control","value":"no-cache"}]},
  {"source":"/index.html","headers":[{"key":"Cache-Control","value":"no-cache"}]},{"source":"/","headers":[{"key":"Cache-Control","value":"no-cache"}]}]},indent=1))
print('built',ver,os.path.getsize(D+'/index.html'))
