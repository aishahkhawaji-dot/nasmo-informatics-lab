"""CSS for the game layer (uses the theme variables from style.py)."""

GAME_CSS = r"""
/* ---------- mascot ---------- */
.nl-nova{display:block;overflow:visible;filter:drop-shadow(0 8px 14px rgba(8,2,50,.35))}
.nl-nova .nl-eyes{transform-origin:64px 66px;animation:nl-blink 4.6s infinite}
.nl-nova .nl-ant{animation:nl-ant 1.6s ease-in-out infinite;transform-origin:64px 22px}
.nl-nova .nl-wave{transform-origin:96px 112px;animation:nl-wave .7s ease-in-out infinite alternate}
@keyframes nl-blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}
@keyframes nl-ant{0%,100%{transform:scale(1);opacity:.8}50%{transform:scale(1.35);opacity:1}}
@keyframes nl-wave{from{transform:rotate(-14deg)}to{transform:rotate(16deg)}}
.nl-nova-say{display:flex;align-items:center;gap:14px;margin:8px 0}
.nl-nova-say .bubble{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:12px 16px;color:var(--ink);font-weight:600;max-width:520px;box-shadow:var(--shadow-s)}
.nl-nova-say .bubble::before{content:"";position:absolute;left:-8px;top:50%;width:14px;height:14px;background:var(--panel);border-left:1px solid var(--line);border-bottom:1px solid var(--line);transform:translateY(-50%) rotate(45deg)}

/* ---------- HUD ---------- */
.nl-hud{display:flex;gap:18px;align-items:center;padding:18px 22px;border-radius:26px;margin:10px 0 16px;color:#fff;position:relative;overflow:hidden;
  background:radial-gradient(circle at 90% 0,rgba(255,122,192,.35),transparent 45%),linear-gradient(120deg,#2b1a90,#4f29b6 55%,#8a2c8a);border:1px solid rgba(255,255,255,.25);box-shadow:var(--shadow)}
.nl-hud .av{flex:0 0 auto}
.nl-hud .body{flex:1;min-width:0}
.nl-hud .who{font-size:13px;opacity:.85;letter-spacing:.3px}
.nl-hud .rank{font-size:25px;font-weight:700;margin:2px 0 8px;color:#fff}
.nl-hud .xpbar{height:14px;border-radius:99px;background:rgba(255,255,255,.2);overflow:hidden;box-shadow:inset 0 2px 4px rgba(0,0,0,.25)}
.nl-hud .xpbar i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#ffd84d,#ff9ad0,#c4b5fd);background-size:200% 100%;animation:nl-xpflow 3.2s linear infinite}
@keyframes nl-xpflow{to{background-position:-200% 0}}
.nl-hud .nx{font-size:13px;margin:6px 0 10px;opacity:.92}
.nl-hud .chips{display:flex;flex-wrap:wrap;gap:8px}
.nl-gchip{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:99px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);font-size:13.5px;color:#fff}
.nl-gchip.hot{background:rgba(255,140,60,.35);border-color:#ffb36b;animation:nl-pulse-s 1.8s ease-in-out infinite}
@keyframes nl-pulse-s{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}
@media(max-width:700px){.nl-hud{flex-direction:column;text-align:center}.nl-hud .chips{justify-content:center}}

/* ---------- stars ---------- */
.nl-stars{display:inline-flex;gap:2px}.nl-stars i{font-style:normal;font-size:22px;color:rgba(160,150,200,.45)}
.nl-stars i.on{color:#ffd84d;text-shadow:0 0 12px rgba(255,216,77,.8)}
.nl-stars.sm i{font-size:15px}

/* ---------- world map ---------- */
.nl-mapintro{display:flex;align-items:center;gap:16px;margin:4px 0 6px}
.nl-world{position:relative;min-height:410px;display:flex;flex-direction:column;border-radius:26px;padding:16px 16px 14px;color:var(--ink);overflow:hidden;
  background:linear-gradient(160deg,var(--panel),var(--panel-2));border:1px solid var(--line);box-shadow:var(--shadow-s);transition:transform .25s,box-shadow .25s}
.nl-world:hover{transform:translateY(-4px);box-shadow:var(--shadow)}
.nl-world.cur{border-color:var(--gold);box-shadow:0 0 0 2px rgba(245,197,66,.45),var(--shadow);animation:nl-glow 2.6s ease-in-out infinite}
.nl-world .wtop{display:flex;align-items:center;gap:8px;min-height:26px}
.nl-world .wnum{width:28px;height:28px;border-radius:50%;display:grid;place-items:center;font-weight:700;background:var(--primary);color:#fff;font-size:14px}
.nl-world .here{font-size:10.5px;font-weight:700;letter-spacing:1.4px;padding:3px 9px;border-radius:99px;background:var(--gold);color:#3b2a00;animation:nl-pulse-s 1.6s infinite}
.nl-world .crown{margin-left:auto;font-size:24px;animation:nl-bob 3s ease-in-out infinite}
.nl-world .wart{height:128px;display:grid;place-items:center;margin:4px 0}.nl-world .wart svg{max-height:128px;width:auto;max-width:100%}
.nl-world .wname{font-size:21px;font-weight:700;color:var(--ink)}
.nl-world .wsub{font-size:12.5px;color:var(--accent);margin:2px 0 6px}
.nl-world .wline{font-size:13px;color:var(--muted);min-height:3.2em}
.nl-world .wfoot{display:flex;align-items:center;gap:12px;margin-top:auto;padding-top:8px}
.nl-world .ring{--p:0;width:54px;height:54px;border-radius:50%;display:grid;place-items:center;flex:0 0 auto;
  background:conic-gradient(var(--gold) calc(var(--p)*1%),var(--lav) 0)}
.nl-world .ring b{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;font-size:12px;background:var(--solid);color:var(--ink)}
.nl-world .wmeta{display:flex;flex-direction:column;gap:2px;font-size:13px;color:var(--text)}
.st-key-worldmap{position:relative}
.st-key-worldmap::before{content:"";position:absolute;left:6%;right:6%;top:46%;border-top:3px dashed rgba(245,197,66,.55);z-index:0;pointer-events:none}
@keyframes nl-dash{to{background-position:20px 0}}
[class*="st-key-world_go_"] button{border-radius:16px!important;font-weight:700!important;min-height:46px!important}

/* ---------- quest path ---------- */
.nl-quest{position:relative;display:flex;gap:16px;align-items:stretch;border-radius:22px;padding:14px 18px;background:linear-gradient(160deg,var(--panel),var(--panel-2));border:1px solid var(--line);box-shadow:var(--shadow-s);color:var(--ink)}
.nl-quest .node{flex:0 0 58px;height:58px;border-radius:50%;display:grid;place-items:center;align-self:center;font-size:23px;font-weight:700;background:var(--lav);color:var(--ink);border:3px solid var(--line)}
.nl-quest.done .node{background:linear-gradient(135deg,#ffd84d,#f59e0b);color:#3b2a00;border-color:#fff3b0;box-shadow:0 0 18px rgba(255,216,77,.55)}
.nl-quest.cur{border-color:var(--pink);box-shadow:0 0 0 2px rgba(255,122,192,.4),var(--shadow)}
.nl-quest.cur .node{background:linear-gradient(135deg,var(--pink-2),var(--pink));color:#fff;border-color:#ffd0ea;animation:nl-ring 1.8s ease-out infinite}
@keyframes nl-ring{0%{box-shadow:0 0 0 0 rgba(255,122,192,.7)}100%{box-shadow:0 0 0 18px rgba(255,122,192,0)}}
.nl-quest .qb{flex:1;min-width:0}
.nl-quest .qh{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.nl-quest .qn{font-size:11px;letter-spacing:1.6px;font-weight:700;color:var(--accent)}
.nl-quest h4{margin:2px 0 2px;font-size:18px;color:var(--ink)}
.nl-quest p{margin:0 0 6px;color:var(--muted);font-size:13.5px}
.nl-quest .qf{display:flex;gap:10px;flex-wrap:wrap;align-items:center;font-size:12.5px}
.nl-quest .rw{padding:3px 10px;border-radius:99px;background:var(--lav);color:var(--text)}
.nl-quest .steps{color:var(--muted)}
.nl-tag{font-size:11px;font-weight:700;padding:2px 9px;border-radius:99px;background:var(--lav);color:var(--text)}
.nl-tag.cur{background:var(--pink);color:#fff}.nl-tag.warn{background:var(--warn-bg);color:var(--warn)}
.nl-worldend{display:flex;gap:14px;align-items:center;border-radius:22px;padding:16px 20px;border:2px dashed var(--line);color:var(--muted);background:var(--lav-2)}
.nl-worldend .ic{font-size:38px;filter:grayscale(1)}.nl-worldend small{display:block}
.nl-worldend.on{border-style:solid;border-color:var(--gold);background:linear-gradient(120deg,rgba(245,197,66,.22),rgba(255,122,192,.15));color:var(--ink)}
.nl-worldend.on .ic{filter:none;animation:nl-bob 2.4s ease-in-out infinite}
[class*="st-key-qrow"]{position:relative}
@media(min-width:900px){
  [class*="st-key-qrowodd_"]{margin-left:70px}
}
[class*="st-key-qrow"] [data-testid="stButton"] button{min-height:52px;font-weight:700;border-radius:16px}

/* ---------- mission HUD ---------- */
.nl-qsteps{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:6px 0 12px}
.nl-qsteps .path{display:flex;align-items:center}
.nl-qsteps .s{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:14px;background:var(--lav);color:var(--muted);border:2px solid var(--line)}
.nl-qsteps .s.on{background:var(--pink);color:#fff;border-color:#ffd0ea;animation:nl-ring 1.8s ease-out infinite}
.nl-qsteps .s.done{background:var(--gold);color:#3b2a00;border-color:#fff3b0}
.nl-qsteps em{width:22px;height:3px;background:var(--line);display:block}
.nl-qsteps .pot{font-size:13px;color:var(--text);background:var(--lav);padding:5px 12px;border-radius:99px}

/* ---------- fx ---------- */
.nl-win{position:relative;border-radius:22px;padding:16px 20px;margin:10px 0;border:1px solid var(--ok);background:linear-gradient(120deg,var(--ok-bg),rgba(245,197,66,.16));color:var(--ink);overflow:visible;animation:nl-pop .5s cubic-bezier(.2,1.4,.4,1)}
.nl-win .xp{font-size:30px;font-weight:700;color:var(--gold);text-shadow:0 2px 0 rgba(0,0,0,.25);animation:nl-float 1.4s ease-out}
.nl-win .ft{font-size:12px;font-weight:700;background:var(--pink);color:#fff;padding:2px 9px;border-radius:99px;vertical-align:middle;margin-left:8px}
.nl-win .cmb{display:inline-block;margin-left:8px;font-weight:700;color:#ffb36b}
.nl-win .say{display:flex;align-items:center;gap:10px;margin-top:4px;font-weight:600}
@keyframes nl-pop{0%{transform:scale(.8);opacity:0}100%{transform:scale(1);opacity:1}}
@keyframes nl-float{0%{transform:translateY(18px);opacity:0}30%{opacity:1}100%{transform:translateY(0)}}
.nl-confetti{position:absolute;left:50%;top:0;width:0;height:0;pointer-events:none;z-index:20}
.nl-confetti i{position:absolute;left:0;top:0;width:var(--s);height:calc(var(--s)*1.6);background:var(--c);border-radius:2px;opacity:0;animation:nl-conf 2.2s var(--d) ease-out forwards}
@keyframes nl-conf{0%{opacity:1;transform:translate(0,0) rotate(0)}100%{opacity:0;transform:translate(var(--x),380px) rotate(var(--r))}}

/* ---------- victory ---------- */
.nl-victory{position:relative;text-align:center;border-radius:30px;padding:26px 22px 22px;margin:10px 0 16px;color:#fff;overflow:hidden;
  background:radial-gradient(circle at 50% -10%,rgba(255,216,77,.45),transparent 55%),linear-gradient(160deg,#3a1fa8,#5b2ab8 55%,#8a2c8a);border:1px solid rgba(255,255,255,.3);box-shadow:var(--shadow)}
.nl-victory .vt{text-transform:uppercase;letter-spacing:4px;font-size:12px;font-weight:700;color:#ffe9a0}
.nl-victory h2{color:#fff;margin:6px 0 4px;font-size:28px}
.nl-victory .vstars{display:flex;justify-content:center;gap:10px;margin:8px 0}
.nl-victory .vstars i{font-style:normal;font-size:58px;color:rgba(255,255,255,.22);transform:scale(.4);opacity:0;animation:nl-starin .7s cubic-bezier(.2,1.6,.4,1) forwards;animation-delay:calc(.25s + var(--k)*.35s)}
.nl-victory .vstars i.on{color:#ffd84d;text-shadow:0 0 24px rgba(255,216,77,.9)}
@keyframes nl-starin{0%{transform:scale(.2) rotate(-40deg);opacity:0}100%{transform:scale(1) rotate(0);opacity:1}}
.nl-victory .vsay{display:flex;align-items:center;justify-content:center;gap:12px;font-weight:600;margin:4px 0 12px}
.nl-victory .vrows{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:6px 0 14px}
.nl-victory .vrows div{min-width:110px;padding:10px 16px;border-radius:16px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);animation:nl-pop .6s .9s both}
.nl-victory .vrows small{display:block;font-size:12px;opacity:.85}.nl-victory .vrows b{font-size:24px}
.nl-chest{display:flex;flex-direction:column;align-items:center;margin:8px 0 14px}
.nl-chest .lid{transform-box:fill-box;transform-origin:0% 100%;animation:nl-lid 1s 1.2s cubic-bezier(.3,1.5,.5,1) forwards}
.nl-chest svg{animation:nl-shake .6s .5s 2}
.nl-chest .loot{height:92px;margin-bottom:-14px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;opacity:0;animation:nl-loot 1s 1.7s ease-out forwards;position:relative;z-index:2}
.nl-chest .ln{margin-top:4px;opacity:0;animation:nl-loot 1s 1.9s ease-out forwards}
.nl-chest .le{font-size:54px;line-height:1;filter:drop-shadow(0 0 14px rgba(255,216,77,.9))}
@keyframes nl-lid{to{transform:rotate(-30deg) translate(-6px,-8px)}}
@keyframes nl-shake{0%,100%{transform:rotate(0)}25%{transform:rotate(-5deg)}75%{transform:rotate(5deg)}}
@keyframes nl-loot{0%{opacity:0;transform:translateY(40px) scale(.3)}100%{opacity:1;transform:translateY(0) scale(1)}}
.nl-newtro,.nl-levelup{display:flex;gap:14px;align-items:center;text-align:left;margin:8px auto;max-width:520px;padding:12px 16px;border-radius:18px;background:rgba(255,255,255,.15);border:1px solid rgba(255,216,77,.7);animation:nl-pop .6s 2.3s both}
.nl-newtro span,.nl-levelup span{font-size:36px}.nl-newtro small,.nl-levelup small{display:block;opacity:.88}
.nl-levelup{background:linear-gradient(120deg,rgba(255,216,77,.35),rgba(255,122,192,.3));animation:nl-pop .6s 2.1s both,nl-pulse-s 1.6s 3s infinite}
.nl-newtro.world{border-color:#ffd0ea}

/* ---------- trophy room ---------- */
.nl-trophy{height:100%;text-align:center;padding:16px 12px;border-radius:22px;border:1px solid var(--line);background:linear-gradient(160deg,var(--panel),var(--panel-2));color:var(--ink);box-shadow:var(--shadow-s)}
.nl-trophy .ti{font-size:42px;line-height:1.2}
.nl-trophy b{display:block;margin-top:4px}.nl-trophy small{display:block;color:var(--muted);min-height:2.6em;margin:2px 0 8px;font-size:12.5px}
.nl-trophy .tb{height:8px;border-radius:99px;background:var(--lav);overflow:hidden}.nl-trophy .tb i{display:block;height:100%;background:linear-gradient(90deg,var(--pink),var(--gold));border-radius:99px}
.nl-trophy .tp{display:block;font-size:12px;margin-top:5px;color:var(--muted)}
.nl-trophy.on{border-color:var(--gold);box-shadow:0 0 0 1px rgba(245,197,66,.5),0 10px 24px rgba(245,197,66,.18)}
.nl-trophy.on .ti{animation:nl-bob 3.2s ease-in-out infinite}.nl-trophy.on .tp{color:var(--gold);font-weight:700}
.nl-trophy.off{opacity:.78}.nl-trophy.off .ti{filter:grayscale(1)}
.nl-loot{height:100%;text-align:center;padding:14px 10px;border-radius:20px;border:1px solid var(--line);background:var(--panel-2);color:var(--ink)}
.nl-loot .li{font-size:40px}.nl-loot small{display:block;color:var(--muted);font-size:12px}
.nl-loot.off{opacity:.55}.nl-loot.off .li{filter:grayscale(1)}
.nl-loot.on.bronze{border-color:#cd7f32}.nl-loot.on.silver{border-color:#c0c8d8;box-shadow:0 0 14px rgba(192,200,216,.4)}
.nl-loot.on.gold{border-color:var(--gold);box-shadow:0 0 18px rgba(245,197,66,.55);background:linear-gradient(160deg,rgba(245,197,66,.16),var(--panel-2))}
.nl-ladder{display:flex;gap:8px;flex-wrap:wrap}
.nl-ladder .rk{flex:1;min-width:120px;text-align:center;padding:10px 6px;border-radius:16px;background:var(--panel-2);border:1px solid var(--line);color:var(--muted)}
.nl-ladder .rk .ri{display:block;font-size:26px;filter:grayscale(1);opacity:.6}.nl-ladder .rk small{display:block;font-size:11px}
.nl-ladder .rk.on{color:var(--text)}.nl-ladder .rk.on .ri{filter:none;opacity:1}
.nl-ladder .rk.cur{border-color:var(--gold);color:var(--ink);background:rgba(245,197,66,.14)}.nl-ladder .rk.cur .ri{filter:none;opacity:1;animation:nl-bob 2.4s infinite}
@media (max-width:1100px){.nl-world .wfoot{flex-wrap:wrap;gap:6px 10px}.nl-world .nl-stars.sm i{font-size:13px}.nl-world .wname{font-size:19px}.nl-world .wmeta{font-size:12px}.st-key-worldmap::before{display:none}.nl-world{min-height:520px}}
"""
