"""Phone menu button.

Streamlit's own "open sidebar" arrow lives inside its toolbar, which this app hides, so on a phone the
sidebar (navigation, theme, language) could not be opened. This script adds one round button to the page.
Tapping it clicks Streamlit's real open-sidebar control (found by its test id, which differs a little
between Streamlit versions). The button is only shown on small screens and only while the sidebar is closed
(see the #nl-menu-fab rules in style.py)."""

MENU_JS = r"""
(function(){
  var pdoc=(window.parent&&window.parent!==window)?window.parent.document:document;
  if(pdoc.getElementById('nl-menu-fab')) return;
  var b=pdoc.createElement('button');
  b.id='nl-menu-fab'; b.type='button'; b.textContent='☰'; b.setAttribute('aria-label','Menu');
  b.addEventListener('click',function(){
    var sels=['[data-testid="stExpandSidebarButton"]','[data-testid="stSidebarCollapsedControl"] button',
              '[data-testid="stSidebarCollapsedControl"]','[data-testid="collapsedControl"] button','[data-testid="collapsedControl"]'];
    for(var i=0;i<sels.length;i++){
      var el=pdoc.querySelector(sels[i]);
      if(el){ (el.tagName==='BUTTON'?el:(el.querySelector('button')||el)).click(); return; }
    }
  });
  pdoc.body.appendChild(b);
})();
"""
