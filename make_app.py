"""Builds the installable web app (PWA) from /tmp/work/arcade_embed.html into /tmp/work/app/dist."""
import os,shutil,re,json,base64,time,hashlib
D='/tmp/work/app/dist';shutil.rmtree(D,ignore_errors=True);os.makedirs(D+'/icons')
for f in os.listdir('/tmp/work/app/icons'):shutil.copy('/tmp/work/app/icons/'+f,D+'/icons/'+f)
os.makedirs(D+'/splash');[shutil.copy('/tmp/work/app/splash/'+f,D+'/splash/'+f) for f in os.listdir('/tmp/work/app/splash') if f.endswith('.png')]
SPCSS=open('/tmp/work/app/splash/splash.css').read();SPIN=open('/tmp/work/app/splash/inner.html').read()
DEV=[(440,956,3),(430,932,3),(402,874,3),(393,852,3),(390,844,3),(428,926,3),(414,896,3),(375,812,3),(414,896,2),(375,667,2),(414,736,3),(320,568,2)]
START=''.join('<link rel="apple-touch-startup-image" media="screen and (device-width: %dpx) and (device-height: %dpx) and (-webkit-device-pixel-ratio: %d) and (orientation: portrait)" href="splash/launch-%dx%d.png">\n'%(w,h,d,w*d,h*d) for w,h,d in DEV)
emb=open('/tmp/work/arcade_embed.html',encoding='utf-8').read()
a="function immOn(){try{return IMMERSIVE&&window.innerWidth>=900&&!(window.matchMedia&&matchMedia('(hover: none) and (pointer: coarse)').matches);}catch(e){return false;}}"
assert emb.count(a)==1;emb=emb.replace(a,"function immOn(){return true;}")
# app: keep clear of the iPhone Dynamic Island / notch and home bar. The arcade box sits inside the safe area
for a,b in [("if(immOn()) h=window.innerHeight||document.documentElement.clientHeight||h;","if(immOn()) h=bleed.getBoundingClientRect().height||window.innerHeight||h;"),
            ("var FULL_BLEED=true;","var FULL_BLEED=false;"),("var UNCLIP=true;","var UNCLIP=false;"),
            ("  function setH(h){\n","  function setH(h){imp(frame,'height','100%');return;\n")]:
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
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="Arcade">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icons/favicon-64.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
'''+START+'''
<style>html,body{margin:0;height:100%;background:#0f172a;overflow:hidden;overscroll-behavior:none;-webkit-text-size-adjust:100%}
#idf-bleed{position:fixed!important;top:0!important;bottom:0!important;left:0!important;right:0!important;width:auto!important;height:auto!important;padding:env(safe-area-inset-top,0px) var(--sr,env(safe-area-inset-right,0px)) 0 var(--sl,env(safe-area-inset-left,0px))!important;margin:0!important;box-sizing:border-box!important}\n#idf-frame{height:100%!important}
'''+SPCSS+'''</style>
</head><body>
<div class="sp" id="splash">'''+SPIN+'''<div class="sp-bar"><i></i></div></div>
'''+emb+'''
<script>/* landscape: only keep clear of the side the Dynamic Island / notch is on; the other side runs to the edge */
(function(){var R=document.documentElement;function side(){var a=typeof window.orientation==='number'?window.orientation:((screen.orientation&&screen.orientation.angle)||0);
  a=((a%360)+360)%360;var E='env(safe-area-inset-',L=E+'left,0px)',Rt=E+'right,0px)';
  if(a===90){R.style.setProperty('--sl',L);R.style.setProperty('--sr','0px');}else if(a===270){R.style.setProperty('--sl','0px');R.style.setProperty('--sr',Rt);}
  else{R.style.removeProperty('--sl');R.style.removeProperty('--sr');}}
 side();addEventListener('orientationchange',function(){side();setTimeout(side,300);});addEventListener('resize',side);
 try{screen.orientation.addEventListener('change',side);}catch(e){}})();</script>
<script>/* splash: fade out once the first room has loaded (at least 1.1s, at most 9s) */
(function(){var t0=Date.now(),sp=document.getElementById('splash');if(!sp)return;
 function ready(){try{var sd=document.getElementById('idf-frame').contentDocument,g=sd&&sd.querySelector('.frames iframe:not(.off)'),gd=g&&g.contentDocument;
   return !!(gd&&gd.readyState==='complete'&&gd.body&&gd.body.childElementCount);}catch(e){return false;}}
 var iv=setInterval(function(){var el=Date.now()-t0;if((ready()&&el>1100)||el>9000){clearInterval(iv);setTimeout(function(){sp.classList.add('gone');setTimeout(function(){sp.remove();},600);},250);}},120);})();</script>
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
