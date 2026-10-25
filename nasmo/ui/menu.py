"""Phone menu helper.

On a phone Streamlit shows the sidebar as a panel that slides over the page, and it stays open after a menu item is
tapped, hiding the page that was just opened. This small script closes it after a navigation tap (not after the
theme / motion / sound / language switches). It only acts on phones and tablets (under 1024px). On tablets Streamlit docks the sidebar open, so it is also closed once when the\npage loads and drawn over the page (see style.py) instead of squeezing it."""

MENU_JS = r"""
(function(){
  var pdoc=(window.parent&&window.parent!==window)?window.parent.document:document;
  if(pdoc.getElementById('nl-nav-script')) return;
  /* the code is injected into the page itself: a listener created inside this small frame would die when Streamlit redraws it */
  var CODE='('+function(){
    var doc=document, win=window;
    doc.addEventListener('click',function(e){
      var t=e.target; if(!t||!t.closest) return;
      var b=t.closest('[data-testid="stSidebar"] button'); if(!b) return;
      if(win.innerWidth>=1024) return;
      if(b.closest('[data-testid="stSidebarCollapseButton"],[data-testid="stSidebarHeader"],[class*="st-key-btn_theme"],[class*="st-key-btn_anim"],[class*="st-key-btn_sound"],[class*="st-key-btn_lang"]')) return;
      setTimeout(function(){
        var c=doc.querySelector('[data-testid="stSidebarCollapseButton"] button')||doc.querySelector('[data-testid="stSidebarCollapseButton"]');
        if(c) c.click();
      },400);
    },true);
    /* tablets open the sidebar by default (it would squeeze the page): close it once when the page first loads */
    var tries=0, iv=setInterval(function(){
      tries++;
      if(win.innerWidth>=1024||tries>40){ clearInterval(iv); return; }
      var sb=doc.querySelector('[data-testid="stSidebar"]');
      var c=doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
      if(sb&&c&&sb.getAttribute('data-collapsed')==='false'){ c.click(); clearInterval(iv); }
      else if(sb&&sb.getAttribute('data-collapsed')==='true'){ clearInterval(iv); }
    },250);
  }+')();';
  var s=pdoc.createElement('script'); s.id='nl-nav-script'; s.textContent=CODE; pdoc.head.appendChild(s);
})();
"""
