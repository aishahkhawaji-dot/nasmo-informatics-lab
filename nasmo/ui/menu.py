"""Phone / tablet menu.

Streamlit's own "open sidebar" arrow lives in its toolbar, which this app hides, and its collapsed state is
unreliable on phones. So below 1024px the sidebar is our own slide-in drawer (see the max-width:1023px rules in
style.py): a round button adds/removes the class `nl-open` on <body>; the CSS does the rest. A dark backdrop closes
it, and so does tapping any button inside it (a page change re-draws the screen anyway) or pressing Escape."""

MENU_JS = r"""
(function(){
  var pdoc=(window.parent&&window.parent!==window)?window.parent.document:document;
  if(pdoc.getElementById('nl-menu-fab')) return;
  var body=pdoc.body;
  var fab=pdoc.createElement('button');
  fab.id='nl-menu-fab'; fab.type='button'; fab.setAttribute('aria-label','Menu'); fab.textContent='\u2630';
  var back=pdoc.createElement('div'); back.id='nl-backdrop';
  function set(open){
    body.classList.toggle('nl-open',!!open);
    fab.textContent=open?'\u2715':'\u2630';
  }
  fab.addEventListener('click',function(){ set(!body.classList.contains('nl-open')); });
  back.addEventListener('click',function(){ set(false); });
  pdoc.addEventListener('keydown',function(e){ if(e.key==='Escape') set(false); });
  pdoc.addEventListener('click',function(e){
    var t=e.target;
    if(t&&t.closest&&t.closest('[data-testid="stSidebar"] button')&&body.classList.contains('nl-open')){
      setTimeout(function(){ set(false); },250);
    }
  },true);
  body.appendChild(back); body.appendChild(fab);
})();
"""
