(function(){
"use strict";
var VENUES = {
  baroeg:{label:"Baroeg",home:"https://baroeg.nl/agenda/",city:"Rotterdam"},
  rotown:{label:"Rotown",home:"https://www.rotown.nl/",city:"Rotterdam"},
  paradiso:{label:"Paradiso",home:"https://www.paradiso.nl/",city:"Amsterdam"},
  melkweg:{label:"Melkweg",home:"https://www.melkweg.nl/nl/agenda/",city:"Amsterdam"},
  tivoli:{label:"TivoliVredenburg",home:"https://www.tivolivredenburg.nl/agenda/",city:"Utrecht"},
  o13:{label:"013",home:"https://www.013.nl/programma",city:"Tilburg"},
  paard:{label:"Paard",home:"https://www.paard.nl/event/",city:"Den Haag"},
  mezz:{label:"Mezz",home:"https://www.mezz.nl/programma/",city:"Breda"},
  effenaar:{label:"Effenaar",home:"https://www.effenaar.nl/agenda",city:"Eindhoven"},
  pul:{label:"De Pul",home:"https://www.livepul.com/agenda/",city:"Uden"},
  boerderij:{label:"De Boerderij",home:"https://poppodiumboerderij.nl/programma/",city:"Zoetermeer"},
  patronaat:{label:"Patronaat",home:"https://patronaat.nl/programma/",city:"Haarlem"},
  hedon:{label:"Hedon",home:"https://www.hedon-zwolle.nl/",city:"Zwolle"},
  helling:{label:"De Helling",home:"https://dehelling.nl/agenda/",city:"Utrecht"},
  dynamo:{label:"Dynamo",home:"https://www.dynamo-eindhoven.nl/evenementen/",city:"Eindhoven"},
  dbs:{label:"dB's",home:"https://dbstudio.nl/agenda/",city:"Utrecht"},
  klokgebouw:{label:"Klokgebouw",home:"https://www.klokgebouw.nl/agenda",city:"Eindhoven"},
  doornroosje:{label:"Doornroosje",home:"https://www.doornroosje.nl/",city:"Nijmegen"},
  metropool:{label:"Metropool",home:"https://metropool.nl/agenda",city:"Hengelo"},
  spot:{label:"SPOT Groningen",home:"https://www.spotgroningen.nl/programma/",city:"Groningen"},
  bibelot:{label:"Bibelot",home:"https://bibelot.net/programma/",city:"Dordrecht"},
  bosuil:{label:"De Bosuil",home:"https://www.debosuil.nl/programma/",city:"Weert"},
  bird:{label:"BIRD",home:"https://bird-rotterdam.nl/concerts/",city:"Rotterdam"},
  amare:{label:"Amare",home:"https://www.amare.nl/nl/agenda",city:"Den Haag"},
  neushoorn:{label:"Neushoorn",home:"https://www.neushoorn.nl/programma",city:"Leeuwarden"},
  gebouwt:{label:"Gebouw-T",home:"https://gebouw-t.nl/agenda/",city:"Bergen op Zoom"},
  tolhuistuin:{label:"Tolhuistuin",home:"https://tolhuistuin.nl/agenda/",city:"Amsterdam"},
  bolwerk:{label:"Het Bolwerk",home:"https://ontdekpoort.nl/programma/locatie/bolwerk-kerkgracht-8/",city:"Sneek"},
  burgerweeshuis:{label:"Burgerweeshuis",home:"https://www.burgerweeshuis.nl/programma",city:"Deventer"},
  ekko:{label:"EKKO",home:"https://ekko.nl/agenda/",city:"Utrecht"},
  nobel:{label:"Gebr. de Nobel",home:"https://nobel.nl/agenda",city:"Leiden"},
  grenswerk:{label:"Grenswerk",home:"https://www.grenswerk.nl/agenda/",city:"Venlo"},
  iduna:{label:"Iduna",home:"https://iduna.nl/agenda/",city:"Drachten"},
  musicon:{label:"Musicon",home:"https://musicon.nl/programma/",city:"Den Haag"},
  qfactory:{label:"Q-Factory",home:"https://q-factory.com/nl",city:"Amsterdam"},
  simplon:{label:"Simplon",home:"https://simplon.nl/programma/",city:"Groningen"},
  sounddog:{label:"Sound Dog",home:"https://sounddogbreda.nl/",city:"Breda"},
  vera:{label:"VERA",home:"https://www.vera-groningen.nl/programma/",city:"Groningen"},
  victorie:{label:"Victorie",home:"https://www.podiumvictorie.nl/programma/",city:"Alkmaar"},
  luxor:{label:"Luxor Live",home:"https://www.luxorlive.nl/agenda/",city:"Arnhem"},
  w2:{label:"Willem Twee",home:"https://www.willem-twee.nl/alle-activiteiten",city:"Den Bosch"},
  gigant:{label:"Gigant",home:"https://www.gigant.nl/concerten/",city:"Apeldoorn"},
  fluor:{label:"Fluor",home:"https://fluor033.nl/programma/",city:"Amersfoort"},
  vorstin:{label:"De Vorstin",home:"https://vorstin.nl/agenda/",city:"Hilversum"},
  p3:{label:"P3",home:"https://www.p3purmerend.nl/programma/",city:"Purmerend"},
  meester:{label:"De Meester",home:"https://poppodiumdemeester.nl/",city:"Almere"},
  occii:{label:"OCCII",home:"https://occii.org/events/",city:"Amsterdam"},
  cinetol:{label:"Cinetol",home:"https://www.cinetol.nl/programma",city:"Amsterdam"},
  engel:{label:"De Groene Engel",home:"https://www.groene-engel.nl/programma/",city:"Oss"},
  bridges:{label:"Backstage Bridges",home:"https://www.backstagebridges.nl/programma/",city:"Tilburg"},
  muziekgieterij:{label:"Muziekgieterij",home:"https://muziekgieterij.nl/",city:"Maastricht"},
  volt:{label:"Volt",home:"https://www.poppodium-volt.nl/programma",city:"Sittard"},
  kade:{label:"De Kade",home:"https://dekadezaandam.nl/agenda/",city:"Zaandam"},
  nor:{label:"Nieuwe Nor",home:"https://nieuwenor.nl/programma",city:"Heerlen"},
  annabel:{label:"Annabel",home:"https://annabel.nu/agenda/",city:"Rotterdam"},
  hof:{label:"Hall of Fame",home:"https://hall-fame.nl/programma",city:"Tilburg"}
};
var REGIONS = [
  ["Noord", ["Groningen", "Leeuwarden", "Sneek", "Drachten", "Assen", "Emmen", "Heerenveen"]],
  ["Oost", ["Zwolle", "Deventer", "Apeldoorn", "Hengelo", "Enschede", "Almelo", "Nijmegen", "Arnhem", "Ede", "Doetinchem"]],
  ["Midden", ["Utrecht", "Amersfoort", "Hilversum"]],
  ["Noord-Holland", ["Amsterdam", "Haarlem", "Zaandam", "Alkmaar", "Purmerend", "Almere", "Hoofddorp", "Hoorn"]],
  ["Zuid-Holland", ["Rotterdam", "Den Haag", "Leiden", "Zoetermeer", "Dordrecht", "Scheveningen", "Delft", "Gouda"]],
  ["Zuid", ["Tilburg", "Breda", "Eindhoven", "Den Bosch", "'s-Hertogenbosch", "Uden", "Oss", "Bergen op Zoom", "Weert", "Venlo", "Heerlen", "Sittard",
            "Maastricht", "Kerkrade", "Roermond", "Landgraaf", "Helmond"]]
];
var REGION_OF = {};
REGIONS.forEach(function (r) { r[1].forEach(function (c) { REGION_OF[c.toLowerCase()] = r[0]; }); });
function regionOf(city) { return REGION_OF[(city || "").toLowerCase()] || "Overig"; }

var DOW = ["zo", "ma", "di", "wo", "do", "vr", "za"], DOWL = ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"];
var MON = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"];
var MONL = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"];
function pad(n) { return (n < 10 ? "0" : "") + n; }
function iso(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
function parse(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
var NOW = new Date(), TODAY = iso(NOW), WEEK_AGO = iso(new Date(NOW.getFullYear(), NOW.getMonth(), NOW.getDate() - 7));
function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
function $(id) { return document.getElementById(id); }
function load(k, d) { try { var r = localStorage.getItem(k); return r ? JSON.parse(r) : d; } catch (e) { return d; } }
function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

/* Titels in HOOFDLETTERS leesbaar maken (alleen weergave) */
var KEEP = /^(DJ|MC|UK|US|USA|NL|BE|DE|FR|GB|II|III|IV|XL|R&B|EP|LP|ABBA|AC\/DC|ADE|TV|NYE|80S|90S|00S|80'S|90'S)$/;
function nice(t) {
  var letters = t.replace(/[^A-Za-zÀ-ÿ]/g, "");
  if (letters.length < 4 || t !== t.toUpperCase()) return t;
  return t.split(/(\s+)/).map(function (w) {
    if (KEEP.test(w.replace(/[^A-Za-z0-9&\/']/g, ""))) return w;
    return w.charAt(0) + w.slice(1).toLowerCase();
  }).join("");
}

var ALL = [], DATA = null, marks = load("ca-marks", {}), mine = load("ca-mine", []);
var state = { tab: "all", q: "", hideSold: load("ca-hidesold", false), useMine: mine.length > 0, weekend: false, sel: [], regions: [], limit: 300, open: null };

function venue(c) { return VENUES[c.v] || { label: c.v, city: "" }; }
function eid(c) { return c.v + "|" + c.d + "|" + c.u; }
function isNew(c) { return c.first && c.first !== "base" && c.first >= WEEK_AGO; }
function club(c) { return c.c && c.v === "rotown"; }
function tsLink(c) { return c.k || c.ka || ("https://www.ticketswap.nl/search?q=" + encodeURIComponent(c.n.split(" + ")[0].replace(/\s*\(.*?\)\s*/g, " ").trim())); }

function weekendRange() {
  var d = new Date(NOW.getFullYear(), NOW.getMonth(), NOW.getDate()), wd = d.getDay();
  var fri = new Date(d); fri.setDate(d.getDate() + ((5 - wd + 7) % 7));
  if (wd === 6) fri.setDate(d.getDate() - 1); if (wd === 0) fri.setDate(d.getDate() - 2);
  var sun = new Date(fri); sun.setDate(fri.getDate() + 2);
  return [iso(fri) < TODAY ? TODAY : iso(fri), iso(sun)];
}

function baseFilter(c, ignoreTab) {
  var v = venue(c);
  if (state.useMine && mine.length) { if (mine.indexOf(c.v) < 0) return false; }
  else if (state.sel.length && state.sel.indexOf(c.v) < 0) return false;
  if (state.regions.length && state.regions.indexOf(regionOf(v.city)) < 0) return false;
  if (state.hideSold && c.s) return false;
  if (state.weekend) { var w = weekendRange(); if (c.d < w[0] || c.d > w[1]) return false; }
  var q = state.q.trim().toLowerCase();
  if (q && (c.n + " " + v.label + " " + v.city + " " + (c.r || "")).toLowerCase().indexOf(q) < 0) return false;
  return true;
}
function tabFilter(c, tab) {
  var m = (marks[c.id] || {}).k;
  if (tab === "new") return isNew(c);
  if (tab === "i") return m === "i";
  if (tab === "t") return m === "t";
  if (tab === "c") return club(c);
  return true;
}
function visible() {
  return ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c) && tabFilter(c, state.tab); });
}

function toggle(id, kind) {
  var c = ALL.filter(function (x) { return x.id === id; })[0];
  if (marks[id] && marks[id].k === kind) delete marks[id];
  else marks[id] = { k: kind, s: c ? { n: c.n, d: c.d, v: c.v, r: c.r, u: c.u } : (marks[id] && marks[id].s) };
  save("ca-marks", marks);
  render(true);
}

function dayLabel(d) {
  var dt = parse(d), diff = Math.round((dt - new Date(NOW.getFullYear(), NOW.getMonth(), NOW.getDate())) / 864e5);
  var base = DOWL[dt.getDay()] + " " + dt.getDate() + " " + MONL[dt.getMonth()] + (dt.getFullYear() !== NOW.getFullYear() ? " " + dt.getFullYear() : "");
  return { base: base.charAt(0).toUpperCase() + base.slice(1), tag: diff === 0 ? "vandaag" : diff === 1 ? "morgen" : "" };
}

function timeCell(t) {
  if (!t) return '<span class="tm">–</span>';
  var m = /^deuren (\d\d:\d\d)$/.exec(t);
  return m ? '<span class="tm d">' + m[1] + '<br>deur</span>' : '<span class="tm">' + esc(t) + "</span>";
}

function row(c) {
  var v = venue(c), m = (marks[c.id] || {}).k || "", open = state.open === c.id;
  var tags = (c.s ? '<span class="tag sold">uitverkocht</span>' : "") + (isNew(c) ? '<span class="tag new">nieuw</span>' : "") +
             (club(c) ? '<span class="tag club">clubcard</span>' : "") + (m === "t" ? '<span class="tag tk">kaartje</span>' : "");
  var where = esc(v.label) + (v.city ? " · " + esc(v.city) : "") + (c.r && c.r !== v.city && c.r.toLowerCase() !== v.label.toLowerCase() ? " · " + esc(c.r) : "");
  return '<div class="ev' + (c.s ? " sold" : "") + (m === "t" ? " t" : "") + (open ? " open" : "") + '" data-id="' + esc(c.id) + '">' +
    '<div class="row" data-act="open">' + timeCell(c.t) +
    '<div class="body"><div class="name">' + esc(nice(c.n)) + '</div><div class="sub">' + where + tags + "</div></div>" +
    '<button class="star" data-act="i" aria-pressed="' + (m === "i") + '" aria-label="Interesse"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3.5l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.8l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z" stroke-linejoin="round"/></svg></button></div>' +
    '<div class="more"><button class="btn" data-act="t" aria-pressed="' + (m === "t") + '">' + (m === "t" ? "Kaartje gekocht" : "Ik heb een kaartje") + "</button>" +
    '<a class="btn link" href="' + esc(c.u) + '" target="_blank" rel="noopener">Zaal ↗</a>' +
    '<a class="btn link" href="' + esc(tsLink(c)) + '" target="_blank" rel="noopener">TicketSwap ↗</a></div></div>';
}

function archive() {
  var out = [];
  Object.keys(marks).forEach(function (id) { var m = marks[id]; if (m.k === "t" && m.s && m.s.d < TODAY) out.push(m.s); });
  return out.sort(function (a, b) { return a.d < b.d ? 1 : -1; });
}

function renderDays(list) {
  var cnt = {}; list.forEach(function (c) { cnt[c.d] = (cnt[c.d] || 0) + 1; });
  var html = "", d = new Date(NOW.getFullYear(), NOW.getMonth(), NOW.getDate());
  for (var i = 0; i < 21; i++) {
    var k = iso(d), wd = d.getDay();
    html += '<button class="dz' + (wd === 5 || wd === 6 || wd === 0 ? " we" : "") + '" data-day="' + k + '">' + DOW[wd] + "<b>" + d.getDate() + "</b><i>" + (cnt[k] || "–") + "</i></button>";
    d.setDate(d.getDate() + 1);
  }
  $("days").innerHTML = html;
}

function render(keepScroll) {
  if (!DATA) return;
  var all = visible();
  $("n-all").textContent = ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c); }).length;
  ["new", "i", "t", "c"].forEach(function (t) { $("n-" + t).textContent = ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c) && tabFilter(c, t); }).length || ""; });
  var arch = archive(); $("n-a").textContent = arch.length || "";
  $("f-mine").setAttribute("aria-pressed", String(state.useMine && mine.length > 0));
  $("f-mine").textContent = mine.length ? "Mijn zalen (" + mine.length + ")" : "Mijn zalen";
  $("f-weekend").setAttribute("aria-pressed", String(state.weekend));
  var nz = state.sel.length + state.regions.length;
  $("f-zalen").setAttribute("aria-pressed", String(nz > 0));
  $("f-zalen").firstChild.textContent = nz ? "Zalen en regio (" + nz + ") " : "Zalen en regio ";
  renderDays(state.tab === "a" ? [] : all);
  var out = $("out");
  if (state.tab === "a") {
    out.innerHTML = arch.length ? '<div class="list">' + arch.map(function (s) {
      var v = VENUES[s.v] || { label: s.v, city: "" };
      return '<div class="ev"><div class="row"><span class="tm">' + esc(s.d.slice(5).split("-").reverse().join("/")) + '</span><div class="body"><div class="name">' + esc(nice(s.n)) +
        '</div><div class="sub">' + esc(v.label) + (v.city ? " · " + esc(v.city) : "") + "</div></div></div></div>";
    }).join("") + "</div>" : '<div class="empty"><b>Nog niets in het archief</b>Concerten waar je een kaartje voor had, komen hier na afloop.</div>';
    return;
  }
  if (!all.length) {
    var msg = state.tab === "i" ? ["Nog geen interesse", "Tik op de ster bij een concert."] : state.tab === "t" ? ["Nog geen kaartjes", "Open een concert en tik op ‘Ik heb een kaartje’."] :
      state.tab === "new" ? ["Niets nieuws", "Hier komen concerten die de afgelopen 7 dagen zijn aangekondigd."] : ["Geen concerten gevonden", "Pas je zoekopdracht of filters aan."];
    out.innerHTML = '<div class="empty"><b>' + msg[0] + "</b>" + msg[1] + "</div>"; return;
  }
  var y = window.scrollY, html = "", cur = "", n = 0, perDay = {};
  all.forEach(function (c) { perDay[c.d] = (perDay[c.d] || 0) + 1; });
  for (var i = 0; i < all.length && n < state.limit; i++, n++) {
    var c = all[i];
    if (c.d !== cur) {
      if (cur) html += "</div>";
      var dl = dayLabel(c.d);
      html += '<div class="dayhead" id="d-' + c.d + '">' + dl.base + (dl.tag ? "<small>" + dl.tag + "</small>" : "") + '<span class="cnt">' + perDay[c.d] + "</span></div><div class=\"list\">";
      cur = c.d;
    }
    html += row(c);
  }
  html += "</div>";
  if (all.length > state.limit) html += '<button class="btn loadmore" id="more">Meer laden (' + (all.length - state.limit) + ")</button>";
  out.innerHTML = html;
  if (keepScroll) window.scrollTo(0, y);
}

function sizeHeader() { document.documentElement.style.setProperty("--hh", $("hdr").offsetHeight + "px"); }

function buildSheet() {
  var byCity = {};
  Object.keys(VENUES).forEach(function (k) {
    if (VENUES[k].linkOnly) return;
    var c = VENUES[k].city || "Overig"; (byCity[c] = byCity[c] || []).push(k);
  });
  var cnt = {}; ALL.forEach(function (c) { if (c.d >= TODAY) cnt[c.v] = (cnt[c.v] || 0) + 1; });
  $("regions").innerHTML = REGIONS.map(function (r) { return r[0]; }).concat(["Overig"]).map(function (r) {
    return '<button class="chip" data-region="' + r + '" aria-pressed="' + (state.regions.indexOf(r) >= 0) + '">' + r + "</button>";
  }).join("");
  var order = REGIONS.map(function (r) { return r[0]; }).concat(["Overig"]);
  var cities = Object.keys(byCity).sort(function (a, b) {
    var ra = order.indexOf(regionOf(a)), rb = order.indexOf(regionOf(b)); return ra - rb || a.localeCompare(b);
  });
  var lastReg = "";
  $("cities").innerHTML = cities.map(function (city) {
    var reg = regionOf(city), head = reg !== lastReg ? '<div style="font:700 15px var(--f-display);margin-top:16px">' + reg + "</div>" : "";
    lastReg = reg;
    var ks = byCity[city].sort(function (a, b) { return VENUES[a].label.localeCompare(VENUES[b].label); });
    return head + '<div class="city"><h3>' + esc(city) + ' <button data-city="' + esc(city) + '">alles</button></h3><div class="vl">' + ks.map(function (k) {
      return '<label><input type="checkbox" value="' + k + '"' + (state.sel.indexOf(k) >= 0 ? " checked" : "") + ">" + esc(VENUES[k].label) + '<span class="c">' + (cnt[k] || 0) + "</span></label>";
    }).join("") + "</div></div>";
  }).join("");
  $("hideSold").checked = !!state.hideSold;
}
function openSheet() {
  if (state.useMine && mine.length && !state.sel.length) state.sel = mine.slice();
  buildSheet(); $("sheet").classList.add("on"); $("sheet").setAttribute("aria-hidden", "false"); document.body.style.overflow = "hidden";
}
function closeSheet() { $("sheet").classList.remove("on"); $("sheet").setAttribute("aria-hidden", "true"); document.body.style.overflow = ""; render(); }

function init(data) {
  DATA = data;
  var tmv = data.venues || {};
  Object.keys(tmv).forEach(function (k) { if (!VENUES[k]) VENUES[k] = { label: tmv[k].label, home: tmv[k].home, city: tmv[k].city || "", tm: true }; });
  ALL = data.events.filter(function (e) { return VENUES[e.v]; }).map(function (e) { e.id = eid(e); return e; });
  var u = new Date(data.updated);
  $("stamp").textContent = "Bijgewerkt " + u.getDate() + " " + MON[u.getMonth()] + " " + pad(u.getHours()) + ":" + pad(u.getMinutes()) + ".";
  var bad = Object.keys(data.status || {}).filter(function (k) { return !data.status[k].ok; });
  if (bad.length) $("warn").innerHTML = '<div class="warn">Niet gelukt vandaag: ' + bad.map(function (k) { return esc((VENUES[k] || {}).label || k); }).join(", ") + ". Daarvan staat de laatst bekende lijst erin.</div>";
  render(); sizeHeader();
}

$("tabs").addEventListener("click", function (e) {
  var b = e.target.closest("[data-tab]"); if (!b) return;
  state.tab = b.getAttribute("data-tab"); state.limit = 300;
  Array.prototype.forEach.call(document.querySelectorAll(".tab"), function (t) { t.setAttribute("aria-selected", String(t === b)); });
  render(); window.scrollTo(0, 0);
});
$("sbtn").addEventListener("click", function () { var q = $("q"); q.classList.toggle("on"); if (q.classList.contains("on")) q.focus(); sizeHeader(); });
$("q").addEventListener("input", function (e) { state.q = e.target.value; state.limit = 300; render(); });
$("f-mine").addEventListener("click", function () {
  if (!mine.length) { openSheet(); return; }
  state.useMine = !state.useMine; if (state.useMine) state.sel = []; render();
});
$("f-weekend").addEventListener("click", function () { state.weekend = !state.weekend; render(); window.scrollTo(0, 0); });
$("f-zalen").addEventListener("click", openSheet);
$("days").addEventListener("click", function (e) {
  var b = e.target.closest("[data-day]"); if (!b) return;
  var d = b.getAttribute("data-day"), all = visible(), idx = all.findIndex(function (c) { return c.d >= d; });
  if (idx < 0) return;
  if (idx + 50 > state.limit) { state.limit = idx + 300; render(); }
  var h = document.getElementById("d-" + all[idx].d);
  if (h) window.scrollTo(0, h.getBoundingClientRect().top + window.scrollY - $("hdr").offsetHeight + 1);
});
$("out").addEventListener("click", function (e) {
  if (e.target.id === "more") { state.limit += 400; render(true); return; }
  var a = e.target.closest("[data-act]"); if (!a) return;
  var ev = a.closest(".ev"), id = ev && ev.getAttribute("data-id"), act = a.getAttribute("data-act");
  if (!id) return;
  if (act === "open") { state.open = state.open === id ? null : id; render(true); return; }
  e.stopPropagation(); toggle(id, act);
});
$("sheet").addEventListener("click", function (e) {
  if (e.target.hasAttribute("data-close")) { closeSheet(); return; }
  var r = e.target.closest("[data-region]");
  if (r) { var k = r.getAttribute("data-region"), i = state.regions.indexOf(k); if (i >= 0) state.regions.splice(i, 1); else state.regions.push(k); r.setAttribute("aria-pressed", String(i < 0)); return; }
  var cb = e.target.closest("[data-city]");
  if (cb) {
    var boxes = cb.closest(".city").querySelectorAll("input"), allOn = Array.prototype.every.call(boxes, function (x) { return x.checked; });
    Array.prototype.forEach.call(boxes, function (x) { x.checked = !allOn; x.dispatchEvent(new Event("change", { bubbles: true })); });
  }
});
$("sheet").addEventListener("change", function (e) {
  if (e.target.id === "hideSold") { state.hideSold = e.target.checked; save("ca-hidesold", state.hideSold); return; }
  if (e.target.type !== "checkbox") return;
  var k = e.target.value, i = state.sel.indexOf(k);
  if (e.target.checked && i < 0) state.sel.push(k); if (!e.target.checked && i >= 0) state.sel.splice(i, 1);
  state.useMine = false;
});
$("clearsel").addEventListener("click", function () { state.sel = []; state.regions = []; state.useMine = false; buildSheet(); });
$("saveMine").addEventListener("click", function () {
  mine = state.sel.slice(); save("ca-mine", mine); state.useMine = mine.length > 0; if (state.useMine) state.sel = []; closeSheet();
});
window.addEventListener("resize", sizeHeader);
fetch("../data/events.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(init).catch(function () {
  $("out").innerHTML = '<div class="empty"><b>Agenda niet geladen</b>Controleer je verbinding en probeer het opnieuw.</div>';
});

})();
