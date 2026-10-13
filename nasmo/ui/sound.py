"""Small synthesized sound effects (Web Audio, no audio files, nothing downloaded).

The browser only allows sound after the person has clicked something, so the audio context is
created in the main page (which just received the click on "Check answer"), not in the tiny iframe
Streamlit uses to run the script."""
from __future__ import annotations

import itertools

_n = itertools.count(1)

SOUND_JS = r"""
(function(kinds,stars){
  try{
    var P=(window.parent&&window.parent!==window)?window.parent:window;
    var AC=P.AudioContext||P.webkitAudioContext; if(!AC) return;
    var ctx=P.__nlAudio||(P.__nlAudio=new AC());
    if(ctx.state==='suspended') ctx.resume();
    function tone(f,t0,d,type,vol){
      var o=ctx.createOscillator(),g=ctx.createGain(),t=ctx.currentTime+t0;
      o.type=type||'sine'; o.frequency.setValueAtTime(f,t);
      g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(vol||0.16,t+0.02);
      g.gain.exponentialRampToValueAtTime(0.0001,t+d);
      o.connect(g); g.connect(ctx.destination); o.start(t); o.stop(t+d+0.05);
    }
    var R={
      correct:function(){tone(659,0,.14,'triangle');tone(988,.1,.3,'triangle');},
      wrong:function(){tone(220,0,.2,'sawtooth',.07);tone(165,.15,.28,'sawtooth',.07);},
      victory:function(){
        [523,659,784,1047].forEach(function(f,i){tone(f,i*.13,.34,'triangle',.17);});
        tone(1047,.55,.7,'sine',.14);
        for(var k=0;k<stars;k++){tone(880+k*220,.25+k*.35,.25,'sine',.15);}
      },
      trophy:function(){[1047,1319,1568,2093].forEach(function(f,i){tone(f,2.3+i*.09,.3,'sine',.11);});},
      levelup:function(){[392,523,659,784,1047].forEach(function(f,i){tone(f,2.1+i*.11,.36,'square',.07);});}
    };
    kinds.forEach(function(k){ if(R[k]) R[k](); });
  }catch(e){}
})(%KINDS%,%STARS%);
"""


def sound_html(kinds: list[str], stars: int = 3) -> str:
    """HTML for st.components.v1.html; the nonce makes every call a fresh iframe."""
    import json
    js = SOUND_JS.replace("%KINDS%", json.dumps(list(kinds))).replace("%STARS%", str(int(stars)))
    return f"<script>/*{next(_n)}*/{js}</script>"
