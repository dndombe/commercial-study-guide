(function(){
var LS='cpl-guide-v1', done={};
try{ done=JSON.parse(localStorage.getItem(LS)||'{}'); }catch(e){ done={}; }
function save(){ try{ localStorage.setItem(LS,JSON.stringify(done)); }catch(e){} }

/* Which guides are switched on. `doc` is now a space-separated set, so a question
   that came from two guides shows while either of them is on. */
var SRCK='cpl-guide-src', KEYS=['chs','fi','gs','poh','acs'];
var on={chs:true, fi:true, gs:true, poh:true, acs:true};
try{
  var st0=JSON.parse(localStorage.getItem(SRCK)||'null');
  if(st0) KEYS.forEach(function(k){ if(k in st0) on[k]=!!st0[k]; });
}catch(e){}
function shows(d){
  var p=d.split(' ');
  for(var i=0;i<p.length;i++){ if(on[p[i]]) return true; }
  return false;
}

var items=[].slice.call(document.querySelectorAll('.it'));
var secs=[].slice.call(document.querySelectorAll('details.sec.qsec'));
items.forEach(function(li){ if(done[li.dataset.k]) li.classList.add('done'); });

var bar=document.querySelector('#prog i'), stat=document.getElementById('stat');
var live=items.length, ticked=0;

/* Progress counts only the questions the selected guides actually contain, so
   switching a guide off does not make you look behind on it. */
function paint(){
  var n=0, tot=0;
  secs.forEach(function(s){
    var li=[].slice.call(s.querySelectorAll('.it')).filter(function(x){ return shows(x.dataset.d); });
    var d=li.filter(function(x){ return x.classList.contains('done'); }).length;
    n+=d; tot+=li.length;
    s.querySelector('.sdone').textContent=d;
    s.querySelector('.sprog span').textContent=li.length;
    s.querySelector('.sbar i').style.width=(li.length?d/li.length*100:0)+'%';
  });
  live=tot; ticked=n;
  bar.style.width=(tot?n/tot*100:0).toFixed(1)+'%';
  paintStat();
}
function paintStat(shown){
  var base=ticked+' of '+live+' ticked  ·  '+(live-ticked)+' to go';
  if(shown===undefined || !toks.length){ stat.textContent=base; return; }
  stat.textContent=shown+(shown===1?' question matches':' questions match')+'  ·  '+base;
}

/* Figures live one per <script type="text/plain"> and are read into the img the
   first time its answer opens. Keeping them out of one big JSON block means the
   page does not parse several megabytes of base64 before it can draw. */
function hydrate(root){
  [].slice.call((root||document).querySelectorAll('.fg img[data-f]')).forEach(function(im){
    var el=document.getElementById('f_'+im.getAttribute('data-f'));
    if(el){ im.src=el.textContent; im.removeAttribute('data-f'); }
  });
}

document.addEventListener('click',function(e){
  var t=e.target.closest('.tick');
  if(t){ e.preventDefault();
    var li=t.closest('.it');
    li.classList.toggle('done');
    if(li.classList.contains('done')) done[li.dataset.k]=1; else delete done[li.dataset.k];
    save(); paint(); filter(); return; }
  var im=e.target.closest('.fg img');
  if(im){ im.closest('.fg').classList.toggle('zoom'); return; }
  var q=e.target.closest('.qb');
  if(q){ var l2=q.closest('.it'); l2.classList.toggle('open'); hydrate(l2); }
});

/* Searchable text is built once. Doing it per keystroke meant walking the text of
   every item, several of which contain a whole inline SVG diagram. */
var norm=function(s){ return s.toLowerCase().replace(/\s+/g,' '); };
secs.forEach(function(s){
  var sname=s.querySelector('.sname').textContent;
  [].slice.call(s.querySelectorAll('.it')).forEach(function(li){
    li._q=norm(li.querySelector('.qt').textContent);
    li._a=norm(li.querySelector('.ans').textContent);
    li._all=norm(li.textContent+' '+sname);
  });
});

var mode='all', toks=[], rawterm='';
var nores=document.getElementById('nores'), nrq=document.getElementById('nrq');

/* Highlight built from text nodes rather than innerHTML, so searching for "<" or
   "&" cannot break the markup. */
function highlight(li){
  var el=li.querySelector('.qt');
  if(el._o===undefined) el._o=el.textContent;
  if(!toks.length){
    if(el.childNodes.length!==1||el.firstChild.nodeType!==3) el.textContent=el._o;
    return;
  }
  var t=el._o, low=t.toLowerCase(), hits=[];
  toks.forEach(function(k){
    var i=low.indexOf(k);
    while(i>-1){ hits.push([i,i+k.length]); i=low.indexOf(k,i+k.length); }
  });
  if(!hits.length){ el.textContent=t; return; }
  hits.sort(function(a,c){ return a[0]-c[0]; });
  var merged=[hits[0]];
  for(var j=1;j<hits.length;j++){
    var last=merged[merged.length-1];
    if(hits[j][0]<=last[1]) last[1]=Math.max(last[1],hits[j][1]);
    else merged.push(hits[j]);
  }
  el.textContent='';
  var at=0;
  merged.forEach(function(r){
    if(r[0]>at) el.appendChild(document.createTextNode(t.slice(at,r[0])));
    var m=document.createElement('mark');
    m.textContent=t.slice(r[0],r[1]);
    el.appendChild(m);
    at=r[1];
  });
  if(at<t.length) el.appendChild(document.createTextNode(t.slice(at)));
}

var stash=null;
function remember(){ if(!stash) stash=secs.map(function(s){ return s.open; }); }
function restore(){
  if(!stash) return;
  secs.forEach(function(s,i){ s.open=stash[i]; });
  stash=null;
}

function filter(){
  var narrowed=(toks.length>0||mode!=='all'), shown=0;
  if(narrowed) remember(); else restore();
  items.forEach(function(li){
    var ok=shows(li.dataset.d);
    if(ok && mode==='todo' && li.classList.contains('done')) ok=false;
    if(ok && mode==='focus' && li.dataset.f!=='1') ok=false;
    if(ok && toks.length){
      for(var i=0;i<toks.length;i++){ if(li._all.indexOf(toks[i])<0){ ok=false; break; } }
    }
    li.classList.toggle('hide',!ok);
    if(ok){
      shown++;
      highlight(li);
      /* Say so when the words are only in the hidden answer, otherwise the question
         on screen looks unrelated to what was typed. */
      var inq=true, ina=true;
      for(var k=0;k<toks.length;k++){
        if(li._q.indexOf(toks[k])<0) inq=false;
        if(li._a.indexOf(toks[k])<0) ina=false;
      }
      li.classList.toggle('ansm', toks.length>0 && !inq && ina);
    } else {
      li.classList.remove('ansm');
    }
  });
  secs.forEach(function(s){
    var any=[].slice.call(s.querySelectorAll('.it')).some(function(l){ return !l.classList.contains('hide'); });
    s.classList.toggle('hide',!any);
    if(any && narrowed) s.open=true;
  });
  nores.classList.toggle('hide', !(toks.length && shown===0));
  if(toks.length && shown===0) nrq.textContent='“'+rawterm+'”';
  paintStat(shown);
}

[].slice.call(document.querySelectorAll('.fb[data-m]')).forEach(function(b){
  b.addEventListener('click',function(){
    [].slice.call(document.querySelectorAll('.fb[data-m]')).forEach(function(x){ x.classList.remove('on'); });
    b.classList.add('on'); mode=b.dataset.m; filter();
  });
});
var qbox=document.getElementById('q');
qbox.addEventListener('input',function(e){
  rawterm=e.target.value.trim();
  toks=rawterm.toLowerCase().split(/\s+/).filter(function(t){ return t.length>0; });
  filter();
});
document.getElementById('nrclear').addEventListener('click',function(){
  qbox.value=''; rawterm=''; toks=[]; filter(); qbox.focus();
});

var chips=[].slice.call(document.querySelectorAll('.src[data-src]'));
var shint=document.getElementById('shint');
function paintChips(){
  chips.forEach(function(c){ c.classList.toggle('on', !!on[c.dataset.src]); });
  var any=KEYS.some(function(k){ return on[k]; });
  shint.textContent = any ? '' : 'Nothing selected — turn a source back on.';
}
chips.forEach(function(c){
  c.addEventListener('click',function(){
    on[c.dataset.src]=!on[c.dataset.src];
    try{ localStorage.setItem(SRCK,JSON.stringify(on)); }catch(e){}
    paintChips(); paint(); filter();
  });
});
paintChips();
paint();
if(!KEYS.every(function(k){ return on[k]; })) filter();

var allOpen=false;
document.getElementById('expand').addEventListener('click',function(){
  allOpen=!allOpen;
  secs.forEach(function(s){ s.open=allOpen; });
  [].slice.call(document.querySelectorAll('.rsec,.ag')).forEach(function(s){ s.open=allOpen; });
  this.textContent=allOpen?'Collapse all':'Expand all';
});

var TK='cpl-guide-theme', tb=document.getElementById('theme');
function nowDark(){
  var d=document.documentElement.getAttribute('data-theme');
  if(d) return d==='dark';
  return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
}
function labelTheme(){ tb.textContent=nowDark()?'Light':'Dark'; }
try{ var th=localStorage.getItem(TK); if(th) document.documentElement.setAttribute('data-theme',th); }catch(e){}
labelTheme();
tb.addEventListener('click',function(){
  var next=nowDark()?'light':'dark';
  document.documentElement.setAttribute('data-theme',next);
  try{ localStorage.setItem(TK,next); }catch(e){}
  labelTheme();
});

/* Reset is two-tap rather than a browser confirm box: tap once to arm, tap again
   within four seconds to wipe. Tapping anything else disarms it. */
var rst=document.getElementById('reset'), armed=false, rt=null;
function disarm(){ armed=false; rst.classList.remove('armed'); rst.textContent='Reset progress'; }
rst.addEventListener('click',function(e){
  e.stopPropagation();
  if(!armed){ armed=true; rst.classList.add('armed'); rst.textContent='Tap again to erase';
    clearTimeout(rt); rt=setTimeout(disarm,4000); return; }
  done={}; save();
  items.forEach(function(l){ l.classList.remove('done'); });
  paint(); filter(); disarm();
});
document.addEventListener('click',function(e){ if(armed && !e.target.closest('#reset')) disarm(); });

/* ---- tabs ------------------------------------------------------------
   The toolbar belongs to the study pane; the other three have their own
   controls, so it is hidden rather than left there doing nothing. */
var TBK='cpl-guide-tab', toolbar=document.getElementById('bar');
var tabs=[].slice.call(document.querySelectorAll('.tb'));
function showTab(p){
  tabs.forEach(function(t){ t.classList.toggle('on', t.dataset.p===p); });
  [].slice.call(document.querySelectorAll('.pane')).forEach(function(s){
    s.classList.toggle('on', s.id==='p-'+p);
  });
  toolbar.style.display = (p==='study') ? '' : 'none';
  if(p!=='study') hydrate(document.getElementById('p-'+p));
  try{ localStorage.setItem(TBK,p); }catch(e){}
  window.scrollTo(0,0);
}
tabs.forEach(function(t){ t.addEventListener('click',function(){ showTab(t.dataset.p); }); });
try{ var sv=localStorage.getItem(TBK); if(sv) showTab(sv); }catch(e){}

/* ---- acronym pane ---------------------------------------------------- */
(function(){
  var box=document.getElementById('aq');
  if(!box) return;
  var ais=[].slice.call(document.querySelectorAll('.ai'));
  var ags=[].slice.call(document.querySelectorAll('.ag'));
  ais.forEach(function(a){ a._t=norm(a.textContent); });
  var at=0, atoks=[];
  function afilter(){
    ais.forEach(function(a){
      var ok=true;
      if(at && +a.dataset.t>at) ok=false;
      if(ok && atoks.length){
        for(var i=0;i<atoks.length;i++){ if(a._t.indexOf(atoks[i])<0){ ok=false; break; } }
      }
      a.classList.toggle('hide',!ok);
    });
    ags.forEach(function(g){
      var any=[].slice.call(g.querySelectorAll('.ai')).some(function(a){ return !a.classList.contains('hide'); });
      g.classList.toggle('hide',!any);
      if(any && (atoks.length||at)) g.open=true;
      g.querySelector('.agc').textContent=
        [].slice.call(g.querySelectorAll('.ai')).filter(function(a){ return !a.classList.contains('hide'); }).length;
    });
  }
  box.addEventListener('input',function(e){
    atoks=e.target.value.trim().toLowerCase().split(/\s+/).filter(function(t){ return t.length>0; });
    afilter();
  });
  [].slice.call(document.querySelectorAll('.fb[data-at]')).forEach(function(b){
    b.addEventListener('click',function(){
      [].slice.call(document.querySelectorAll('.fb[data-at]')).forEach(function(x){ x.classList.remove('on'); });
      b.classList.add('on'); at=+b.dataset.at; afilter();
    });
  });
})();

/* ---- weight and balance ----------------------------------------------
   The forward CG limit is a sloped line, so it has to be interpolated at the
   weight you are actually at rather than read off one corner of the envelope. */
(function(){
  var D=__WBDATA__;
  var out=document.getElementById('wbout');
  if(!out) return;
  var ids=['w_ew','w_ea','w_p1','w_p2','w_rr','w_bg','w_fu','w_fb'];
  var el={};
  ids.forEach(function(i){ el[i]=document.getElementById(i); });
  var P=D.limits.fwd_limit_points.slice().sort(function(a,b){ return a[0]-b[0]; });
  function fwdLimit(w){
    if(w<=P[0][0]) return P[0][1];
    if(w>=P[P.length-1][0]) return P[P.length-1][1];
    for(var i=1;i<P.length;i++){
      if(w<=P[i][0]){
        var a=P[i-1], b=P[i];
        return a[1]+(w-a[0])*(b[1]-a[1])/(b[0]-a[0]);
      }
    }
    return P[P.length-1][1];
  }
  function num(i){ var v=parseFloat(el[i].value); return isNaN(v)?0:v; }
  function calc(){
    var ew=num('w_ew'), ea=num('w_ea');
    var gal=Math.max(0, num('w_fu')-num('w_fb'));
    var rows=[
      ['Empty airplane (assumed)', ew, ea],
      ['Pilot',            num('w_p1'), D.arms.front_seats],
      ['Front passenger',  num('w_p2'), D.arms.front_seats],
      ['Rear seats',       num('w_rr'), D.arms.rear_seats],
      ['Fuel, '+gal.toFixed(1)+' gal', gal*D.fuel.lb_per_gal, D.arms.fuel],
      ['Baggage',          num('w_bg'), D.arms.baggage]
    ];
    var tw=0, tm=0, body='';
    rows.forEach(function(r){
      var m=r[1]*r[2];
      tw+=r[1]; tm+=m;
      body+='<tr><td>'+r[0]+'</td><td>'+r[1].toFixed(1)+'</td><td>'+r[2].toFixed(2)+
            '</td><td>'+m.toFixed(1)+'</td></tr>';
    });
    var cg = tw ? tm/tw : 0;
    var fl = fwdLimit(tw), al = D.limits.aft_limit, gross = D.limits.max_gross;
    var bag = num('w_bg'), bagmax = D.limits.max_baggage;
    var probs=[];
    if(tw>gross) probs.push('over gross by '+(tw-gross).toFixed(1)+' lb');
    if(cg<fl)    probs.push('CG is '+(fl-cg).toFixed(2)+' in forward of the forward limit');
    if(cg>al)    probs.push('CG is '+(cg-al).toFixed(2)+' in aft of the aft limit');
    if(bag>bagmax) probs.push('baggage over the '+bagmax+' lb limit');
    if(gal>D.fuel.gal_usable) probs.push('more fuel than the tanks hold');
    var ok = probs.length===0;
    var marg = Math.min(cg-fl, al-cg);
    out.innerHTML =
      '<table><thead><tr><th>Item</th><th>Weight</th><th>Arm</th><th>Moment</th></tr></thead><tbody>'+
      body+'<tr class="tot"><td>Total</td><td>'+tw.toFixed(1)+'</td><td>'+cg.toFixed(2)+
      '</td><td>'+tm.toFixed(1)+'</td></tr></tbody></table>'+
      '<div class="verd '+(ok?'ok':'no')+'">'+
      (ok ? 'Within limits — '+(gross-tw).toFixed(1)+' lb under gross, '+
            marg.toFixed(2)+' in of CG margin.'
          : 'Not legal — '+probs.join('; ')+'.')+
      '<small>Gross limit '+gross+' lb · forward limit '+fl.toFixed(2)+
      ' in at '+tw.toFixed(0)+' lb · aft limit '+al.toFixed(1)+' in</small></div>';
  }
  ids.forEach(function(i){ el[i].addEventListener('input',calc); });
  calc();
})();

window.addEventListener('beforeprint',function(){ hydrate(document); });
})();
