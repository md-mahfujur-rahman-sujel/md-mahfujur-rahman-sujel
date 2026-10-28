#!/usr/bin/env python3
"""Assemble the GitHub Pages mirror into _site/.

The README can only embed SVGs as <img>, which blocks pointer events and
strips target="_blank" from links. This build inlines the hero panel so the
reactor reacts to the cursor and every link can open in a new tab.
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / "_site"

USER = "md-mahfujur-rahman-sujel"
REPO = f"https://github.com/{USER}"
LINKEDIN = "https://linkedin.com/in/md-mahfujur-rahman-sujel"
APEX = f"{REPO}/Apex-Arcade"
UNROT = f"{REPO}/Unrot"
OPPZY = "https://github.com/masum-mir/Oppzy"

CSS = """
:root{
  --bg:#05080D; --bg2:#090F16; --chrome:#080E15; --rim:#16263A;
  --accent:#3B82F6; --accent2:#4F8DFF; --cyan:#67C7EB; --ice:#A9C7FF;
  --gold:#FBCA03; --bronze:#B97D10; --red:#AA0505; --maroon:#6A0C0B;
  --text:#EEF6FF; --muted:#93A6BA; --dim:#7E93A8;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
  --sans:"Segoe UI",system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 var(--sans);-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;background:
  radial-gradient(900px 520px at 10% -8%,rgba(59,130,246,.16),transparent 70%),
  radial-gradient(820px 520px at 92% 6%,rgba(103,199,235,.10),transparent 70%),
  radial-gradient(980px 620px at 50% 112%,rgba(106,12,11,.24),transparent 70%)}
.wrap{width:min(1180px,92vw);margin:0 auto;position:relative;z-index:1}

.site-head{position:sticky;top:0;z-index:30;background:rgba(5,8,13,.76);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid rgba(22,38,58,.7)}
.head-in{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:13px 0}
.brand{display:inline-flex;align-items:center;gap:10px;color:var(--text);text-decoration:none;
  font:800 14px/1 var(--mono);letter-spacing:.2em}
.brand .dot{width:9px;height:9px;border-radius:50%;background:var(--red);box-shadow:0 0 14px rgba(170,5,5,.95)}
.nav{display:flex;gap:6px;flex-wrap:wrap}
.nav a{font:600 11.5px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);
  text-decoration:none;padding:9px 12px;border-radius:999px;border:1px solid transparent;
  transition:color .25s,border-color .25s,background .25s}
.nav a:hover,.nav a:focus-visible{color:var(--text);border-color:var(--rim);background:rgba(22,38,58,.4)}
a:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:6px}

.hero{margin:30px 0 6px;border-radius:20px;overflow:hidden;
  box-shadow:0 40px 120px -60px rgba(59,130,246,.65),0 0 0 1px rgba(22,38,58,.35)}
.hero svg{display:block;width:100%;height:auto}

.chips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:24px 0 10px}
.chip{display:inline-flex;align-items:center;gap:9px;padding:11px 17px;border-radius:999px;
  border:1px solid rgba(22,38,58,.9);background:rgba(13,22,34,.7);color:var(--text);text-decoration:none;
  font:600 12.5px/1 var(--mono);letter-spacing:.06em;
  transition:transform .3s cubic-bezier(.2,.7,.2,1),border-color .3s,background .3s,box-shadow .3s}
.chip .pip{width:6px;height:6px;border-radius:50%;background:var(--c,var(--accent2));box-shadow:0 0 10px var(--c,var(--accent2))}
.chip:hover{transform:translateY(-2px);border-color:rgba(251,202,3,.6);
  background:rgba(22,38,58,.55);box-shadow:0 14px 34px -22px rgba(79,141,255,.9)}

section{padding:14px 0 6px}
.kicker{margin:0 0 10px;font:600 11px/1 var(--mono);letter-spacing:.24em;text-transform:uppercase;color:var(--bronze)}
h2{margin:0 0 12px;font:700 clamp(22px,2.3vw,29px)/1.2 var(--sans);letter-spacing:-.015em}
.lead{margin:0 0 18px;max-width:72ch;color:var(--muted)}
.lead strong{color:var(--text);font-weight:600}
.panel{display:block;width:100%;height:auto}
.divider{display:block;width:100%;height:auto;margin:26px 0;opacity:.9}

.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.card{display:block;border-radius:18px;text-decoration:none;
  transition:transform .35s cubic-bezier(.2,.7,.2,1),box-shadow .35s}
.card img{display:block;width:100%;height:auto}
.card:hover{transform:translateY(-5px);box-shadow:0 26px 64px -34px rgba(79,141,255,.8)}
.card:focus-visible{outline-offset:5px}

.links{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:16px 0 4px}
.links a{color:var(--muted);text-decoration:none;font:600 13px/1 var(--mono);letter-spacing:.05em;
  padding:8px 13px;border-radius:999px;border:1px solid rgba(22,38,58,.9)}
.links a:hover{color:var(--text);border-color:rgba(251,202,3,.55);background:rgba(22,38,58,.45)}

footer{margin:44px 0 64px;padding-top:22px;border-top:1px solid rgba(22,38,58,.6);
  text-align:center;color:var(--dim);font:12.5px/1.9 var(--mono);letter-spacing:.04em}
footer a{color:var(--muted);text-decoration:none}
footer a:hover{color:var(--gold)}

@media (max-width:900px){
  .cards{grid-template-columns:1fr}
  .head-in{flex-direction:column;align-items:flex-start;gap:10px}
}
/* Skybot: original mascot. Roams by default; click to follow the cursor. */
#flyer{position:fixed;left:0;top:0;z-index:20;pointer-events:none;will-change:transform}
#flyer[hidden]{display:none}
#flyer-btn{pointer-events:auto;display:block;width:64px;height:94px;padding:0;margin:0;border:0;background:none;cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent;will-change:transform}
#flyer-btn svg{display:block;width:100%;height:100%;overflow:visible;filter:drop-shadow(0 10px 14px rgba(0,0,0,.55))}
#flyer-btn:focus-visible{outline:2px solid var(--gold);outline-offset:4px;border-radius:14px}
.sk-thrust{transform-origin:0 26px;transform:scaleY(var(--thrust,1))}
.sk-flame{transform-origin:0 26px;animation:skflick .16s ease-in-out infinite alternate}
@keyframes skflick{from{transform:scaleY(.82)}to{transform:scaleY(1.14)}}
.sk-spark{position:fixed;left:0;top:0;width:6px;height:6px;margin:-3px 0 0 -3px;border-radius:50%;pointer-events:none;z-index:19}
.nav .nav-btn{font:600 11.5px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--bronze);background:transparent;border:1px solid rgba(185,125,16,.5);padding:9px 12px;border-radius:999px;cursor:pointer;transition:color .25s,border-color .25s}
.nav .nav-btn:hover,.nav .nav-btn:focus-visible{color:var(--gold);border-color:var(--gold)}
@media (prefers-reduced-motion:reduce){.sk-flame{animation:none}}

/* dashboard panels keep their density: pan sideways instead of shrinking to illegible type */
.panel-scroll{overflow-x:auto;overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch}
.panel-scroll img{display:block;width:100%;height:auto}
@media (max-width:820px){
  .hero{overflow-x:auto}
  .hero svg,.panel-scroll img{min-width:900px}
  .panel-scroll{scrollbar-color:var(--rim) transparent}
  .panel-scroll::-webkit-scrollbar{height:6px}
  .panel-scroll::-webkit-scrollbar-thumb{background:var(--rim);border-radius:3px}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .chip,.card,.nav a{transition:none}
  .chip:hover,.card:hover{transform:none}
}
"""

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Md Mahfujur Rahman Sujel — software engineering student</title>
<meta name="description" content="BSc in Computer Science &amp; Engineering at East West University, Bangladesh. Live GitHub telemetry, projects and activity.">
<meta name="theme-color" content="#05080D">
<meta name="color-scheme" content="dark">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<style>__CSS__</style>
</head>
<body id="top">
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="#top"><span class="dot"></span>SUJEL.OS</a>
    <nav class="nav" aria-label="Primary">
      <a href="__REPO__" target="_blank" rel="noopener noreferrer">GitHub</a>
      <a href="__LINKEDIN__" target="_blank" rel="noopener noreferrer">LinkedIn</a>
      <a href="#projects">Projects</a>
      <a href="#telemetry">Telemetry</a>
      <button class="nav-btn" id="flyer-toggle" type="button" aria-pressed="true">Skybot: on</button>
    </nav>
  </div>
</header>

<main class="wrap">
  <div class="hero">__HERO__</div>

  <div class="chips">
    <a class="chip" href="__LINKEDIN__" target="_blank" rel="noopener noreferrer"><span class="pip" style="--c:#4F8DFF"></span>LinkedIn</a>
    <a class="chip" href="__REPO__" target="_blank" rel="noopener noreferrer"><span class="pip" style="--c:#A9C7FF"></span>GitHub</a>
  </div>

  <img class="divider" src="assets/divider-v4.svg" alt="" width="1280" height="36">

  <section id="about" aria-labelledby="about-h">
    <p class="kicker">01 — about</p>
    <h2 id="about-h">Building products end to end</h2>
    <p class="lead">BSc in Computer Science &amp; Engineering at <strong>East West University, Bangladesh</strong>.
    I turn product ideas into working systems: from the first sketch in Figma to a shipped, polished release.</p>
  </section>

  <section id="projects" aria-labelledby="projects-h">
    <p class="kicker">02 — projects</p>
    <h2 id="projects-h">Selected work</h2>
    <div class="cards">
      <a class="card" href="__APEX__" target="_blank" rel="noopener noreferrer"><img src="assets/project-apex-v4.svg" alt="Apex Arcade — React launcher for 50 browser games" width="400" height="320"></a>
      <a class="card" href="__UNROT__" target="_blank" rel="noopener noreferrer"><img src="assets/project-unrot-v4.svg" alt="Unrot — Android app blocker with a focus timer" width="400" height="320"></a>
      <a class="card" href="__OPPZY__" target="_blank" rel="noopener noreferrer"><img src="assets/project-oppzy-v4.svg" alt="Oppzy — internship and research matching platform" width="400" height="320"></a>
    </div>
  </section>

  <img class="divider" src="assets/divider-v4.svg" alt="" width="1280" height="36">

  <section id="stack" aria-labelledby="stack-h">
    <p class="kicker">03 — stack</p>
    <h2 id="stack-h">Tools in rotation</h2>
    <div class="panel-scroll"><img class="panel" src="assets/stack-v4.svg" alt="JavaScript, TypeScript, React, HTML, CSS, Bootstrap, Figma, Java, Spring Boot, MySQL, Kotlin, Git, GitHub, Android Studio, UI/UX" width="1280" height="176"></div>
  </section>

  <section id="telemetry" aria-labelledby="telemetry-h">
    <p class="kicker">04 — telemetry</p>
    <h2 id="telemetry-h">Live from GitHub</h2>
    <div class="panel-scroll"><img class="panel" src="assets/telemetry.svg" alt="Live GitHub telemetry: contributions, streaks, active days and languages by bytes" width="1280" height="680"></div>
  </section>

  <section id="repositories" aria-labelledby="repos-h">
    <p class="kicker">05 — repositories</p>
    <h2 id="repos-h">Repository index</h2>
    <div class="panel-scroll"><img class="panel" src="assets/repos.svg" alt="Repository index with live metadata for Apex Arcade, Unrot and Oppzy" width="1280" height="432"></div>
    <p class="links">
      <a href="__APEX__" target="_blank" rel="noopener noreferrer">Apex-Arcade</a>
      <a href="__UNROT__" target="_blank" rel="noopener noreferrer">Unrot</a>
      <a href="__OPPZY__" target="_blank" rel="noopener noreferrer">Oppzy</a>
    </p>
  </section>

  <img class="divider" src="assets/divider-v4.svg" alt="" width="1280" height="36">

  <section id="activity" aria-labelledby="activity-h">
    <p class="kicker">06 — activity</p>
    <h2 id="activity-h">Recent activity</h2>
    <div class="panel-scroll"><img class="panel" src="assets/activity.svg" alt="Recent public GitHub activity feed" width="1280" height="384"></div>
    <p class="links">
      <a href="__REPO__" target="_blank" rel="noopener noreferrer">full contribution graph on GitHub</a>
    </p>
  </section>

  <footer>
    East West University · Bangladesh · <a href="__REPO__" target="_blank" rel="noopener noreferrer">github.com/__USER__</a><br>
    Panels refresh every 3 hours via GitHub Actions.
  </footer>
</main>
<div id="flyer"><button id="flyer-btn" type="button" aria-pressed="false" aria-label="Skybot is roaming. Activate to make it follow your cursor."><svg viewBox="-40 -56 80 118" width="64" height="94" aria-hidden="true" focusable="false">
<g class="sk-thrust"><g class="sk-flame"><path d="M-8 26Q0 58 8 26Z" fill="#AA0505"/><path d="M-5 26Q0 46 5 26Z" fill="#FBCA03"/><path d="M-2.2 26Q0 36 2.2 26Z" fill="#FFFFFF"/></g></g>
<path d="M-18 6L-36 20L-18 22Z" fill="#3B82F6" stroke="#16263A" stroke-width="2.4" stroke-linejoin="round"/>
<path d="M18 6L36 20L18 22Z" fill="#3B82F6" stroke="#16263A" stroke-width="2.4" stroke-linejoin="round"/>
<path d="M-17 -2Q-19 22-9 26H9Q19 22 17-2Z" fill="#4F8DFF" stroke="#16263A" stroke-width="2.6" stroke-linejoin="round"/>
<rect x="-10" y="8" width="20" height="9" rx="3.5" fill="#EEF6FF" stroke="#16263A" stroke-width="1.8"/>
<rect x="-6.5" y="11.5" width="13" height="2.4" rx="1.2" fill="#FBCA03"/>
<rect x="-10" y="24" width="20" height="6" rx="3" fill="#6A0C0B" stroke="#16263A" stroke-width="1.8"/>
<ellipse cx="-21" cy="10" rx="4.6" ry="6.4" fill="#EEF6FF" stroke="#16263A" stroke-width="2.2"/>
<ellipse cx="21" cy="10" rx="4.6" ry="6.4" fill="#EEF6FF" stroke="#16263A" stroke-width="2.2"/>
<path d="M0 -37V-47" stroke="#16263A" stroke-width="2.8" stroke-linecap="round"/>
<circle cx="0" cy="-49" r="3.8" fill="#FBCA03" stroke="#16263A" stroke-width="1.8"/>
<circle cx="0" cy="-16" r="22" fill="#EEF6FF" stroke="#16263A" stroke-width="2.8"/>
<path d="M13 -4Q22 -12 20 -24" fill="none" stroke="#A9C7FF" stroke-width="3" stroke-linecap="round" opacity=".7"/>
<rect x="-16" y="-25" width="32" height="17" rx="8.5" fill="#05080D" stroke="#16263A" stroke-width="1.8"/>
<ellipse cx="-6.5" cy="-16.5" rx="3.4" ry="4.2" fill="#67C7EB"/>
<ellipse cx="6.5" cy="-16.5" rx="3.4" ry="4.2" fill="#67C7EB"/>
</svg></button></div>
<script>
(function(){
var root=document.getElementById('flyer'),btn=document.getElementById('flyer-btn'),tog=document.getElementById('flyer-toggle');
if(!root||!btn){return;}
var svg=btn.querySelector('svg');
var reduce=window.matchMedia?window.matchMedia('(prefers-reduced-motion: reduce)'):{matches:false};
var W=window.innerWidth,H=window.innerHeight;
var pos={x:W*0.78,y:H*0.62},vel={x:0,y:0},target={x:pos.x,y:pos.y},mouse={x:W/2,y:H/2};
var mode='roam',face=1,last=0,raf=0,pauseUntil=0,sparkAt=0,live=0,enabled=true,MAX=24;
function rnd(a,b){return a+Math.random()*(b-a);}
function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
function pick(){target.x=rnd(70,Math.max(120,W-70));target.y=rnd(110,Math.max(160,H-90));}
function place(){root.style.transform='translate3d('+(pos.x-32).toFixed(1)+'px,'+(pos.y-45).toFixed(1)+'px,0)';}
function dot(x,y,dx,dy,life,color){
  if(live>=MAX||!svg.animate){return;}
  var s=document.createElement('span');
  s.className='sk-spark';
  s.style.background=color;
  document.body.appendChild(s);
  live++;
  var a=s.animate([{transform:'translate('+x+'px,'+y+'px) scale(1)',opacity:1},{transform:'translate('+(x+dx)+'px,'+(y+dy)+'px) scale(0.1)',opacity:0}],{duration:life,easing:'ease-out'});
  a.onfinish=function(){live--;if(s.parentNode){s.parentNode.removeChild(s);}};
}
function burst(){
  for(var i=0;i<14;i++){var a=Math.random()*6.283,d=rnd(30,90);dot(pos.x,pos.y,Math.cos(a)*d,Math.sin(a)*d,rnd(450,800),Math.random()<0.5?'#FBCA03':'#AA0505');}
  if(svg.animate){svg.animate([{transform:'rotate(0deg)'},{transform:'rotate(360deg)'}],{duration:700,easing:'cubic-bezier(.2,.7,.2,1)'});}
}
function tick(t){
  raf=requestAnimationFrame(tick);
  var dt=last?Math.min((t-last)/1000,0.05):0.016;last=t;
  if(mode==='follow'){target.x=clamp(mouse.x+70,40,W-40);target.y=clamp(mouse.y+54,60,H-50);}
  else if(Math.hypot(target.x-pos.x,target.y-pos.y)<26){
    if(!pauseUntil){pauseUntil=t+rnd(500,1500);}
    else if(t>pauseUntil){pauseUntil=0;pick();}
  }
  var k=mode==='follow'?24:7,c=mode==='follow'?9.5:5;
  vel.x+=((target.x-pos.x)*k-vel.x*c)*dt;
  vel.y+=((target.y-pos.y)*k-vel.y*c)*dt;
  pos.x+=vel.x*dt;pos.y+=vel.y*dt;
  var speed=Math.hypot(vel.x,vel.y);
  if(Math.abs(vel.x)>25){face+=((vel.x>0?1:-1)-face)*Math.min(1,dt*12);}
  var tilt=clamp(vel.x*0.035,-20,20);
  btn.style.transform='translateY('+(Math.sin(t/430)*3).toFixed(2)+'px) rotate('+tilt.toFixed(2)+'deg) scaleX('+face.toFixed(3)+')';
  svg.style.setProperty('--thrust',(1+Math.min(speed/450,1)).toFixed(2));
  if(speed>170&&t>sparkAt){sparkAt=t+75;dot(pos.x,pos.y+34,rnd(-8,8),rnd(20,44),420,Math.random()<0.5?'#FBCA03':'#AA0505');}
  place();
}
function settle(){pos.x=W-60;pos.y=H-80;btn.style.transform='none';place();}
function sync(){
  cancelAnimationFrame(raf);raf=0;
  if(!enabled){return;}
  if(reduce.matches){settle();return;}
  last=0;raf=requestAnimationFrame(tick);
}
function setMode(m){
  mode=m;
  btn.setAttribute('aria-pressed',m==='follow'?'true':'false');
  btn.setAttribute('aria-label',m==='follow'?'Skybot is following your cursor. Activate to send it roaming.':'Skybot is roaming. Activate to make it follow your cursor.');
  if(m==='roam'){pick();}
}
function setEnabled(on){
  enabled=on;root.hidden=!on;
  if(tog){tog.setAttribute('aria-pressed',on?'true':'false');tog.textContent='Skybot: '+(on?'on':'off');}
  try{localStorage.setItem('skybot',on?'on':'off');}catch(err){}
  sync();
}
window.addEventListener('pointermove',function(e){mouse.x=e.clientX;mouse.y=e.clientY;},{passive:true});
window.addEventListener('pointerdown',function(e){mouse.x=e.clientX;mouse.y=e.clientY;},{passive:true});
window.addEventListener('resize',function(){W=window.innerWidth;H=window.innerHeight;pos.x=clamp(pos.x,40,W-40);pos.y=clamp(pos.y,60,H-50);if(reduce.matches&&enabled){settle();}});
btn.addEventListener('click',function(){if(!reduce.matches){burst();}setMode(mode==='roam'?'follow':'roam');});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&mode==='follow'){setMode('roam');}});
document.addEventListener('visibilitychange',function(){if(document.hidden){cancelAnimationFrame(raf);raf=0;}else{sync();}});
if(reduce.addEventListener){reduce.addEventListener('change',sync);}else if(reduce.addListener){reduce.addListener(sync);}
if(tog){tog.addEventListener('click',function(){setEnabled(!enabled);});}
var saved=null;try{saved=localStorage.getItem('skybot');}catch(err){}
setMode('roam');
place();
setEnabled(saved!=='off');
})();
</script>
</body>
</html>
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="8" fill="#05080D"/>
<path d="M16 5l9.5 5.5v11L16 27l-9.5-5.5v-11z" fill="none" stroke="#4F8DFF" stroke-width="1.4"/>
<circle cx="16" cy="16" r="4.6" fill="#67C7EB"/>
<circle cx="16" cy="16" r="7.6" fill="none" stroke="#A9C7FF" stroke-opacity=".5"/>
</svg>
"""


def inline_svg(path: Path) -> str:
    svg = path.read_text(encoding="utf-8").strip()
    if not svg.startswith("<svg"):
        raise SystemExit(f"{path.name}: expected a bare <svg> root")
    return svg.replace("<svg ", '<svg class="panel panel-hero" ', 1)


def main() -> None:
    hero = inline_svg(ASSETS / "hero-v4.svg")
    html = (
        HTML.replace("__CSS__", CSS.strip())
        .replace("__HERO__", hero)
        .replace("__REPO__", REPO)
        .replace("__LINKEDIN__", LINKEDIN)
        .replace("__APEX__", APEX)
        .replace("__UNROT__", UNROT)
        .replace("__OPPZY__", OPPZY)
        .replace("__USER__", USER)
    )

    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    for stale in (OUT / "assets").glob("*.svg"):
        stale.unlink()

    for asset in sorted(ASSETS.glob("*.svg")):
        shutil.copy2(asset, OUT / "assets" / asset.name)
    (OUT / "assets" / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    (OUT / "index.html").write_text(html, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}/index.html ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
