"""CSS for the whole app: design tokens (light / dark), the lab components and
the Streamlit overrides.

Brand colours come from the Tuwaiq schools identity guide:
  blue #4d95ff, purple #4f29b6, light #f0f9ff, black #262626, font IBM Plex Sans Arabic.
The pink accent and the lavender tints come from the approved lab mock-up
(they are lab design colours, not Tuwaiq brand colours). Dark-mode surfaces are
derived from the brand black/purple."""
from __future__ import annotations

FONT_IMPORT = ("@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700"
               "&family=JetBrains+Mono:wght@400;600&family=Caveat:wght@600;700&display=swap');")

LIGHT = """
--bg:#f6f3ff; --bg-2:#f0f9ff; --panel:#ffffff; --panel-2:#faf8ff; --solid:#ffffff; --field:#ffffff; --gold:#f5c542;
--ink:#1d1550; --text:#38366a; --muted:#6b6a92;
--primary:#4f29b6; --primary-2:#6a3fd0; --on-primary:#ffffff;
--blue:#4d95ff; --accent:#4f29b6; --pink:#e04aa3; --pink-2:#ff7ac0;
--line:#e6e0f8; --lav:#efe9ff; --lav-2:#f7f3ff;
--hero:linear-gradient(135deg,#fff8ff 0%,#f3e9ff 48%,#e8f1ff 100%);
--header:linear-gradient(90deg,#ffffff 0%,#f6f1ff 55%,#eef6ff 100%);
--shadow:0 14px 34px rgba(79,41,182,.13); --shadow-s:0 6px 16px rgba(79,41,182,.10);
--ok:#1f9d55; --ok-bg:#e6f7ee; --warn:#a15c00; --warn-bg:#fff4dc; --bad:#c0392b; --bad-bg:#ffe9e6;
--code-bg:#1b1450; --code-ink:#efeaff; --logo-plate:transparent; --logo-blend:multiply;
--side:linear-gradient(180deg,#f3ecff 0%,#f6f3ff 100%);
"""

DARK = """
--bg:radial-gradient(1100px 640px at 85% -8%,#6a47e8 0%,transparent 62%),radial-gradient(900px 600px at -5% 28%,#3f24b4 0%,transparent 58%),linear-gradient(180deg,#2b1b92 0%,#1c1174 55%,#150c58 100%);
--bg-2:#1b1070; --panel:rgba(255,255,255,.075); --panel-2:rgba(255,255,255,.05); --solid:#2a1a90; --field:rgba(255,255,255,.10);
--ink:#ffffff; --text:#e9e4ff; --muted:#bcb2ee;
--primary:#6f4ef2; --primary-2:#8a6dff; --on-primary:#ffffff;
--blue:#7db4ff; --accent:#d3c8ff; --gold:#f5c542; --pink:#ff7ac0; --pink-2:#ff9ad0;
--line:rgba(255,255,255,.17); --lav:rgba(255,255,255,.11); --lav-2:rgba(255,255,255,.065);
--hero:linear-gradient(160deg,rgba(132,100,255,.55) 0%,rgba(70,42,190,.45) 55%,rgba(52,30,150,.5) 100%);
--header:linear-gradient(180deg,rgba(22,11,92,.78),rgba(30,17,116,.62));
--shadow:0 18px 40px rgba(8,2,50,.5); --shadow-s:0 8px 20px rgba(8,2,50,.35);
--ok:#6fe0a0; --ok-bg:rgba(60,200,130,.16); --warn:#ffd27a; --warn-bg:rgba(255,200,90,.15); --bad:#ff9a8d; --bad-bg:rgba(255,110,90,.16);
--code-bg:rgba(10,4,60,.75); --code-ink:#efeaff; --logo-plate:#ffffff; --logo-blend:normal;
--side:linear-gradient(180deg,rgba(24,12,100,.92) 0%,rgba(20,10,84,.95) 100%);
"""

LAB_CSS = r"""
.nl-root, .nl-root *{box-sizing:border-box}
.nl-root{font-family:'IBM Plex Sans Arabic','Segoe UI',Tahoma,Arial,sans-serif;color:var(--text);line-height:1.5}
.nl-root a{color:inherit}
.nl-ico{flex:none}

/* ---------------------------------------------------------------- header */
.nl-header{direction:ltr;display:flex;align-items:center;gap:14px;flex-wrap:nowrap;padding:8px 20px;
  background:var(--header);border-bottom:1px solid var(--line);height:72px;min-height:72px;box-sizing:border-box;overflow:hidden}
.nl-credit,.nl-school{display:flex;align-items:center;gap:10px;min-width:0;flex:none}
.nl-school .nl-ico{width:30px;height:30px}
.nl-credit .nl-ico,.nl-credit .nl-teacher-badge{color:var(--accent)}
.nl-teacher-badge{width:38px;height:auto;flex:none}
.nl-credit-text{direction:rtl;text-align:right;line-height:1.15}
.nl-credit-text small{display:block;font-size:13px;font-weight:600;color:var(--ink)}
.nl-credit-text b{display:block;font-size:17px;font-weight:700;color:var(--ink)}
.nl-school .nl-ico{color:var(--accent)}
.nl-school-text{direction:rtl;font-size:16px;white-space:nowrap;font-weight:600;color:var(--ink);line-height:1.2}
.nl-vsep{width:1px;align-self:stretch;min-height:34px;background:var(--line)}
.nl-grow{flex:1 1 20px}
.nl-logos{display:flex;align-items:center;gap:10px;background:var(--logo-plate);border-radius:12px;padding:3px 8px;flex:none}
.nl-logo-nasmo{width:50px;height:50px;border-radius:50%;object-fit:cover;display:block;box-shadow:var(--shadow-s)}
.nl-logo-inst{height:50px;width:auto;display:block;mix-blend-mode:var(--logo-blend)}

/* ------------------------------------------------------------------ hero */
.nl-hero-shell,.st-key-hero{position:relative;overflow:hidden;border-radius:30px;background:var(--hero);
  border:1px solid var(--line);padding:38px 44px 30px;isolation:isolate;margin:18px 26px 0;gap:0!important;container-type:inline-size}
.nl-hero-shell::before,.st-key-hero::before{content:"";position:absolute;border-radius:50%;z-index:-1;width:380px;height:380px;right:-60px;top:-140px;
  background:radial-gradient(circle,rgba(176,140,255,.38),transparent 68%)}
.nl-hero-shell::after,.st-key-hero::after{content:"";position:absolute;border-radius:50%;z-index:-1;width:300px;height:300px;left:-90px;bottom:-130px;
  background:radial-gradient(circle,rgba(255,122,192,.22),transparent 70%)}
.nl-hero{position:static;min-height:400px}
.nl-hero-text{position:relative;z-index:2;max-width:58%}
.nl-welcome{font-size:clamp(24px,2.6vw,38px);font-weight:500;color:var(--blue);letter-spacing:.2px}
.nl-title{margin:2px 0 0;white-space:nowrap;font-size:clamp(34px,6.1vw,88px);font-size:clamp(34px,5.2cqw,86px);line-height:1;font-weight:700;color:var(--ink);
  letter-spacing:-.025em;font-family:'IBM Plex Sans Arabic','Segoe UI',Arial,sans-serif}
.nl-title-row{display:flex;align-items:center;gap:22px;direction:ltr}
.nl-ar-block{display:flex;flex-direction:column;align-items:flex-start;line-height:1.35;padding-top:8px}
.nl-lab{font-size:clamp(28px,3.4vw,50px);font-size:clamp(28px,3.6cqw,56px);font-weight:700;color:var(--ink)}
.nl-ar-title{font-size:clamp(30px,3.9vw,56px);font-size:clamp(28px,3.9cqw,60px);font-weight:700;color:var(--ink);direction:rtl}
.nl-ar-tag{direction:rtl;font-size:clamp(15px,1.5vw,22px);font-weight:600;color:var(--ink);margin:0;padding:0}
.nl-tcc{display:flex;align-items:center;gap:0;flex-wrap:wrap;margin:6px 0 16px;color:var(--ink);font-weight:600;font-size:clamp(15px,1.5vw,22px)}
.nl-tcc span{display:inline-flex;align-items:center;gap:8px;padding:0 18px}
.nl-tcc span:first-child{padding-left:0}
.nl-tcc span+span{border-left:2px solid var(--ink)}
.nl-tcc .nl-ico{color:var(--accent)}
.nl-lede{font-size:clamp(15px,1.45vw,21px);line-height:1.55;color:var(--muted);max-width:640px;margin:0}
.nl-hero-art{position:absolute;right:0;top:0;width:54%;height:100%;z-index:1;pointer-events:none}
.nl-art-box{position:absolute;right:2%;top:5%;width:96%;aspect-ratio:740/470;max-height:92%}
.nl-art-box .nl-laptop{position:absolute;left:0;top:12%;width:100%;height:auto}
.nl-fl{position:absolute;display:block}
.nl-fl .nl-fg{position:absolute;inset:0;width:100%;height:100%;display:block}
.nl-fl-code .nl-fg{inset:7%;width:86%;height:86%}.nl-fl-trophy .nl-fg{inset:10%;width:80%;height:80%}.nl-fl-chart .nl-fg{inset:6%;width:88%;height:88%}
.nl-art-box{container-type:inline-size}
.nl-fl-code{left:15%;top:3%;width:21%;aspect-ratio:1.28;padding:6%;border-radius:18px;transform:rotate(-8deg);
  background:linear-gradient(145deg,rgba(255,255,255,.85),rgba(213,196,255,.75));border:1px solid rgba(255,255,255,.9);
  color:var(--primary-2);box-shadow:var(--shadow);backdrop-filter:blur(3px);animation:nl-float 7s ease-in-out infinite}
.nl-fl-trophy{left:62%;top:2%;width:13.5%;aspect-ratio:1;padding:10%;border-radius:20px;
  background:linear-gradient(145deg,#a98bff,#6a3fd0);box-shadow:var(--shadow);transform:rotate(5deg);animation:nl-float2 6s ease-in-out infinite .8s}
.nl-fl-note{left:78%;top:-1%;width:19.5%;aspect-ratio:.86;padding:9% 8%;border-radius:6px;transform:rotate(7deg);
  background:linear-gradient(160deg,#fffdf6,#fff1d4);box-shadow:0 12px 24px rgba(79,41,182,.18);animation:nl-float 8s ease-in-out infinite 1.4s;
  font-family:'Caveat','Comic Sans MS',cursive;font-weight:700;color:#2a1c6e;font-size:clamp(10px,1.4vw,20px);font-size:3.1cqw;line-height:1.02;text-align:left;overflow:visible}
.nl-fl-note::before{content:"";position:absolute;left:30%;top:-6%;width:40%;height:10%;background:rgba(255,122,192,.75);transform:rotate(-3deg);border-radius:2px}
.nl-fl-note i{position:absolute;right:10%;bottom:8%;width:16%;height:14%;background:var(--primary-2);
  clip-path:path('M10 18 C-6 6 4 -4 10 4 C16 -4 26 6 10 18Z');transform:scale(.8)}
.nl-fl-chart{left:76%;top:54%;width:21%;aspect-ratio:1.15;padding:5%;border-radius:16px;
  background:linear-gradient(145deg,rgba(255,255,255,.85),rgba(206,222,255,.8));border:1px solid rgba(255,255,255,.9);
  box-shadow:var(--shadow);animation:nl-float2 7.5s ease-in-out infinite .3s}
.nl-fl-sq{width:3.2%;aspect-ratio:1;border-radius:4px}
.nl-fl-sq.a{left:2%;top:34%;background:#ff9ad0;animation:nl-float 5s ease-in-out infinite}
.nl-fl-sq.b{left:6%;top:48%;width:4.2%;background:#c9b6ff;animation:nl-float2 6.5s ease-in-out infinite .5s}
.nl-fl-sq.c{left:1%;top:62%;width:2.4%;background:#9fb9ff;animation:nl-float 7s ease-in-out infinite 1s}
.nl-fl-sq.d{left:70%;top:42%;width:2.6%;background:#ff7ac0;animation:nl-float2 5.5s ease-in-out infinite .2s}
.nl-fl-spark{width:3.6%;aspect-ratio:1;animation:nl-twinkle 3.6s ease-in-out infinite}
.nl-fl-spark.a{left:58%;top:-2%;width:4.4%}
.nl-fl-spark.b{left:93%;top:36%;animation-delay:1.2s}
.nl-fl-spark.c{left:27%;top:92%;animation-delay:2.1s;width:3%}

/* ------------------------------------------------------------ stage cards */
.nl-stage-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}
.nl-card{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:14px 14px 16px;
  box-shadow:var(--shadow-s);transition:transform .22s ease,box-shadow .22s ease;height:100%;display:flex;flex-direction:column;min-height:318px;
  animation:nl-rise .6s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--i,0)*90ms)}
.nl-card:hover{transform:translateY(-5px);box-shadow:var(--shadow)}
.nl-card-top{position:relative;height:118px;margin:-2px -2px 8px;border-radius:16px;background:linear-gradient(160deg,var(--lav-2),var(--lav));overflow:hidden}
.nl-card-top .nl-card-art{position:absolute;inset:0;width:100%;height:100%}
.nl-badge{position:absolute;left:8px;top:6px;z-index:2;width:44px;height:44px;border-radius:50%;display:grid;place-items:center;
  font-weight:700;font-size:20px;color:var(--primary);background:linear-gradient(145deg,#ffd3ec,#e2d4ff);box-shadow:var(--shadow-s)}
.nl-card h3{margin:2px 0 0;font-size:21px;line-height:1.15;color:var(--ink);font-weight:700}
.nl-card h4{margin:2px 0 6px;font-size:16px;line-height:1.25;color:var(--primary);font-weight:600}
[data-nl="dark"] .nl-card h4{color:var(--accent)}
.nl-card p{margin:0;font-size:13.5px;line-height:1.5;color:var(--muted);flex:1}
.nl-card-foot{margin-top:12px}
.nl-bar{height:9px;border-radius:99px;background:var(--lav);overflow:hidden;position:relative}
.nl-bar>i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--pink-2),var(--primary-2));min-width:0}
.nl-card-meta{display:flex;align-items:center;justify-content:space-between;margin-top:10px}
.nl-card-meta b{font-size:16px;color:var(--ink);font-weight:700}
.nl-go{display:grid;place-items:center;width:46px;height:36px;border-radius:12px;background:linear-gradient(135deg,var(--primary-2),var(--primary));color:#fff;transition:transform .2s}
.nl-card:hover .nl-go{transform:translateX(3px)}
.nl-hint{font-size:12.5px;color:var(--muted)}

/* ---------------------------------------------------------------- sidebar */
.nl-login{display:flex;align-items:center;gap:12px;padding:14px 14px;border-radius:18px;background:var(--panel);
  border:1px solid var(--line);box-shadow:var(--shadow-s);transition:transform .2s,box-shadow .2s}
.nl-login:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
.nl-login.teacher{background:linear-gradient(135deg,#fff0fa,#f1e7ff)}
[data-nl="dark"] .nl-login.teacher{background:linear-gradient(135deg,#3a1f58,#2b2559)}
.nl-login .ic{color:var(--primary);width:40px;display:grid;place-items:center}
.nl-login.teacher .ic{color:var(--pink)}
.nl-login .tx{flex:1;min-width:0;line-height:1.2}
.nl-login .tx b{display:block;font-size:19px;color:var(--ink);font-weight:600}
.nl-login .tx small{display:block;font-size:12.5px;color:var(--muted)}
.nl-login .go{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:var(--primary);color:#fff}
.nl-login.teacher .go{background:var(--pink)}
.nl-who{padding:14px;border-radius:18px;background:var(--panel);border:1px solid var(--line);box-shadow:var(--shadow-s)}
.nl-who b{display:block;font-size:17px;color:var(--ink)}
.nl-who small{color:var(--muted);font-size:13px}
.nl-who .role{display:inline-block;margin-top:6px;padding:2px 10px;border-radius:99px;font-size:12px;font-weight:600;background:var(--lav);color:var(--primary)}
[data-nl="dark"] .nl-who .role{color:var(--accent)}
.nl-nav{display:flex;align-items:center;gap:14px;padding:12px 16px;border-radius:14px;font-size:19px;font-weight:500;color:var(--ink);
  transition:background .18s,transform .18s}
.nl-nav .nl-ico{color:var(--primary)}
[data-nl="dark"] .nl-nav .nl-ico{color:var(--accent)}
.nl-nav:hover{background:var(--lav)}
.nl-nav.on{background:linear-gradient(135deg,#3b1f95,var(--primary));color:#fff;box-shadow:0 8px 18px rgba(79,41,182,.32)}
.nl-nav.on .nl-ico{color:#fff}
.nl-deco{margin-top:6px;border-radius:20px;background:var(--panel);border:1px solid var(--line);padding:14px 10px 0;text-align:center;overflow:hidden;box-shadow:var(--shadow-s)}
.nl-deco .ar{direction:rtl;font-size:21px;font-weight:700;color:var(--ink);line-height:1.2}
.nl-deco .en{font-size:15px;font-weight:600;color:var(--ink);margin:2px 0 4px}
.nl-side-art{width:100%;height:auto;display:block;margin-top:2px}

/* ------------------------------------------------------- shared components */
.nl-panel{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:22px 24px;box-shadow:var(--shadow-s)}
.nl-h1{font-size:clamp(28px,3.2vw,42px);line-height:1.1;margin:0 0 6px;color:var(--ink);font-weight:700;letter-spacing:-.01em}
.nl-h2{font-size:24px;margin:0 0 10px;color:var(--ink);font-weight:700}
.nl-sub{color:var(--muted);font-size:16px;margin:0 0 14px;max-width:760px}
.nl-chip{display:inline-flex;align-items:center;gap:6px;padding:3px 11px;border-radius:99px;font-size:13px;font-weight:600;background:var(--lav);color:var(--primary)}
[data-nl="dark"] .nl-chip{color:var(--accent)}
.nl-chip.ok{background:var(--ok-bg);color:var(--ok)}.nl-chip.warn{background:var(--warn-bg);color:var(--warn)}.nl-chip.bad{background:var(--bad-bg);color:var(--bad)}
.nl-chip.demo{background:var(--warn-bg);color:var(--warn);border:1px dashed var(--warn)}
.nl-code{direction:ltr;text-align:left;background:var(--code-bg);color:var(--code-ink);border-radius:14px;padding:16px 18px;overflow:auto;
  font-family:'JetBrains Mono',Consolas,'Courier New',monospace;font-size:14px;line-height:1.55;margin:10px 0;white-space:pre;tab-size:4}
.nl-topic{display:flex;flex-direction:column;gap:2px;padding:12px 14px;border:1px solid var(--line);border-radius:14px;background:var(--panel-2);text-decoration:none;height:100%}
.nl-topic b{color:var(--ink);font-size:16px}.nl-topic span{color:var(--muted);font-size:13.5px}
.nl-topic em{font-style:normal;font-size:12.5px;font-weight:600;color:var(--primary);margin-top:4px}
[data-nl="dark"] .nl-topic em{color:var(--accent)}
a.nl-topic:hover{border-color:var(--primary-2);transform:translateY(-2px)}
.nl-topic-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.nl-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:8px 0 16px}
.nl-kpi{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:14px 16px;box-shadow:var(--shadow-s)}
.nl-kpi b{display:block;font-size:30px;line-height:1.1;color:var(--ink);font-weight:700}.nl-kpi span{font-size:14px;color:var(--muted)}
.nl-table{width:100%;border-collapse:collapse;font-size:14.5px;background:var(--panel);border-radius:14px;overflow:hidden}
.nl-table th{background:var(--lav);color:var(--ink);text-align:left;padding:10px 12px;font-weight:600;white-space:nowrap}
.nl-table td{padding:9px 12px;border-top:1px solid var(--line);color:var(--text);vertical-align:top}
.nl-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:14px}
.nl-note{border-radius:14px;padding:12px 16px;font-size:14.5px;border:1px solid var(--line);background:var(--lav-2);color:var(--text)}

.fm-card,.fm-post{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:14px 18px;margin:10px 0 2px}
.fm-card.pinned{border-color:var(--gold)}
.fm-post.best{border-color:var(--ok);box-shadow:0 0 0 1px var(--ok) inset}
.fm-post.q{padding:18px 20px}
.fm-title{margin:4px 0 6px;font-size:18px;color:var(--ink)}
.fm-qtitle{margin:2px 0 10px;font-size:22px;color:var(--ink)}
.fm-meta{font-size:13px;color:var(--muted)}
.fm-body{color:var(--text);line-height:1.8;font-size:15.5px;margin-bottom:10px;overflow-wrap:anywhere}
.fm-badges{display:flex;gap:6px;flex-wrap:wrap}
.fm-badge{font-size:12px;font-weight:700;padding:2px 10px;border-radius:999px;background:var(--lav);color:var(--ink)}
.fm-badge.ok{background:var(--ok-bg);color:var(--ok)} .fm-badge.pin{background:var(--gold);color:#3a2b00}
.fm-badge.teach{background:#6a47e8;color:#fff} .fm-badge.shut{background:var(--bad-bg);color:var(--bad)}
.fm-code{background:#14102f;color:#f1ecff;border-radius:12px;padding:12px 14px;overflow-x:auto;font-size:13.5px;line-height:1.6;margin:8px 0;text-align:left}
.fm-thanks{margin-inline-start:8px}
.nl-note.ok{background:var(--ok-bg);color:var(--ok);border-color:transparent}
.nl-note.bad{background:var(--bad-bg);color:var(--bad);border-color:transparent}
.nl-note.warn{background:var(--warn-bg);color:var(--warn);border-color:transparent}
.nl-explain{border-left:4px solid var(--primary-2);background:var(--lav-2);border-radius:0 14px 14px 0;padding:12px 16px;margin:10px 0;color:var(--text)}
.nl-explain .ar{direction:rtl;text-align:right;margin-top:6px;font-size:15.5px}
.nl-steps{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 12px}
.nl-step-dot{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:99px;font-size:13px;font-weight:600;background:var(--lav);color:var(--muted)}
.nl-step-dot.on{background:var(--primary);color:#fff}.nl-step-dot.done{background:var(--ok-bg);color:var(--ok)}
.nl-cert{position:relative;border:3px double var(--primary);border-radius:18px;padding:34px 40px;text-align:center;background:#fff;color:#1d1550}
.nl-footer{margin:26px 0 8px;text-align:center;color:var(--muted);font-size:13.5px}
.nl-mini-bar{display:flex;align-items:center;gap:10px}.nl-mini-bar .nl-bar{flex:1;min-width:60px}.nl-mini-bar span{font-size:13px;color:var(--muted);min-width:42px;text-align:right}

/* --------------------------------------------------------------- animation */
@keyframes nl-float{0%,100%{transform:translateY(0) rotate(var(--r,0deg))}50%{transform:translateY(-12px) rotate(calc(var(--r,0deg) + 1.5deg))}}
@keyframes nl-float2{0%,100%{transform:translateY(0)}50%{transform:translateY(10px)}}
@keyframes nl-twinkle{0%,100%{opacity:.25;transform:scale(.6)}50%{opacity:1;transform:scale(1.1)}}
@keyframes nl-rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes nl-sway{0%,100%{transform:rotate(-2deg)}50%{transform:rotate(2.5deg)}}
@keyframes nl-bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes nl-drift{0%,100%{transform:translate(0,0)}50%{transform:translate(9px,-5px)}}
@keyframes nl-drift2{0%,100%{transform:translate(0,0)}50%{transform:translate(-10px,4px)}}
@keyframes nl-pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.08);opacity:.85}}
@keyframes nl-flow{to{stroke-dashoffset:-20}}
@keyframes nl-flag{0%,100%{transform:skewY(0)}50%{transform:skewY(-6deg)}}
@keyframes nl-caret{0%,49%{opacity:.9}50%,100%{opacity:0}}
.nl-fl-code{--r:-8deg}.nl-fl-trophy{--r:5deg}.nl-fl-note{--r:7deg}
.nl-drift,.nl-drift2,.nl-sway,.nl-bob,.nl-bob2,.nl-pulse,.nl-pulse2,.nl-flag,.nl-tick{transform-box:fill-box;transform-origin:center}
.nl-sway{transform-origin:bottom center;animation:nl-sway 4.5s ease-in-out infinite}
.nl-bob{animation:nl-bob 3.4s ease-in-out infinite}.nl-bob2{animation:nl-bob 4s ease-in-out infinite .9s}
.nl-pulse{animation:nl-pulse 3.2s ease-in-out infinite}.nl-pulse2{animation:nl-pulse 3.8s ease-in-out infinite 1s}
.nl-flow{animation:nl-flow 1.2s linear infinite}
.nl-drift{animation:nl-drift 6s ease-in-out infinite}.nl-drift2{animation:nl-drift2 7.5s ease-in-out infinite .6s}
.nl-card:hover .nl-card-art{transform:scale(1.06)}.nl-card-art{transition:transform .35s ease}
.nl-card:hover .nl-bob,.nl-card:hover .nl-bob2{animation-duration:2s}
.nl-flag{transform-origin:left bottom;animation:nl-flag 2.8s ease-in-out infinite}
.nl-tick{transform-origin:center;animation:nl-sway 4s linear infinite}
.nl-caret{animation:nl-caret 1.1s steps(1) infinite}

.nl-side-logo{display:flex;justify-content:center;padding:4px 0 12px}
.nl-side-logo img{width:112px;height:112px;border-radius:50%;object-fit:cover;box-shadow:0 10px 26px rgba(20,8,90,.4);background:#fff}
/* ------------------------------------------------------ immersive glass look */
[data-nl="dark"] .nl-card,[data-nl="dark"] .nl-panel,[data-nl="dark"] .nl-kpi,[data-nl="dark"] .nl-mcard,[data-nl="dark"] .nl-login,
[data-nl="dark"] .nl-who,[data-nl="dark"] .nl-deco,[data-nl="dark"] .nl-qchip{backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.18),var(--shadow-s)}
[data-nl="dark"] .nl-hero-shell,[data-nl="dark"] .st-key-hero{border-color:rgba(255,255,255,.22);
  background:radial-gradient(rgba(255,255,255,.17) 1.1px,transparent 1.6px) 0 0/15px 15px,var(--hero);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.3),var(--shadow)}
[data-nl="dark"] .nl-title{text-shadow:0 6px 30px rgba(20,8,90,.45)}
.nl-lede{border-left:4px solid var(--gold);padding-left:14px}
.nl-welcome{display:inline-block;padding:2px 0}
.nl-tcc{display:inline-flex;padding:6px 6px;border-radius:18px;border:1px solid var(--line);background:var(--lav-2)}
.nl-tcc span{padding:2px 16px}
.nl-chips-title{font-size:15px;color:var(--muted);margin:18px 0 8px;font-weight:600}
.nl-qchip{display:flex;align-items:center;gap:12px;padding:8px 18px 8px 8px;border-radius:20px;background:var(--panel);
  border:1px solid var(--line);color:var(--ink);font-weight:600;font-size:17px;box-shadow:var(--shadow-s);transition:transform .2s,border-color .2s;height:100%}
.nl-qchip:hover{transform:translateY(-3px);border-color:var(--primary-2)}
.nl-qchip .tile{flex:none;width:48px;height:48px;border-radius:15px;display:grid;place-items:center;color:#fff;
  background:linear-gradient(145deg,var(--c1),var(--c2));box-shadow:inset 0 1px 0 rgba(255,255,255,.45),0 6px 14px rgba(0,0,0,.25)}
.nl-qchip small{display:block;font-size:12.5px;font-weight:500;color:var(--muted)}
/* bottom tab bar (phones) */
.nl-tab{display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 0 6px;color:var(--muted);font-size:12.5px;font-weight:600}
.nl-tab.on{color:#fff}.nl-tab.on .nl-ico{color:var(--gold)}
.nl-tab.plus .pl{width:58px;height:58px;margin-top:-26px;border-radius:20px;background:#fff;color:var(--primary);display:grid;
  place-items:center;box-shadow:0 0 0 7px rgba(255,255,255,.14),0 12px 24px rgba(8,2,50,.5)}
.nl-tab.plus span.t{display:none}
/* ---- sidebar: balanced (roomy enough to read, short enough to avoid scrolling) ---- */
.nl-side-logo{height:72px;margin:0 -14px 10px;padding:0;display:flex;align-items:center;justify-content:center;border-bottom:1px solid var(--line);background:var(--header)}
.nl-side-logo img{width:64px;height:64px}
.nl-login{padding:11px 13px;gap:11px;border-radius:16px}
.nl-login .ic{width:34px}.nl-login .ic .nl-ico{width:28px;height:28px}
.nl-login .tx b{font-size:16.5px}.nl-login .tx small{font-size:12px;line-height:1.25}
.nl-login .go{width:32px;height:32px}.nl-login .go .nl-ico{width:17px;height:17px}
.nl-who{padding:11px 14px;border-radius:16px}.nl-who b{font-size:15.5px}.nl-who small{font-size:12px}.nl-who .role{margin-top:4px;font-size:12px;padding:1px 10px}
.nl-nav{gap:13px;padding:10px 15px;border-radius:12px;font-size:16px}.nl-nav .nl-ico{width:22px;height:22px}
.nl-deco{margin-top:4px;padding:10px 10px 0;border-radius:16px}
.nl-deco .ar{font-size:16px;line-height:1.25}.nl-deco .en{font-size:12.5px;margin:0 0 2px}
.nl-deco{display:flex;flex-direction:column}.nl-deco .nl-side-art{width:46%;margin:auto auto 0}
[data-testid="stSidebarContent"]{padding:0 14px 8px!important}
@media(min-width:1024px){[data-testid="stSidebarCollapseButton"],[data-testid="stSidebarHeader"] button{display:none!important}}
[data-testid="stSidebarHeader"]{position:absolute!important;right:4px;top:4px;z-index:6;height:auto!important;min-height:0!important;padding:0!important;background:transparent!important}
[data-testid="stSidebarUserContent"]{padding-top:0!important}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:1.2rem!important}
[data-testid="stSidebar"] .stButton>button{min-height:0;padding:.38rem .8rem;font-size:14px}
[data-testid="stSidebar"] .stCaption,[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{font-size:11.5px;margin:0}
/* ----------------------------------------------------------- responsive */
@media (max-width:1250px){.nl-stage-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:900px){
  .nl-header{padding:6px 10px 6px 68px;gap:8px}.nl-vsep{display:none}.nl-school{display:none}.nl-grow{display:block;flex:1 1 0}
  .nl-credit-text small{display:none}.nl-credit-text b{font-size:14px}.nl-teacher-badge{width:30px}
  .nl-logo-nasmo{width:36px;height:36px}.nl-logo-inst{height:36px}.nl-logos{gap:6px;padding:2px 6px}
  .nl-hero-shell,.st-key-hero{padding:26px 20px 22px;margin:12px 12px 0}.nl-hero{min-height:0}
  .nl-hero-text{max-width:100%}
  .nl-hero-art{position:relative;width:100%;height:auto;margin-top:14px}
  .nl-art-box{position:relative;right:auto;top:auto;width:100%;max-height:none}
    .nl-btn.ghost,.nl-btn.solid{min-width:0;width:100%}
  .nl-stage-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:560px){.nl-stage-grid{grid-template-columns:1fr}.nl-fl-note{font-size:3cqw;padding:10% 4%;overflow-wrap:normal;word-break:normal}}

/* gentle motion (switchable from the sidebar) */
@keyframes nl-dots{to{background-position:60px 30px,0 0}}
@keyframes nl-shine{0%,70%{transform:translateX(-120%) skewX(-20deg)}100%{transform:translateX(260%) skewX(-20deg)}}
@keyframes nl-glow{0%,100%{box-shadow:0 0 0 7px rgba(255,255,255,.14),0 12px 24px rgba(8,2,50,.5)}50%{box-shadow:0 0 0 12px rgba(255,255,255,.07),0 12px 28px rgba(138,109,255,.6)}}
.nl-hero-text>*{animation:nl-rise .7s cubic-bezier(.2,.7,.2,1) both}
.nl-hero-text>*:nth-child(2){animation-delay:.08s}.nl-hero-text>*:nth-child(3){animation-delay:.16s}.nl-hero-text>*:nth-child(4){animation-delay:.24s}
.nl-hero-text>*:nth-child(5){animation-delay:.32s}.nl-hero-text>*:nth-child(6){animation-delay:.4s}
[data-nl="dark"] .nl-hero-shell,[data-nl="dark"] .st-key-hero{animation:nl-dots 40s linear infinite}
.st-key-hero_start button{position:relative;overflow:hidden}
.st-key-hero_start button::after{content:"";position:absolute;top:0;bottom:0;width:40%;left:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.35),transparent);animation:nl-shine 4.5s ease-in-out infinite}
.nl-tab.plus .pl{animation:nl-glow 2.8s ease-in-out infinite}
.nl-nav .nl-ico,.nl-qchip .tile{transition:transform .25s}.nl-nav:hover .nl-ico{transform:scale(1.18) rotate(-6deg)}
.nl-login .go{transition:transform .25s}.nl-login:hover .go{transform:translateX(4px)}
.nl-kpi,.nl-mcard{animation:nl-rise .5s both}
"""

# Streamlit-specific overrides ------------------------------------------------
STREAMLIT_CSS = r"""
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--text)}
.stApp{font-family:'IBM Plex Sans Arabic','Segoe UI',Tahoma,Arial,sans-serif}
[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important}
[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important}
[data-testid="stMainBlockContainer"],.block-container{padding:0 0 2rem 0!important;max-width:100%!important}
[data-testid="stSidebar"]{background:var(--side)!important;border-right:1px solid var(--line)}
@media (min-width:1024px){[data-testid="stSidebar"]{min-width:300px!important;max-width:300px!important}}
@media (max-width:1023px){
  /* phones and tablets: Streamlit's own sidebar (it slides over the page). Its open button lives in the toolbar we hide
     on desktop, so here the toolbar is kept (without its menu / deploy actions) and the open button becomes a round button. */
  [data-testid="stHeader"]{height:0!important;min-height:0!important;overflow:visible!important}
  [data-testid="stToolbar"]{display:block!important;visibility:visible!important;height:0!important;min-height:0!important;background:transparent!important;overflow:visible!important}
  [data-testid="stToolbarActions"],[data-testid="stMainMenu"],[data-testid="stAppDeployButton"],[data-testid="stStatusWidget"],.stDeployButton,#MainMenu{display:none!important}
  [data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"],[data-testid="collapsedControl"]{
    display:flex!important;visibility:visible!important;opacity:1!important;position:fixed!important;top:13px!important;bottom:auto!important;left:12px!important;
    right:auto!important;z-index:1000003!important;width:48px!important;height:48px!important;min-width:0!important;border-radius:50%!important;
    align-items:center;justify-content:center;padding:0!important;margin:0!important;color:#fff!important;
    background:linear-gradient(135deg,#8a63e6,#5b34d6)!important;box-shadow:0 6px 18px rgba(40,22,130,.5)!important}
  [data-testid="stSidebarCollapsedControl"] *,[data-testid="stExpandSidebarButton"] *,[data-testid="collapsedControl"] *{color:#fff!important;fill:#fff!important}
  /* show a classic menu icon instead of the small arrow */
  [data-testid="stExpandSidebarButton"] > *,[data-testid="stSidebarCollapsedControl"] button > *,[data-testid="collapsedControl"] button > *{display:none!important}
  [data-testid="stExpandSidebarButton"]::after,[data-testid="stSidebarCollapsedControl"] button::after,[data-testid="collapsedControl"] button::after{content:"\2630";font-size:24px;line-height:1;color:#fff}
  [data-testid="stSidebarCollapsedControl"] button,[data-testid="collapsedControl"] button{background:transparent!important;border:0!important;width:100%;height:100%;display:flex;align-items:center;justify-content:center}
  [data-testid="stSidebar"]{max-width:86vw!important;position:fixed!important;top:0!important;bottom:0!important;left:0!important;z-index:1000002!important;box-shadow:0 0 40px rgba(10,4,60,.55)}
  /* never let the page scroll sideways */
  html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{overflow-x:hidden!important;max-width:100vw}
  [data-testid="stMainBlockContainer"]{padding-left:0!important;padding-right:0!important}
}
[data-testid="stSidebar"] > div:first-child{background:transparent!important}
[data-testid="stSidebarContent"]{padding:14px 14px 18px!important}
[data-testid="stSidebarUserContent"]{padding-top:0!important}
h1,h2,h3,h4,h5,h6,label,p,li,span,div[data-testid="stMarkdownContainer"]{color:inherit}
.nl-pad{padding:18px 26px}
@media (max-width:900px){.nl-pad{padding:14px 14px}}
.nl-hero-shell{min-width:0}

/* overlay buttons: a transparent real button on top of a styled card */
[class*="st-key-ov_"]{position:relative;gap:0!important}
[class*="st-key-ov_"] [data-testid="stElementContainer"]{margin:0!important}
[class*="st-key-ov_"] [data-testid="stButton"],[class*="st-key-ov_"] .stButton{position:absolute!important;inset:0;margin:0!important;z-index:5}
[class*="st-key-ov_"] button{width:100%!important;height:100%!important;min-height:0!important;opacity:0;cursor:pointer;padding:0!important;border-radius:20px!important}
[class*="st-key-ov_"] button:focus-visible{opacity:1;outline:3px solid var(--blue);background:transparent!important;color:transparent!important}
[class*="st-key-ov_"][class*="_nav_"] button{border-radius:14px!important}

/* normal Streamlit buttons */
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{border-radius:12px;font-weight:600;border:1px solid var(--line);
  background:var(--panel);color:var(--ink);padding:.5rem 1.1rem;transition:transform .15s,box-shadow .15s,background .15s}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--primary-2);color:var(--primary);transform:translateY(-1px)}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button[kind="primaryFormSubmit"],.stButton>button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,var(--primary-2),var(--primary));color:#fff!important;border:none;box-shadow:0 8px 18px rgba(79,41,182,.3)}
.stButton>button[kind="primary"] p{color:#fff!important}
[data-nl="dark"] .stButton>button:hover{color:var(--accent)}


/* button text must follow the theme (Streamlit's own theme is light) */
.stButton>button,.stButton>button p,.stButton>button span,.stButton>button div,
.stDownloadButton>button,.stDownloadButton>button p,[data-testid="stFormSubmitButton"]>button p{color:var(--ink)!important}
.stButton>button[kind="primary"] p,.stButton>button[kind="primary"] span,[data-testid="stFormSubmitButton"]>button[kind="primaryFormSubmit"] p{color:#fff!important}
[data-testid="stSidebar"] .stButton>button{background:var(--lav)!important;border:1px solid var(--line)!important;font-weight:600}
[data-testid="stSidebar"] .stButton>button:hover{background:var(--lav-2)!important;border-color:var(--primary-2)!important}
/* Selected navigation items use a high-contrast purple surface and white text. */
[data-testid="stSidebar"] .stButton>button[kind="primary"],
[data-testid="stSidebar"] .stButton>button[data-testid^="stBaseButton-primary"] {background:linear-gradient(135deg,var(--primary-2),var(--primary))!important;border:1px solid var(--primary)!important;color:#fff!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"] *,
[data-testid="stSidebar"] .stButton>button[data-testid^="stBaseButton-primary"] * {color:#fff!important}
.stButton>button:hover p{color:var(--primary)!important}


/* readable text everywhere in both themes (Streamlit's own theme is light) */
.stTabs [data-baseweb="tab"] p,.stTabs [data-baseweb="tab"] div,.stTabs [data-baseweb="tab"] span{color:var(--text)!important;font-weight:600}
.stTabs [data-baseweb="tab"][aria-selected="true"] p,.stTabs [data-baseweb="tab"][aria-selected="true"] div{color:var(--ink)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--gold)!important}
.stTabs [data-baseweb="tab-border"]{background:var(--line)!important}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label,label p,.stRadio label p,.stCheckbox label p,.stToggle label p{color:var(--text)!important}
[data-testid="stExpander"] summary p,[data-testid="stExpander"] summary span{color:var(--ink)!important}
.stMarkdown p,.stMarkdown li,.stMarkdown strong,[data-testid="stCaptionContainer"] p{color:var(--text)!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:var(--muted)!important;opacity:1}
[data-testid="stForm"] button p{color:inherit}


/* tabs + buttons: robust selectors for every Streamlit 1.4x markup variant */
[role="tab"],[role="tab"] *{color:var(--text)!important;font-weight:600}
[role="tab"][aria-selected="true"],[role="tab"][aria-selected="true"] *{color:var(--ink)!important}
button[data-testid^="stBaseButton-primary"],button[data-testid="stBaseButton-primaryFormSubmit"]{background:linear-gradient(135deg,var(--primary-2),var(--primary))!important;border:none!important;box-shadow:0 8px 18px rgba(79,41,182,.3)}
button[data-testid^="stBaseButton-primary"] *,button[data-testid="stBaseButton-primaryFormSubmit"] *{color:#fff!important}
button[data-testid^="stBaseButton-secondary"],button[data-testid="stBaseButton-secondaryFormSubmit"]{background:var(--panel)!important;border:1px solid var(--line)!important}
button[data-testid^="stBaseButton-secondary"] *,button[data-testid="stBaseButton-secondaryFormSubmit"] *{color:var(--ink)!important}
[data-testid="stFormSubmitButton"] button *{color:inherit!important}
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"],[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] *{color:#fff!important}

/* Login and registration fields: force readable contrast even when Streamlit's
   native light theme overrides custom input styles. Keep passwords readable as bullets. */
div[data-testid="stForm"] input,
div[data-testid="stTextInput"] input,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-baseweb="input"] input,
[data-baseweb="base-input"] input {
  color:#1d1550 !important;
  -webkit-text-fill-color:#1d1550 !important;
  background-color:#ffffff !important;
  caret-color:#4f29b6 !important;
  opacity:1 !important;
}
div[data-testid="stForm"] input::placeholder,
.stTextInput input::placeholder {
  color:#77718f !important;
  -webkit-text-fill-color:#77718f !important;
  opacity:1 !important;
}
/* inputs */
.stTextInput input,.stTextArea textarea,.stNumberInput input,[data-baseweb="select"]>div,[data-baseweb="input"]{
  background:var(--field)!important;color:var(--ink)!important;border-color:var(--line)!important;border-radius:12px!important}
.stTextArea textarea{font-family:'JetBrains Mono',Consolas,monospace;font-size:14px}
.stTextInput label,.stTextArea label,.stRadio label,.stSelectbox label,.stCheckbox label,.stToggle label{color:var(--text)!important}
[data-baseweb="popover"] *{color:var(--ink)}
[data-baseweb="menu"],[data-baseweb="popover"]>div{background:var(--solid)!important}
div[data-testid="stForm"]{border:1px solid var(--line);border-radius:18px;background:var(--panel);padding:18px}
div[data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:14px!important;background:var(--panel)}
div[data-testid="stExpander"] summary{color:var(--ink)}
/* expander header must keep the page colours in every state (hover, focus, open, click) - dark mode showed white */
div[data-testid="stExpander"] details,div[data-testid="stExpander"] details>summary,
div[data-testid="stExpander"] details>summary:hover,div[data-testid="stExpander"] details>summary:focus,
div[data-testid="stExpander"] details>summary:focus-visible,div[data-testid="stExpander"] details>summary:active,
div[data-testid="stExpander"] details[open]>summary{background:transparent!important;background-color:transparent!important;color:var(--ink)!important;box-shadow:none!important;outline:none}
div[data-testid="stExpander"] details>summary:hover{background:var(--lav-2)!important}
div[data-testid="stExpander"] [data-baseweb="base-input"],div[data-testid="stExpander"] [data-baseweb="input"],
div[data-testid="stExpander"] input{background:var(--field)!important;color:var(--ink)!important}
div[data-testid="stExpander"] summary svg{color:var(--ink)!important;fill:currentColor}
.stTabs [data-baseweb="tab"]{color:var(--muted)}.stTabs [aria-selected="true"]{color:var(--primary)!important}
[data-nl="dark"] .stTabs [aria-selected="true"]{color:var(--accent)!important}
div[data-testid="stAlert"]{border-radius:14px}
div[data-testid="stRadio"] label{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:8px 14px;margin:3px 0;width:100%}
div[data-testid="stRadio"] label:has(input:checked){border-color:var(--primary-2);background:var(--lav)}
a:focus-visible,button:focus-visible{outline:3px solid var(--blue)!important;outline-offset:2px}

/* hero buttons are real Streamlit buttons styled as pills */
.st-key-hero{padding-bottom:34px!important}
.st-key-hero [data-testid="stHorizontalBlock"]{gap:16px!important;margin-top:26px;position:relative;z-index:6;flex-wrap:wrap}
.st-key-hero [data-testid="stColumn"]{min-width:260px!important;flex:0 0 auto!important;width:auto!important}
.st-key-hero_kit button,.st-key-hero_start button{border-radius:999px!important;white-space:pre-line;text-align:left;justify-content:space-between;min-height:64px;
  font-size:19px!important;font-weight:600!important;min-width:270px;line-height:1.15}
.st-key-hero_kit button{border:2px solid var(--pink)!important;background:rgba(255,255,255,.6)!important;color:var(--ink)!important;padding:8px 24px!important}
[data-nl="dark"] .st-key-hero_kit button{background:rgba(255,255,255,.08)!important}
.st-key-hero_start button{border:none!important;background:linear-gradient(135deg,var(--primary-2),var(--primary))!important;color:#fff!important;
  min-width:330px;min-height:64px;font-size:21px!important;box-shadow:0 10px 22px rgba(79,41,182,.35)}
.st-key-hero_start button p,.st-key-hero_start button span{color:#fff!important}
.st-key-hero_kit button p{color:var(--ink)!important}

/* bottom tab bar container */
.st-key-tabbar{display:none}
@media (max-width:900px){
  .st-key-tabbar{display:block;position:fixed;left:0;right:0;bottom:0;z-index:999;background:linear-gradient(180deg,rgba(60,38,170,.96),rgba(40,22,130,.98));
    border-top:1px solid var(--line);padding:2px 6px calc(20px + env(safe-area-inset-bottom));backdrop-filter:blur(16px);overflow:visible}
  body:has([class*="viewerBadge"]) .st-key-tabbar{right:64px}
  .st-key-tabbar [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:0!important}
  .st-key-tabbar [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important}
  [data-testid="stMainBlockContainer"],.block-container{padding-bottom:90px!important}
  [class*="st-key-ov_tab_"] button{border-radius:12px!important}
}
/* responsive grids built from st.columns */
[class*="st-key-grid_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:14px!important}
[class*="st-key-grid_"] [data-testid="stColumn"]{flex:1 1 calc(20% - 14px)!important;min-width:calc(20% - 14px)!important;width:auto!important}
[class*="st-key-grid3_"] [data-testid="stColumn"]{flex:1 1 calc(33.3% - 14px)!important;min-width:260px!important}
@media (max-width:1250px){[class*="st-key-grid_"] [data-testid="stColumn"]{flex-basis:calc(33.3% - 14px)!important;min-width:calc(33.3% - 14px)!important}}
@media (max-width:900px){[class*="st-key-grid_"] [data-testid="stColumn"]{flex-basis:calc(50% - 14px)!important;min-width:calc(50% - 14px)!important}}
@media (max-width:560px){[class*="st-key-grid_"] [data-testid="stColumn"]{flex-basis:100%!important;min-width:100%!important}}
.st-key-pagepad{padding:18px 26px}
@media (max-width:900px){.st-key-pagepad{padding:14px}}
.nl-mcard{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:14px 16px;box-shadow:var(--shadow-s);height:100%;
  display:flex;flex-direction:column;gap:6px;transition:transform .2s,box-shadow .2s}
.nl-mcard:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
.nl-mcard h4{margin:0;font-size:18px;color:var(--ink);font-weight:700;line-height:1.25}
.nl-mcard p{margin:0;font-size:14px;color:var(--muted);flex:1}
.nl-mcard .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.nl-qtype{display:inline-block;font-weight:700;font-size:13px;color:var(--primary);background:var(--lav);border-radius:99px;padding:3px 12px}
[data-nl="dark"] .nl-qtype{color:var(--accent)}
.nl-prompt{font-size:18px;line-height:1.55;color:var(--ink);margin:8px 0 4px;white-space:pre-wrap}
.nl-ar-s{direction:rtl;text-align:right}

@media (max-width:900px){.nl-hero-art{margin-bottom:34px!important}.st-key-hero [data-testid="stHorizontalBlock"]{margin-top:18px;gap:12px!important}.st-key-hero [data-testid="stColumn"]{min-width:100%!important;flex:1 1 100%!important}.st-key-hero_kit button,.st-key-hero_start button{min-width:0;width:100%}}
"""


RTL_CSS = r"""
/* Arabic: the page content reads right-to-left; the sidebar stays where Streamlit puts it. */
[data-testid="stMain"],[data-testid="stSidebarContent"],[data-testid="stMainBlockContainer"]{direction:rtl;text-align:right}
.nl-root{text-align:right}
pre,code,.nl-code,textarea,[data-testid="stTextArea"] textarea,.nl-code *{direction:ltr!important;text-align:left!important}
input{text-align:start}
[data-testid="stTextInput"] input[type="text"],[data-testid="stTextInput"] input[type="password"]{direction:ltr;text-align:right}
[data-testid="stMain"] [data-testid="stRadio"] label,[data-testid="stMain"] [data-testid="stCheckbox"] label{flex-direction:row}
@media(min-width:900px){[class*="st-key-qrowodd_"]{margin-left:0!important;margin-right:70px}}
.nl-hud,.nl-quest,.nl-world,.nl-trophy,.nl-loot,.nl-nova-say{direction:rtl}
/* English titles inside Arabic text (mission names, C++) keep their own order, e.g. "Hello, C++!" */
.nl-root :is(h1,h2,h3,h4,p,b,span,div,li,label,td,th){unicode-bidi:plaintext}
.nl-nova-say .bubble::before{left:auto;right:-8px;transform:translateY(-50%) rotate(225deg)}
/* Streamlit's built-in English hint "Press Enter to submit form" cannot be translated and overlaps the Arabic placeholder */
[data-testid="InputInstructions"],[data-testid="stTextInput"] [data-testid="InputInstructions"],[data-testid="stTextArea"] [data-testid="InputInstructions"]{display:none!important}
/* hero: the picture moves to the left, the text to the right */
.nl-hero-art{right:auto;left:0;width:46%}
.nl-hero-text{max-width:52%}
.nl-title-row{direction:rtl}
.nl-ar-block{align-items:flex-start}
.nl-lede{border-left:0;padding-left:0;border-right:4px solid var(--gold);padding-right:14px}
.nl-fl-note{font-family:'IBM Plex Sans Arabic','Segoe UI',sans-serif;font-size:2.2cqw;line-height:1.5;text-align:center;direction:rtl;padding:12% 5%;word-break:keep-all;overflow-wrap:normal}
@media(max-width:900px){.nl-hero-art{width:100%;left:auto}.nl-hero-text{max-width:100%}}
.nl-art-box{direction:ltr}
.nl-hero-shell::before,.st-key-hero::before{right:auto;left:-60px}
.nl-hero-shell::after,.st-key-hero::after{left:auto;right:-90px}
.st-key-hero_kit button,.st-key-hero_start button{text-align:right}
"""


def build_css(theme: str = "light", animate: bool = True, lang: str = "en") -> str:
    vars_ = DARK if theme == "dark" else LIGHT
    scheme = "dark" if theme == "dark" else "light"
    from .game_css import GAME_CSS
    css = f"{LAB_CSS}\n{STREAMLIT_CSS}\n{GAME_CSS}"
    if lang == "ar":
        css += "\n" + RTL_CSS
    if not animate:       # the person switched motion off
        css += "\n*,*::before,*::after{animation:none!important;transition:none!important}"
    if theme == "dark":   # no attribute on <html> inside Streamlit: make the dark-only rules apply directly
        css = css.replace('[data-nl="dark"] ', ':root:root ')
    return f"<style>{FONT_IMPORT}\n:root{{{vars_}color-scheme:{scheme};}}\n{css}</style>"


def build_css_static(theme: str = "light") -> str:
    """Same CSS for the standalone preview page (no Streamlit overrides)."""
    vars_ = DARK if theme == "dark" else LIGHT
    return (f"<style>:root{{{vars_}}}\nbody{{margin:0;background:var(--bg);}}\n{LAB_CSS}\n{__import__('nasmo.ui.game_css', fromlist=['x']).GAME_CSS}</style>")
