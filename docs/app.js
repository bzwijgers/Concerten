(function(){
"use strict";
var VENUES = {
  baroeg:{label:"Baroeg",home:"https://baroeg.nl/agenda/"},
  rotown:{label:"Rotown",home:"https://www.rotown.nl/"},
  paradiso:{label:"Paradiso",home:"https://www.paradiso.nl/"},
  melkweg:{label:"Melkweg",home:"https://www.melkweg.nl/nl/agenda/"},
  tivoli:{label:"TivoliVredenburg",home:"https://www.tivolivredenburg.nl/agenda/"},
  o13:{label:"013",home:"https://www.013.nl/programma"},
  paard:{label:"Paard",home:"https://www.paard.nl/event/"},
  mezz:{label:"Mezz",home:"https://www.mezz.nl/programma/"},
  effenaar:{label:"Effenaar",home:"https://www.effenaar.nl/agenda"},
  pul:{label:"De Pul",home:"https://www.livepul.com/agenda/"},
  boerderij:{label:"De Boerderij",home:"https://poppodiumboerderij.nl/programma/"},
  patronaat:{label:"Patronaat",home:"https://patronaat.nl/programma/"},
  hedon:{label:"Hedon",home:"https://www.hedon-zwolle.nl/"},
  helling:{label:"De Helling",home:"https://dehelling.nl/agenda/"},
  dynamo:{label:"Dynamo",home:"https://www.dynamo-eindhoven.nl/evenementen/"},
  dbs:{label:"dB's",home:"https://dbstudio.nl/agenda/"},
  klokgebouw:{label:"Klokgebouw",home:"https://www.klokgebouw.nl/agenda"},
  doornroosje:{label:"Doornroosje",home:"https://www.doornroosje.nl/"},
  metropool:{label:"Metropool",home:"https://metropool.nl/agenda"},
  spot:{label:"SPOT Groningen",home:"https://www.spotgroningen.nl/programma/"},
  bibelot:{label:"Bibelot",home:"https://bibelot.net/programma/"},
  bosuil:{label:"De Bosuil",home:"https://www.debosuil.nl/programma/"},
  bird:{label:"BIRD",home:"https://bird-rotterdam.nl/concerts/"},
  amare:{label:"Amare",home:"https://www.amare.nl/nl/agenda"},
  neushoorn:{label:"Neushoorn",home:"https://www.neushoorn.nl/programma"},
  gebouwt:{label:"Gebouw-T",home:"https://gebouw-t.nl/agenda/"},
  tolhuistuin:{label:"Tolhuistuin",home:"https://tolhuistuin.nl/agenda/"},
  bolwerk:{label:"Het Bolwerk",home:"https://ontdekpoort.nl/programma/locatie/bolwerk-kerkgracht-8/"},
  ticketmaster:{label:"Ticketmaster",home:"https://www.ticketmaster.nl/",linkOnly:true},
  ticketswap:{label:"TicketSwap-links",home:"https://www.ticketswap.nl/",linkOnly:true}
};
/* TicketSwap-pagina's van de zaal of stad (gecontroleerd), anders zoekresultaten */
var TSV = {rotown:"https://www.ticketswap.com/location/rotown/2033", melkweg:"https://www.ticketswap.com/location/melkweg/41", o13:"https://www.ticketswap.com/city/tilburg/12"};
var TS = {};   // directe evenementlinks: wordt gevuld uit data/ticketswap.json

var DOW=["zo","ma","di","wo","do","vr","za"], MON=["jan","feb","mrt","apr","mei","jun","jul","aug","sep","okt","nov","dec"];
function pad(n){return (n<10?"0":"")+n;}
function iso(d){return d.getFullYear()+"-"+pad(d.getMonth()+1)+"-"+pad(d.getDate());}
var NOW=new Date(), TODAY=iso(NOW), WEEK_AGO=iso(new Date(NOW.getFullYear(),NOW.getMonth(),NOW.getDate()-7));
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function $(id){return document.getElementById(id);}
function slug(s){return s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/['’*]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");}

var ALL=[], state={tab:"all",q:"",hideSold:false,venues:{}}, marks={}, DATA=null;
function eid(c){return c.v+"|"+c.d+"|"+c.u;}
function loadMarks(){try{var r=localStorage.getItem("ca-marks");if(r)marks=JSON.parse(r)||{};}catch(e){}}
function saveMarks(){try{localStorage.setItem("ca-marks",JSON.stringify(marks));}catch(e){}}
function toggle(id,kind){
  var c=ALL.filter(function(x){return x.id===id;})[0];
  if(marks[id]&&marks[id].k===kind){delete marks[id];}
  else{marks[id]={k:kind,s:c?{n:c.n,d:c.d,v:c.v,r:c.r,u:c.u}:(marks[id]&&marks[id].s)};}
  saveMarks();render();
}
function dayLabel(d){
  var p=d.split("-"),dt=new Date(+p[0],+p[1]-1,+p[2]);
  var base=DOW[dt.getDay()]+" "+(+p[2])+" "+MON[+p[1]-1]+(+p[0]!==NOW.getFullYear()?" "+p[0]:"");
  var diff=Math.round((dt-new Date(NOW.getFullYear(),NOW.getMonth(),NOW.getDate()))/86400000);
  return {base:base,tag:diff===0?"vandaag":diff===1?"morgen":""};
}
function isNew(c){return c.first&&c.first!=="base"&&c.first>=WEEK_AGO;}
function tsLink(c){return c.k||c.ka||TS[c.id]||TSV[c.v]||("https://www.ticketswap.nl/search?q="+encodeURIComponent(c.n.split(" + ")[0].replace(/\s*\(.*?\)\s*/g," ").trim()));}

function visible(){
  var q=state.q.trim().toLowerCase(), on=Object.keys(state.venues).filter(function(k){return state.venues[k];});
  return ALL.filter(function(c){
    if(c.d<TODAY) return false;
    if(on.length&&on.indexOf(c.v)<0) return false;
    if(state.hideSold&&c.s) return false;
    if(q&&(c.n+" "+VENUES[c.v].label+" "+c.r).toLowerCase().indexOf(q)<0) return false;
    return true;
  });
}
function row(c){
  var m=(marks[c.id]||{}).k||"", v=VENUES[c.v];
  var place=c.r?esc(v.label)+" · "+esc(c.r):esc(v.label);
  return '<article class="ev'+(m==="t"?" t":"")+'"><div class="name">'+esc(c.n)+'</div><div class="meta"><span class="venue">'+place+'</span>'
   +(isNew(c)?'<span class="badge new">nieuw</span>':'')+(c.s?'<span class="badge sold">uitverkocht</span>':'')+(c.c?'<span class="badge club">clubcard</span>':'')+(c.t?'<span>'+esc(c.t)+'</span>':'')
   +'</div><div class="acts"><button class="mk" data-act="t" data-id="'+esc(c.id)+'" aria-pressed="'+(m==="t")+'">Kaartje</button>'
   +'<button class="mk" data-act="i" data-id="'+esc(c.id)+'" aria-pressed="'+(m==="i")+'">Interesse</button>'
   +'<a class="lk first" href="'+esc(c.u)+'" target="_blank" rel="noopener">Zaal ↗</a>'
   +(m==="i"?'<a class="lk" href="'+esc(tsLink(c))+'" target="_blank" rel="noopener">TicketSwap ↗</a>':'')+'</div></article>';
}
function archive(){
  var out=[];
  Object.keys(marks).forEach(function(id){var m=marks[id];if(m.k==="t"&&m.s&&m.s.d<TODAY)out.push(m.s);});
  out.sort(function(a,b){return a.d<b.d?1:a.d>b.d?-1:0;});return out;
}
function list(items,rowFn,key){
  var html="",cur="";
  items.forEach(function(c){var d=key(c);if(d!==cur){if(cur)html+='</div>';var dl=dayLabel(d);html+='<div class="dayhead">'+dl.base+(dl.tag?'<small>'+dl.tag+'</small>':'')+'</div><div class="list">';cur=d;}html+=rowFn(c);});
  return html+(cur?'</div>':'');
}
function render(){
  if(!DATA) return;
  var all=visible(), arch=archive();
  var nT=ALL.filter(function(c){return c.d>=TODAY&&marks[c.id]&&marks[c.id].k==="t";}).length;
  var nI=ALL.filter(function(c){return c.d>=TODAY&&marks[c.id]&&marks[c.id].k==="i";}).length;
  $("n-all").textContent=all.length;
  $("n-new").textContent=all.filter(isNew).length;
  $("n-t").textContent=nT;$("n-i").textContent=nI;
  $("n-c").textContent=all.filter(function(c){return c.c;}).length;$("n-a").textContent=arch.length;
  var out=$("out"),shown;
  if(state.tab==="a"){
    if(!arch.length){out.innerHTML='<div class="empty"><b>Nog niets in het archief</b>Concerten waarvoor je een kaartje had komen hier na de concertdatum en blijven hier staan.</div>';return;}
    out.innerHTML=list(arch,function(s){var v=VENUES[s.v]||{label:s.v};return '<article class="ev t"><div class="name">'+esc(s.n)+'</div><div class="meta"><span class="venue">'+esc(v.label)+(s.r?' · '+esc(s.r):'')+'</span></div><div class="acts"><a class="lk first" href="'+esc(s.u)+'" target="_blank" rel="noopener">Zaal ↗</a></div></article>';},function(s){return s.d;});
    return;
  }
  shown=all;
  if(state.tab==="new") shown=all.filter(isNew);
  else if(state.tab==="c") shown=all.filter(function(c){return c.c;});
  else if(state.tab==="t"||state.tab==="i") shown=all.filter(function(c){return marks[c.id]&&marks[c.id].k===state.tab;});
  if(!shown.length){
    var t=state.tab==="t"?["Nog geen kaartjes","Tik bij een concert op Kaartje als je een ticket hebt."]:state.tab==="i"?["Nog geen interesse gemarkeerd","Tik bij een concert op Interesse."]:state.tab==="new"?["Niets nieuws in de laatste 7 dagen","Hier staan concerten die de afgelopen week aan een zaalprogramma zijn toegevoegd."]:state.tab==="c"?["Geen Rotown clubconcerten","Hier staan Rotown-concerten waar Clubcard-houders gratis naar binnen kunnen."]:["Geen concerten gevonden","Pas je zoekopdracht of de zaalfilter aan."];
    out.innerHTML='<div class="empty"><b>'+t[0]+'</b>'+t[1]+'</div>';return;
  }
  out.innerHTML=list(shown,row,function(c){return c.d;});
}
function init(data){
  DATA=data;
  var tmv=data.venues||{};  /* locaties uit Ticketmaster: als zaal toevoegen, achter de eigen zalen */
  Object.keys(tmv).sort(function(a,b){return tmv[a].label.localeCompare(tmv[b].label);}).forEach(function(k){if(!VENUES[k])VENUES[k]={label:tmv[k].label,home:tmv[k].home,tm:true};});
  ALL=data.events.filter(function(e){return VENUES[e.v];}).map(function(e){e.id=eid(e);return e;});
  var keys=Object.keys(VENUES).filter(function(k){return !VENUES[k].linkOnly;});
  $("venues").innerHTML=keys.map(function(k){return (VENUES[k].tm&&!VENUES[keys[keys.indexOf(k)-1]].tm?'<span class="chipsep">Via Ticketmaster:</span>':"")+'<button class="chip" data-v="'+k+'" aria-pressed="false">'+esc(VENUES[k].label)+'</button>';}).join("");
  var u=new Date(data.updated);
  $("stamp").textContent="bijgewerkt "+u.getDate()+" "+MON[u.getMonth()]+" "+pad(u.getHours())+":"+pad(u.getMinutes());
  var bad=Object.keys(data.status||{}).filter(function(k){return !data.status[k].ok;});
  if(bad.length) $("warn").innerHTML='<div class="warn">Niet alle zalen zijn vandaag gelukt: '+bad.map(function(k){return esc(VENUES[k]?VENUES[k].label:k);}).join(", ")+'. Daarvan staat de laatst bekende lijst erin.</div>';
  var tv=(data.status||{}).tivoli;
  if(tv&&tv.manual&&(tv.checked||"")<iso(new Date(NOW.getFullYear(),NOW.getMonth(),NOW.getDate()-3))) $("warn").innerHTML+='<div class="warn">TivoliVredenburg: laatst bijgewerkt op '+esc(tv.checked||"?")+' (via de pc van de eigenaar).</div>';
  render();
}
$("venues").addEventListener("click",function(e){var b=e.target.closest("[data-v]");if(!b)return;var k=b.getAttribute("data-v");state.venues[k]=!state.venues[k];b.setAttribute("aria-pressed",String(!!state.venues[k]));render();});
$("tabs").addEventListener("click",function(e){var b=e.target.closest("[data-tab]");if(!b)return;state.tab=b.getAttribute("data-tab");Array.prototype.forEach.call(document.querySelectorAll(".tab"),function(t){t.setAttribute("aria-selected",String(t===b));});render();});
$("q").addEventListener("input",function(e){state.q=e.target.value;render();});
$("hideSold").addEventListener("change",function(e){state.hideSold=e.target.checked;render();});
$("out").addEventListener("click",function(e){var b=e.target.closest(".mk");if(!b)return;toggle(b.getAttribute("data-id"),b.getAttribute("data-act"));});
loadMarks();
fetch("data/events.json",{cache:"no-cache"}).then(function(r){return r.json();}).then(function(d){init(d);if(window.__splashReady)window.__splashReady();}).catch(function(){if(window.__splashReady)window.__splashReady();$("out").innerHTML='<div class="empty"><b>Agenda niet geladen</b>Controleer je verbinding en probeer het opnieuw.</div>';});
fetch("data/ticketswap.json",{cache:"no-cache"}).then(function(r){return r.ok?r.json():{};}).then(function(j){TS=j||{};render();}).catch(function(){});
try{if("serviceWorker" in navigator)navigator.serviceWorker.register("sw.js");}catch(e){}
})();
