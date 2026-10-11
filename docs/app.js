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
  hof:{label:"Hall of Fame",home:"https://hall-fame.nl/programma",city:"Tilburg"},
  vanpolanen:{label:"Van Polanen Presenteert",home:"https://www.vanpolanenpresenteert.com/",city:"Leiden"},
  walhalla:{label:"Theater Walhalla",home:"https://www.theaterwalhalla.nl/programma/",city:"Rotterdam"},
  ab:{label:"AB",home:"https://www.abconcerts.be/nl/agenda",city:"Brussel",cc:"BE"},
  botanique:{label:"Botanique",home:"https://botanique.be/nl/concerts",city:"Brussel",cc:"BE"},
  trix:{label:"Trix",home:"https://www.trixonline.be/nl/programma",city:"Antwerpen",cc:"BE"},
  roma:{label:"De Roma",home:"https://www.deroma.be/nl/",city:"Borgerhout",cc:"BE"},
  depot:{label:"Het Depot",home:"https://www.hetdepot.be/programma",city:"Leuven",cc:"BE"},
  ha:{label:"Handelsbeurs",home:"https://www.haconcerts.be/nl/concertagenda",city:"Gent",cc:"BE"},
  kreun:{label:"De Kreun",home:"https://www.wildewesten.be/nl/agenda",city:"Kortrijk",cc:"BE"},
  vierad:{label:"4AD",home:"https://www.4ad.be/",city:"Diksmuide",cc:"BE"},
  n9:{label:"N9",home:"https://www.n9.be/agenda/",city:"Eeklo",cc:"BE"},
  casino:{label:"De Casino",home:"https://decasino.be/",city:"Sint-Niklaas",cc:"BE"},
  reflektor:{label:"Reflektor",home:"https://reflektor.be/agenda/",city:"Luik",cc:"BE"},
  bos:{label:"Het Bos",home:"https://www.hetbos.be/programma",city:"Antwerpen",cc:"BE"}
};
var REGIONS = [
  ["Noord", ["Groningen", "Leeuwarden", "Sneek", "Drachten", "Assen", "Emmen", "Heerenveen"]],
  ["Oost", ["Zwolle", "Deventer", "Apeldoorn", "Hengelo", "Enschede", "Almelo", "Nijmegen", "Arnhem", "Ede", "Doetinchem", "Veenendaal"]],
  ["Midden", ["Utrecht", "Amersfoort", "Hilversum"]],
  ["Noord-Holland", ["Amsterdam", "Haarlem", "Zaandam", "Alkmaar", "Purmerend", "Almere", "Hoofddorp", "Hoorn", "Amstelveen"]],
  ["Zuid-Holland", ["Rotterdam", "Den Haag", "Leiden", "Zoetermeer", "Dordrecht", "Scheveningen", "Delft", "Gouda"]],
  ["Zuid", ["Tilburg", "Breda", "Eindhoven", "Den Bosch", "'s-Hertogenbosch", "Uden", "Oss", "Bergen op Zoom", "Weert", "Venlo", "Heerlen", "Sittard",
            "Maastricht", "Kerkrade", "Roermond", "Landgraaf", "Helmond"]]
];
REGIONS.push(["België", ["Brussel", "Bruxelles", "Antwerpen", "Borgerhout", "Leuven", "Gent", "Brugge", "Kortrijk", "Diksmuide", "Eeklo", "Sint-Niklaas",
  "Luik", "Liège", "Hasselt", "Mechelen", "Oostende", "Vorst", "Forest", "Werchter", "Genk", "Aalst", "Namen", "Namur", "Charleroi", "Bergen", "Mons", "Turnhout"]]);
var REGION_OF = {};
REGIONS.forEach(function (r) { r[1].forEach(function (c) { REGION_OF[c.toLowerCase()] = r[0]; }); });
function regionOf(city) { return REGION_OF[(city || "").toLowerCase()] || "Overig"; }
var RCOL = { "België": "#E2B33C", "Noord": "#1D9E75", "Oost": "#BA7517", "Midden": "#7F77DD", "Noord-Holland": "#378ADD", "Zuid-Holland": "#D4537E", "Zuid": "#D85A30", "Overig": "#888780" };
function rcol(city) { return RCOL[regionOf(city)]; }
var HOME = [51.958, 4.476];   /* Rotterdam-Schiebroek (3056), afgerond */
function travel(city) {
  var c = COORD[city]; if (!c) return null;
  var R = 6371, dLa = (c[0] - HOME[0]) * Math.PI / 180, dLo = (c[1] - HOME[1]) * Math.PI / 180;
  var a = Math.sin(dLa / 2) * Math.sin(dLa / 2) + Math.cos(HOME[0] * Math.PI / 180) * Math.cos(c[0] * Math.PI / 180) * Math.sin(dLo / 2) * Math.sin(dLo / 2);
  var km = 2 * R * Math.asin(Math.sqrt(a)) * 1.2;   /* hemelsbreed x 1,2 = over de weg */
  return Math.round(km / 100 * 60 + 8);              /* ~100 km/u gemiddeld + 8 min op- en afrit */
}
function fmtTravel(m) { return m < 60 ? m + " min" : Math.floor(m / 60) + " u " + (m % 60 ? (m % 60) + " min" : ""); }
/* vlaggetje in plaats van de landnaam (land uit de zaal, standaard Nederland) */
/* getekende vlaggetjes (emoji-vlaggen werken niet op elke telefoon) */
var FLAG = {
  NL: '<svg class="flag" viewBox="0 0 9 6" aria-label="Nederland"><rect width="9" height="2" fill="#AE1C28"/><rect y="2" width="9" height="2" fill="#fff"/><rect y="4" width="9" height="2" fill="#21468B"/></svg>',
  BE: '<svg class="flag" viewBox="0 0 9 6" aria-label="België"><rect width="3" height="6" fill="#000"/><rect x="3" width="3" height="6" fill="#FDDA24"/><rect x="6" width="3" height="6" fill="#EF3340"/></svg>' };
function place(v) { return v.city ? " · " + esc(v.city) + (state.tab === "c" ? "" : " " + (FLAG[v.cc || "NL"] || "")) : ""; }   /* Rotown club: geen vlag */
/* ligging van de steden (breedte, lengte) voor de kaart */
var COORD = { "Amsterdam": [52.37, 4.90], "Utrecht": [52.09, 5.12], "Groningen": [53.22, 6.57], "Den Haag": [52.08, 4.30], "Rotterdam": [51.92, 4.48],
  "Eindhoven": [51.44, 5.47], "Tilburg": [51.56, 5.09], "Nijmegen": [51.84, 5.86], "Haarlem": [52.38, 4.64], "Breda": [51.59, 4.78], "Arnhem": [51.98, 5.91],
  "Hengelo": [52.27, 6.79], "Enschede": [52.22, 6.89], "Zwolle": [52.52, 6.09], "Leiden": [52.16, 4.49], "Maastricht": [50.85, 5.69], "Alkmaar": [52.63, 4.75],
  "Oss": [51.77, 5.52], "Heerlen": [50.89, 5.98], "Leeuwarden": [53.20, 5.80], "Zoetermeer": [52.06, 4.49], "Dordrecht": [51.81, 4.67], "Bergen op Zoom": [51.49, 4.29],
  "Uden": [51.66, 5.62], "Weert": [51.25, 5.71], "Sneek": [53.03, 5.66], "Purmerend": [52.50, 4.95], "Venlo": [51.37, 6.17], "Amersfoort": [52.16, 5.39],
  "Hilversum": [52.22, 5.18], "Deventer": [52.25, 6.16], "Apeldoorn": [52.21, 5.97], "Drachten": [53.11, 6.10], "Almere": [52.37, 5.21], "Den Bosch": [51.69, 5.30],
  "Sittard": [51.00, 5.87], "Zaandam": [52.44, 4.83], "Amstelveen": [52.30, 4.86], "Ede": [52.04, 5.67], "Hoofddorp": [52.30, 4.69], "Kerkrade": [50.87, 6.06],
  "Roermond": [51.19, 5.99], "Brussel": [50.85, 4.35], "Bruxelles": [50.85, 4.35], "Antwerpen": [51.22, 4.40], "Borgerhout": [51.21, 4.44],
  "Leuven": [50.88, 4.70], "Gent": [51.05, 3.72], "Brugge": [51.21, 3.22], "Kortrijk": [50.83, 3.26], "Diksmuide": [51.03, 2.86], "Eeklo": [51.19, 3.56],
  "Sint-Niklaas": [51.17, 4.14], "Luik": [50.63, 5.57], "Liège": [50.63, 5.57], "Hasselt": [50.93, 5.34], "Mechelen": [51.03, 4.48], "Oostende": [51.23, 2.92],
  "Vorst": [50.81, 4.32], "Forest": [50.81, 4.32], "Werchter": [50.97, 4.70], "Genk": [50.97, 5.50], "Aalst": [50.94, 4.04], "Namen": [50.47, 4.87], "Veenendaal": [52.03, 5.56], "Landgraaf": [50.90, 6.02], "Helmond": [51.48, 5.66], "Scheveningen": [52.11, 4.27], "Delft": [52.01, 4.36] };

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
Object.keys(marks).forEach(function (id) { var m = marks[id]; if (m && m.k) { m[m.k] = true; delete m.k; } });   /* oud formaat */
function has(id, f) { return !!(marks[id] && marks[id][f]); }
var state = { asort: load("ca-asort", "d"), near: false, city: "", tab: "all", q: "", hideSold: load("ca-hidesold", false), useMine: mine.length > 0, from: "", to: "", sel: [], regions: [], limit: 300, open: null, showDate: false };

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

function baseFilter(c, noDates, noCity) {
  var v = venue(c);
  if (!noCity && state.city && v.city !== state.city) return false;
  if (state.near) { var tt = travel(v.city); if (tt === null || tt > 90) return false; }
  if (state.useMine && mine.length) { if (mine.indexOf(c.v) < 0) return false; }
  else if (state.sel.length && state.sel.indexOf(c.v) < 0) return false;
  if (state.regions.length && state.regions.indexOf(regionOf(v.city)) < 0) return false;
  if (state.hideSold && c.s) return false;
  if (!noDates && state.from && c.d < state.from) return false;
  if (!noDates && state.to && c.d > state.to) return false;
  var q = state.q.trim().toLowerCase();
  if (q && (c.n + " " + v.label + " " + v.city + " " + (c.r || "")).toLowerCase().indexOf(q) < 0) return false;
  return true;
}
function tabFilter(c, tab) {
  if (tab === "new") return isNew(c);
  if (tab === "i") return has(c.id, "i");
  if (tab === "t") return has(c.id, "t");
  if (tab === "c") return club(c);
  return true;
}
function visible() {
  var out = ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c) && tabFilter(c, state.tab); });
  if (state.tab === "i" || state.tab === "t") {
    var known = {}; ALL.forEach(function (c) { known[c.id] = 1; });
    Object.keys(marks).forEach(function (id) {
      var m = marks[id];
      if (known[id] || !m[state.tab] || !m.s || m.s.d < TODAY) return;
      out.push({ id: id, v: m.s.v, d: m.s.d, n: m.s.n, u: m.s.u, t: "", r: m.s.r || "", s: false, orphan: true, ts: "99" });
    });
    out.sort(function (a, b) { return a.d < b.d ? -1 : a.d > b.d ? 1 : a.ts < b.ts ? -1 : a.ts > b.ts ? 1 : 0; });
  }
  return out;
}

function toggle(id, kind) {
  var c = ALL.filter(function (x) { return x.id === id; })[0];
  var m = marks[id] || {}; m[kind] = !m[kind];
  if (!c && m.s) c = null;   /* concert niet meer in de agenda: markering en momentopname blijven bewaard */   // kaartje en interesse zijn los van elkaar
  if (c) m.s = { n: c.n, d: c.d, v: c.v, r: c.r, u: c.u };
  if (!m.i && !m.t) delete marks[id]; else marks[id] = m;
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
  var v = venue(c), tk = has(c.id, "t"), it = has(c.id, "i"), open = state.open === c.id;
  var tags = (c.s ? '<span class="tag sold">uitverkocht</span>' : "") + (isNew(c) ? '<span class="tag new">nieuw</span>' : "") +
             (club(c) ? '<span class="tag club">clubcard</span>' : "") + (tk ? '<span class="tag tk">kaartje</span>' : "");
  var where = esc(v.label) + place(v) + (c.r && c.r.toLowerCase().indexOf(v.label.toLowerCase()) < 0 && c.r.toLowerCase().indexOf((v.city || "~").toLowerCase()) < 0 && v.label.toLowerCase().indexOf(c.r.toLowerCase()) < 0 ? " · " + esc(c.r) : "");
  var col = rcol(v.city), pic = c.th ? '<img class="th" src="' + esc(c.th) + '" alt="" loading="lazy" width="44" height="44">' :
    '<span class="th thx" style="background:' + col + '26;color:' + col + '">' + esc((nice(c.n).replace(/^[^A-Za-z0-9\u00C0-\u00FF]+/, "").charAt(0) || "*").toUpperCase()) + "</span>";
  return '<div class="ev' + (c.s ? " sold" : "") + (tk ? " t" : "") + (open ? " open" : "") + '" data-id="' + esc(c.id) + '" style="--rc:' + col + '">' +
    '<div class="row" data-act="open">' + pic + timeCell(c.t) +
    '<div class="body"><div class="name">' + esc(nice(c.n)) + '</div><div class="sub">' + where + tags + "</div></div>" +
    '<button class="star" data-act="i" aria-pressed="' + it + '" aria-label="Interesse"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3.5l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.8l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z" stroke-linejoin="round"/></svg></button></div>' +
    '<div class="more">' + (travel(v.city) !== null ? '<span class="trv">± ' + fmtTravel(travel(v.city)) + " rijden</span>" : "") + '<button class="btn" data-act="t" aria-pressed="' + tk + '">' + (tk ? "Kaartje gekocht" : "Ik heb een kaartje") + "</button>" +
    '<a class="btn link" href="' + esc(c.u) + '" target="_blank" rel="noopener">Zaal ↗</a>' +
    '<a class="btn link" href="' + esc(tsLink(c)) + '" target="_blank" rel="noopener">TicketSwap ↗</a></div></div>';
}

/* archief: bezochte concerten met een cijfer van 0 tot 10, een korte review, en verwijderen na bevestiging */
var STAR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3.5l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.8l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z" stroke-linejoin="round"/></svg>';
function archRow(a) {
  var s = a.s, v = VENUES[s.v] || { label: s.v, city: "" }, r = a.rv.r, open = state.aopen === a.id, conf = state.aconfirm === a.id;
  var score = typeof r === "number" ? '<span class="score">' + String(r).replace(".", ",") + "/10</span>" : '<span class="score none">nog geen cijfer</span>';
  var stars = "";
  for (var i = 1; i <= 10; i++) {
    var st = typeof r === "number" ? (r >= i ? " on" : r >= i - 0.5 ? " half" : "") : "";
    stars += '<button class="rs' + st + '" data-rate="' + i + '" aria-label="' + i + ' van 10 (links: ' + (i - 0.5) + ')">' + STAR + "</button>";
  }
  return '<div class="ev arch' + (open ? " open" : "") + '" data-aid="' + esc(a.id) + '">' +
    '<div class="row" data-aact="open"><span class="tm d">' + esc(+s.d.slice(8) + " " + MON[+s.d.slice(5, 7) - 1]) + "<br>" + s.d.slice(0, 4) + "</span>" +
    '<div class="body"><div class="name">' + esc(nice(s.n)) + '</div><div class="sub">' + esc(v.label) + place(v) + "</div>" +
    (a.rv.txt && !open ? '<div class="rvtxt">“' + esc(a.rv.txt) + "”</div>" : "") + "</div>" + score + "</div>" +
    '<div class="more amore"><div class="rate">' + stars + '<button class="rz' + (r === 0 ? " on" : "") + '" data-rate="0">0</button></div>' +
    '<textarea class="rvin" data-rv="1" rows="3" maxlength="600" placeholder="Hoe was het? (optioneel)">' + esc(a.rv.txt || "") + "</textarea>" +
    (conf ? '<div class="confirm">Dit concert uit je archief verwijderen? Je cijfer en review gaan ook weg.' +
            '<div><button class="btn danger" data-aact="del">Ja, verwijderen</button><button class="btn" data-aact="nodel">Annuleren</button></div></div>'
          : '<button class="btn link small" data-aact="ask">Verwijderen uit archief</button>') + "</div></div>";
}
function setReview(id, f, val) {
  var m = marks[id]; if (!m) return;
  m.rv = m.rv || {}; if (val === null || val === "") delete m.rv[f]; else m.rv[f] = val;
  save("ca-marks", marks);
}

function archive() {
  var out = [];
  Object.keys(marks).forEach(function (id) { var m = marks[id]; if (m.t && m.s && m.s.d < TODAY) out.push({ id: id, s: m.s, rv: m.rv || {} }); });
  return out.sort(function (a, b) { return a.s.d < b.s.d ? 1 : -1; });
}

function renderDays(list) {
  var cnt = {}, last = TODAY; list.forEach(function (c) { cnt[c.d] = (cnt[c.d] || 0) + 1; if (c.d > last) last = c.d; });
  var html = "", d = new Date(NOW.getFullYear(), NOW.getMonth(), NOW.getDate()), one = state.from && state.from === state.to ? state.from : "";
  for (var i = 0; i < 450; i++) {
    var k = iso(d), wd = d.getDay();
    if (k > last) break;
    if (i === 0 || d.getDate() === 1) html += '<span class="dm">' + MON[d.getMonth()] + (d.getFullYear() !== NOW.getFullYear() ? " " + String(d.getFullYear()).slice(2) : "") + "</span>";
    html += '<button class="dz' + (wd === 5 || wd === 6 || wd === 0 ? " we" : "") + (k === one ? " cur" : "") + (!one && state.from && k >= state.from && k <= (state.to || "9999") ? " inr" : "") + '" data-day="' + k + '">' + DOW[wd] + "<b>" + d.getDate() + "</b><i>" + (cnt[k] || "–") + "</i></button>";
    d.setDate(d.getDate() + 1);
  }
  $("days").innerHTML = html;
  var cur = $("days").querySelector(".cur"); if (cur) cur.scrollIntoView({ inline: "center", block: "nearest" });
}
function fmt(k) { var d = parse(k); return DOW[d.getDay()] + " " + d.getDate() + " " + MON[d.getMonth()]; }
function setRange(a, b) { state.from = a || ""; state.to = b || a || ""; state.limit = 300; $("dfrom").value = state.from; $("dto").value = state.to; render(); window.scrollTo(0, 0); }

function render(keepScroll) {
  if (!DATA) return;
  var all = visible();
  $("n-all").textContent = ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c); }).length;
  ["new", "i", "t", "c"].forEach(function (t) { $("n-" + t).textContent = ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c) && tabFilter(c, t); }).length || ""; });
  var arch = archive(); $("n-a").textContent = arch.length || "";
  $("f-mine").setAttribute("aria-pressed", String(state.useMine && mine.length > 0));
  $("f-mine").textContent = mine.length ? "Mijn zalen (" + mine.length + ")" : "Mijn zalen";
  var w = weekendRange();
  $("f-weekend").setAttribute("aria-pressed", String(state.from === w[0] && state.to === w[1]));
  $("f-date").setAttribute("aria-pressed", String(!!state.from));
  $("f-date").firstChild.textContent = state.from ? (state.from === state.to ? fmt(state.from) : fmt(state.from) + " – " + (state.to ? fmt(state.to) : "…")) + " " : "Datum ";
  var nz = state.sel.length + state.regions.length;
  $("f-zalen").setAttribute("aria-pressed", String(nz > 0));
  $("f-zalen").firstChild.textContent = nz ? "Zalen en regio (" + nz + ") " : "Zalen en regio ";
  $("f-ov").setAttribute("aria-pressed", String(!!state.city));
  $("f-near").setAttribute("aria-pressed", String(state.near));
  $("f-ov").lastChild.textContent = state.city ? " " + state.city + " \u2715" : " Overzicht";
  document.body.classList.toggle("arch", state.tab === "a");
  renderDays(state.tab === "a" ? [] : ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c, true) && tabFilter(c, state.tab); }));
  var out = $("out");
  if (state.tab === "a") {
    var rated = arch.filter(function (a) { return typeof a.rv.r === "number"; });
    var head = arch.length ? '<div class="resinfo"><b>' + arch.length + "</b> bezochte concerten" + (rated.length ? " · gemiddeld <b>" +
      (rated.reduce(function (t, a) { return t + a.rv.r; }, 0) / rated.length).toFixed(1).replace(".", ",") + "</b>/10 over " + rated.length : "") + "</div>" : "";
    /* archief sorteren op datum, naam of cijfer; het zoekveld werkt hier ook */
    var srt = state.asort, qa = state.q.trim().toLowerCase(), shown = arch.filter(function (a) {
      return !qa || (a.s.n + " " + venue(a.s).label + " " + (venue(a.s).city || "")).toLowerCase().indexOf(qa) >= 0; });
    if (srt === "n") shown.sort(function (a, b) { return nice(a.s.n).localeCompare(nice(b.s.n), "nl"); });
    if (srt === "r") shown.sort(function (a, b) { var x = typeof a.rv.r === "number" ? a.rv.r : -1, y = typeof b.rv.r === "number" ? b.rv.r : -1; return y - x || (a.s.d < b.s.d ? 1 : -1); });
    var seg = arch.length > 1 ? '<div class="aseg">Sorteer: ' + [["d", "Datum"], ["n", "Naam"], ["r", "Cijfer"]].map(function (o) {
      return '<button class="chip" data-asort="' + o[0] + '" aria-pressed="' + (srt === o[0]) + '">' + o[1] + "</button>"; }).join("") + "</div>" : "";
    out.innerHTML = arch.length ? head + seg + (shown.length ? '<div class="list">' + shown.map(archRow).join("") + "</div>" :
      '<div class="empty"><b>Niets gevonden</b>Geen bezocht concert met ‘' + esc(state.q.trim()) + '’.</div>') :
      '<div class="empty"><b>Nog niets in het archief</b>Concerten waar je een kaartje voor had, komen hier na afloop.</div>';
    return;
  }
  if (!all.length) {
    var msg = state.tab === "i" ? ["Nog geen interesse", "Tik op de ster bij een concert."] : state.tab === "t" ? ["Nog geen kaartjes", "Open een concert en tik op ‘Ik heb een kaartje’."] :
      state.tab === "new" ? ["Niets nieuws", "Hier komen concerten die de afgelopen 7 dagen zijn aangekondigd."] : ["Geen concerten gevonden", "Pas je zoekopdracht of filters aan."];
    out.innerHTML = '<div class="empty"><b>' + msg[0] + "</b>" + msg[1] + "</div>"; return;
  }
  var y = window.scrollY, html = "", cur = "", n = 0, perDay = {};
  if (state.q.trim() || state.from || state.city || state.near) html += '<div class="resinfo"><b>' + all.length + "</b> concert" + (all.length === 1 ? "" : "en") +
    (state.q.trim() ? " voor ‘" + esc(state.q.trim()) + "’" : "") + (state.city ? " in " + esc(state.city) : "") + (state.near ? " binnen 1,5 uur rijden" : "") + (state.from ? (state.from === state.to ? " op " + fmt(state.from) : " van " + fmt(state.from) + (state.to ? " t/m " + fmt(state.to) : "")) : "") +
    ' <button class="lnk" id="clearall">wissen</button></div>';
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
var ovOpenedAt = 0;
function openOverview() {
  var list = ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c, false, true) && tabFilter(c, state.tab); });
  var per = {}; list.forEach(function (c) { var ct = venue(c).city; if (COORD[ct]) per[ct] = (per[ct] || 0) + 1; });
  var X = function (l) { return 10 + (l - 2.45) / (7.3 - 2.45) * 300; }, Y = function (b) { return 10 + (53.6 - b) / (53.6 - 49.45) * 420; };
  var max = Math.max.apply(null, Object.keys(per).map(function (k) { return per[k]; }).concat([1]));
  var cities = Object.keys(per).sort(function (a, b) { return per[b] - per[a]; });
  var NL = [[52.96,4.73],[53.18,5.40],[53.40,5.95],[53.45,6.60],[53.33,7.20],[53.18,7.21],[52.65,7.05],[52.42,7.07],[52.22,7.06],[52.04,6.69],[51.85,6.15],
    [51.83,5.95],[51.65,6.10],[51.37,6.20],[51.17,6.08],[51.02,5.90],[50.76,6.02],[50.75,5.69],[51.05,5.62],[51.15,5.55],[51.27,5.23],[51.43,5.00],[51.45,4.55],
    [51.37,4.23],[51.30,3.95],[51.37,3.37],[51.60,3.70],[51.85,4.05],[52.10,4.25],[52.45,4.57],[52.96,4.73]];
  var BE = [[51.37,3.37],[51.30,3.95],[51.37,4.23],[51.45,4.55],[51.43,5.00],[51.27,5.23],[51.15,5.55],[51.05,5.62],[50.75,5.69],[50.76,6.02],[50.32,6.40],
    [50.13,6.13],[49.55,5.85],[49.50,5.47],[49.80,4.85],[50.15,4.20],[50.35,4.05],[50.73,3.25],[50.80,2.85],[51.00,2.55],[51.37,3.37]];
  var poly = function (P) { return "M" + P.map(function (p) { return X(p[1]).toFixed(1) + " " + Y(p[0]).toFixed(1); }).join(" L") + "Z"; };
  var svg = '<svg viewBox="0 0 320 440" class="map" role="img" aria-label="Concerten per stad"><path class="nl" d="' + poly(NL) + '"/><path class="nl be" d="' + poly(BE) + '"/>';
  cities.slice().reverse().forEach(function (ct) {
    var r = Math.max(4, Math.sqrt(per[ct] / max) * 24), on = state.city === ct, col = rcol(ct);
    svg += '<circle data-city="' + esc(ct) + '" cx="' + X(COORD[ct][1]).toFixed(1) + '" cy="' + Y(COORD[ct][0]).toFixed(1) + '" r="' + r.toFixed(1) + '" fill="' + col +
      '" fill-opacity="' + (on ? ".85" : ".32") + '" stroke="' + col + '" stroke-width="' + (on ? 3 : 1) + '"><title>' + esc(ct) + ": " + per[ct] + "</title></circle>";
  });
  var boxes = [];   /* namen alleen tonen als ze niet over een andere naam vallen */
  cities.forEach(function (ct) {
    var r = Math.max(4, Math.sqrt(per[ct] / max) * 24), cx = X(COORD[ct][1]), cy = Y(COORD[ct][0]), txt = ct + " " + per[ct];
    var w = txt.length * 5.6, left = cx > 200, x0 = left ? cx - r - 3 - w : cx + r + 3, b = [x0, cy - 7, x0 + w, cy + 5];
    if (b[0] < 2 || b[2] > 318 || boxes.some(function (o) { return !(b[2] < o[0] || b[0] > o[2] || b[3] < o[1] || b[1] > o[3]); })) return;
    boxes.push(b);
    svg += '<text x="' + (left ? cx - r - 3 : cx + r + 3).toFixed(1) + '" y="' + (cy + 4).toFixed(1) + '" class="ml"' + (left ? ' text-anchor="end"' : "") + ">" + esc(txt) + "</text>";
  });
  svg += '<text class="cl" x="' + X(3.3).toFixed(1) + '" y="' + Y(53.25).toFixed(1) + '">Nederland</text><text class="cl" x="' + X(4.6).toFixed(1) + '" y="' + Y(49.85).toFixed(1) + '">België</text>';
  $("map").innerHTML = svg + "</svg>";
  var mon = {};
  ALL.filter(function (c) { return c.d >= TODAY && baseFilter(c, true) && tabFilter(c, state.tab); }).forEach(function (c) { var k = c.d.slice(0, 7); mon[k] = (mon[k] || 0) + 1; });
  var ks = Object.keys(mon).sort().slice(0, 12), mm = Math.max.apply(null, ks.map(function (k) { return mon[k]; }).concat([1]));
  $("months").innerHTML = ks.map(function (k) {
    var y = +k.slice(0, 4), m = +k.slice(5) - 1, on = !!(state.from && state.to && state.from.slice(0, 7) === k && state.to.slice(0, 7) === k && state.from !== state.to);
    return '<button class="mb' + (on ? " on" : "") + '" data-month="' + k + '"><span>' + MON[m] + (y !== NOW.getFullYear() ? " " + String(y).slice(2) : "") +
      '</span><i><b style="width:' + Math.round(mon[k] / mm * 100) + '%"></b></i><em>' + mon[k] + "</em></button>";
  }).join("");
  $("ovclear").style.display = state.city ? "" : "none";
  ovOpenedAt = Date.now();   /* tikken op de kaart pas na een halve seconde: een doorgevallen tik kiest geen stad */
  $("ovsheet").classList.add("on"); $("ovsheet").setAttribute("aria-hidden", "false"); document.body.style.overflow = "hidden";
}
function closeOverview() { $("ovsheet").classList.remove("on"); $("ovsheet").setAttribute("aria-hidden", "true"); document.body.style.overflow = ""; }

function openSheet() {
  if (state.useMine && mine.length && !state.sel.length) state.sel = mine.slice();
  buildSheet(); $("sheet").classList.add("on"); $("sheet").setAttribute("aria-hidden", "false"); document.body.style.overflow = "hidden";
}
function closeSheet() { $("sheet").classList.remove("on"); $("sheet").setAttribute("aria-hidden", "true"); document.body.style.overflow = ""; render(); }

function init(data) {
  DATA = data;
  var tmv = data.venues || {};
  Object.keys(tmv).forEach(function (k) { if (!VENUES[k]) VENUES[k] = { label: tmv[k].label, home: tmv[k].home, city: (tmv[k].city || "").replace(/ OV$/, ""), cc: tmv[k].cc || "NL", tm: true }; });
  ALL = data.events.filter(function (e) { return VENUES[e.v]; }).map(function (e) { e.id = eid(e); e.ts = (e.t || "").replace("deuren ", "") || "99"; if (e.ts < "06") e.ts = "3" + e.ts; return e; });
  ALL.sort(function (a, b) { return a.d < b.d ? -1 : a.d > b.d ? 1 : a.ts < b.ts ? -1 : a.ts > b.ts ? 1 : 0; });
  var u = new Date(data.updated);
  $("stamp").textContent = "bijgewerkt " + u.getDate() + " " + MON[u.getMonth()] + " " + pad(u.getHours()) + ":" + pad(u.getMinutes());
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
$("f-weekend").addEventListener("click", function () { var w = weekendRange(); if (state.from === w[0] && state.to === w[1]) setRange("", ""); else setRange(w[0], w[1]); });
$("f-date").addEventListener("click", function () { state.showDate = !state.showDate; $("daterow").classList.toggle("on", state.showDate); sizeHeader(); });
$("daterow").addEventListener("change", function () { var a = $("dfrom").value, b = $("dto").value; if (b && a && b < a) b = a; setRange(a, b); });
$("daterow").addEventListener("click", function (e) {
  var p = e.target.closest("[data-preset]"); if (!p) return;
  state.showDate = false; $("daterow").classList.remove("on");
  var t = new Date(NOW.getFullYear(), NOW.getMonth(), NOW.getDate()), k = p.getAttribute("data-preset"), e2 = new Date(t);
  if (k === "today") setRange(TODAY, TODAY);
  else if (k === "tomorrow") { e2.setDate(t.getDate() + 1); setRange(iso(e2), iso(e2)); }
  else if (k === "week") { e2.setDate(t.getDate() + 6); setRange(TODAY, iso(e2)); }
  else if (k === "month") { setRange(TODAY, iso(new Date(t.getFullYear(), t.getMonth() + 1, 0))); }
  else if (k === "next") { setRange(iso(new Date(t.getFullYear(), t.getMonth() + 1, 1)), iso(new Date(t.getFullYear(), t.getMonth() + 2, 0))); }
  else setRange("", "");
});
$("f-zalen").addEventListener("click", openSheet);
$("f-ov").addEventListener("click", function () {
  if (state.city) { state.city = ""; state.limit = 300; render(); return; }   /* stad aan: de knop zet het filter uit */
  openOverview();
});
$("f-near").addEventListener("click", function () { state.near = !state.near; state.limit = 300; render(); window.scrollTo(0, 0); });
$("ovsheet").addEventListener("click", function (e) {
  if (e.target.hasAttribute("data-close")) { closeOverview(); return; }
  var c = e.target.closest("[data-city]");
  if (e.target.id === "ovclear") { state.city = ""; closeOverview(); render(); return; }
  if (c && Date.now() - ovOpenedAt < 500) return;
  if (c) { var ct = c.getAttribute("data-city"); state.city = state.city === ct ? "" : ct; state.limit = 300; closeOverview(); render(); window.scrollTo(0, 0); return; }
  var m = e.target.closest("[data-month]");
  if (m) {
    var k = m.getAttribute("data-month"), y = +k.slice(0, 4), mo = +k.slice(5);
    var a = k + "-01" < TODAY ? TODAY : k + "-01"; closeOverview(); setRange(a, iso(new Date(y, mo, 0)));
  }
});
$("days").addEventListener("click", function (e) {
  var b = e.target.closest("[data-day]"); if (!b) return;
  var d = b.getAttribute("data-day");
  if (state.from === d && state.to === d) setRange("", ""); else setRange(d, d);   // tik = alleen die dag, nog eens = alles
});
$("out").addEventListener("click", function (e) {
  if (e.target.id === "more") { state.limit += 400; render(true); return; }
  var arow = e.target.closest("[data-aid]");
  if (arow) {
    var aid = arow.getAttribute("data-aid"), rb = e.target.closest("[data-rate]"), ab = e.target.closest("[data-aact]");
    if (rb) {
      var n = +rb.getAttribute("data-rate"), box = rb.getBoundingClientRect(), cur = (marks[aid].rv || {}).r;
      if (n > 0 && e.clientX < box.left + box.width / 2) n -= 0.5;   /* linkerhelft van de ster = halve punt */
      setReview(aid, "r", cur === n ? null : n); render(true); return;
    }
    if (!ab || e.target.closest("textarea")) return;
    var act0 = ab.getAttribute("data-aact");
    if (act0 === "open") { state.aopen = state.aopen === aid ? null : aid; state.aconfirm = null; }
    else if (act0 === "ask") state.aconfirm = aid;
    else if (act0 === "nodel") state.aconfirm = null;
    else if (act0 === "del") { delete marks[aid]; save("ca-marks", marks); state.aconfirm = null; state.aopen = null; }
    render(true); return;
  }
  var as = e.target.closest && e.target.closest("[data-asort]");
  if (as) { state.asort = as.getAttribute("data-asort"); try { localStorage.setItem("ca-asort", JSON.stringify(state.asort)); } catch (x) {} render(); return; }
  if (e.target.id === "clearall") { state.q = ""; $("q").value = ""; state.city = ""; state.near = false; setRange("", ""); return; }
  var a = e.target.closest("[data-act]"); if (!a) return;
  var ev = a.closest(".ev"), id = ev && ev.getAttribute("data-id"), act = a.getAttribute("data-act");
  if (!id) return;
  if (act === "open") { state.open = state.open === id ? null : id; render(true); return; }
  e.stopPropagation(); toggle(id, act);
});
$("out").addEventListener("input", function (e) {
  if (!e.target.hasAttribute("data-rv")) return;
  var row0 = e.target.closest("[data-aid]"); if (row0) setReview(row0.getAttribute("data-aid"), "txt", e.target.value.trim());
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
fetch("data/events.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (d) {
  init(d);
  var u = new Date(d.updated);
  if (window.__splashReady) window.__splashReady("Agenda bijgewerkt " + DOW[u.getDay()] + " " + u.getDate() + " " + MON[u.getMonth()] + " " + pad(u.getHours()) + ":" + pad(u.getMinutes()) + " · " + ALL.filter(function (c) { return c.d >= TODAY; }).length + " concerten");
}).catch(function () {
  if (window.__splashReady) window.__splashReady("Geen verbinding: je ziet de laatst bekende agenda");
  $("out").innerHTML = '<div class="empty"><b>Agenda niet geladen</b>Controleer je verbinding en probeer het opnieuw.</div>';
});

try { if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js"); } catch (e) {}

})();
