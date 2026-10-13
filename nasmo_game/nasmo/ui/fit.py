"""Keeps the sidebar aligned with the hero box on the home page: the first sidebar card starts where
the hero box starts and the last card ends where the hero box ends. Streamlit's real element heights
can only be known in the browser, so a tiny script measures them and adjusts the spacing."""

FIT_JS = r"""
(function(){
  var pdoc=(window.parent&&window.parent!==window)?window.parent.document:document;
  var pwin=pdoc.defaultView;
  if(pdoc.getElementById('nl-fit-script')){ if(pwin.__nlFit) pwin.__nlFit(); return; }
  var CODE = '('+function(){
    var doc=document, win=window, GAP=24;
    function fit(){
      try{
        var sb=doc.querySelector('[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"]')
            ||doc.querySelector('[data-testid="stSidebar"] [data-testid="stVerticalBlock"]')||doc.querySelector('.side');
        var hero=doc.querySelector('.st-key-hero')||doc.querySelector('.nl-hero-shell');
        if(hero) hero.style.minHeight='';
        if(!sb) return;
        var kids=Array.prototype.slice.call(sb.children);
        sb.style.removeProperty('row-gap');
        kids.forEach(function(k){k.style.removeProperty('margin-top');});
        var deco=sb.querySelector('.nl-deco'); if(deco) deco.style.minHeight='';
        if(!hero||!deco||win.innerWidth<=900) return;
        var hr=hero.getBoundingClientRect(); if(hr.height<80) return;
        var di=-1,bi=-1;
        kids.forEach(function(k,i){ if(k.contains(deco)) di=i; if(k.querySelector('.nl-side-logo')) bi=i; });
        if(bi<0||di<bi+2) return;
        var sumH=0; for(var i=bi+1;i<=di;i++) sumH+=kids[i].getBoundingClientRect().height;
        var gaps=di-bi-1, Hh=hr.height;
        var inner=Math.max(1,gaps), need=sumH+inner*GAP;
        if(Hh<need){ hero.style.boxSizing='border-box'; hero.style.minHeight=Math.ceil(need)+'px'; Hh=need; }
        var g=(Hh-sumH)/inner, remaining=0;
        if(g>34){ g=34; remaining=Hh-(sumH+inner*g); }
        sb.style.rowGap=g+'px';
        var band=kids[bi].getBoundingClientRect();
        var m=hr.top-(band.bottom+g);
        kids[bi+1].style.marginTop=m+'px';
        if(remaining>1) deco.style.minHeight=(deco.getBoundingClientRect().height+remaining)+'px';
      }catch(e){}
    }
    win.__nlFit=fit;
    var t=null; function later(){ clearTimeout(t); t=setTimeout(fit,120); }
    try{ new MutationObserver(later).observe(doc.body,{childList:true,subtree:true}); }catch(e){}
    win.addEventListener('resize',later); win.addEventListener('load',later);
    [200,700,1500,3000].forEach(function(ms){setTimeout(fit,ms);});
    fit();
  }.toString()+')();';
  var el=pdoc.createElement('script'); el.id='nl-fit-script'; el.text=CODE;
  (pdoc.head||pdoc.body).appendChild(el);
})();
"""
