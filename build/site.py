# -*- coding: utf-8 -*-
"""Generates the Shinsei Export multi-page site (EN at root, JA under /ja/)."""
import os, shutil, json, html
from content import PACKS
from css import CSS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
STEP_WORD = {"en": "Step", "ja": "手順"}

IMG_ALT = {
    "en": {
        "band": "A container ship and gantry cranes at a Japanese export port, with stacked containers on the quay",
        "engine": "A used engine and transmission set placed on a work mat in our yard",
        "container": "An export container loaded with used car doors and body parts, secured with belts",
        "loading": "Used engines and transmissions loaded on a truck bed for transport",
        "port": "Used engines and transmissions loaded on a truck bed at our yard",
    },
    "ja": {
        "band": "日本の輸出港に着岸したコンテナ船とガントリークレーン、岸壁に並ぶコンテナ",
        "engine": "ヤードのマットの上に置かれた中古エンジンとトランスミッションのセット",
        "container": "中古のドアやボディパーツをベルトで固定して積み込んだ輸出コンテナ",
        "loading": "運搬のためトラックの荷台に積み込まれた中古エンジンとトランスミッション",
        "port": "ヤードでトラックの荷台に積み込まれた中古エンジンとトランスミッション",
    },
}


JS = """
(function(){
  var hdr=document.querySelector('.hdr');
  var onS=function(){ if(hdr) hdr.classList.toggle('is-solid', window.scrollY>20); };
  onS(); window.addEventListener('scroll',onS,{passive:true});

  var b=document.getElementById('burger'), d=document.getElementById('drwr');
  if(b&&d){
    b.addEventListener('click',function(){
      var o=d.classList.toggle('is-open');
      b.setAttribute('aria-expanded',o?'true':'false');
      document.body.style.overflow=o?'hidden':'';
    });
    d.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click',function(){
        d.classList.remove('is-open'); b.setAttribute('aria-expanded','false'); document.body.style.overflow='';
      });
    });
  }

  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var rvs=document.querySelectorAll('.rv');
  if(reduce||!('IntersectionObserver' in window)){
    rvs.forEach(function(el){el.classList.add('is-in');});
  } else {
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); } });
    },{rootMargin:'0px 0px -8% 0px',threshold:0.08});
    rvs.forEach(function(el){io.observe(el);});
  }

  var form=document.getElementById('buyerForm');
  if(form){
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var missing=[];
      form.querySelectorAll('[data-req="1"]').forEach(function(el){
        if(!el.value.trim()) missing.push(el.getAttribute('data-label'));
      });
      var ag=document.getElementById('agree');
      if(ag && !ag.checked) missing.push(form.getAttribute('data-agree'));
      var msg=document.getElementById('formMsg');
      var btn=form.querySelector('button[type="submit"]');
      if(missing.length){
        msg.textContent=form.getAttribute('data-msg-missing').replace('{fields}', missing.join(', '));
        msg.classList.add('is-on'); msg.classList.remove('is-ok');
        return;
      }
      msg.textContent=form.getAttribute('data-msg-sending');
      msg.classList.add('is-on'); msg.classList.remove('is-ok');
      if(btn) btn.disabled=true;
      fetch(form.getAttribute('action'),{method:'POST',body:new FormData(form),headers:{'Accept':'application/json'}})
        .then(function(r){return r.json();})
        .then(function(j){
          if(j&&j.success){
            form.reset();
            msg.textContent=form.getAttribute('data-msg-ok');
            msg.classList.add('is-on','is-ok');
          }else{
            msg.textContent=form.getAttribute('data-msg-error');
            msg.classList.add('is-on');
          }
        })
        .catch(function(){
          msg.textContent=form.getAttribute('data-msg-error');
          msg.classList.add('is-on');
        })
        .finally(function(){ if(btn) btn.disabled=false; });
    });
  }

  /* destination map: white basemap + region filter buttons */
  var dmap=document.getElementById('destMap');
  if(dmap){
    var dnote=document.getElementById('destMapFallback');
    var dbtns=document.querySelectorAll('.rfilter button');
    var dcards=document.querySelectorAll('.ctry__c');
    var fail=function(){ dmap.classList.add('map--off'); if(dnote) dnote.hidden=false; };
    if(window.L){
      try{
        var pts=JSON.parse(dmap.getAttribute('data-map'));
        var dml=L.map(dmap,{scrollWheelZoom:false,worldCopyJump:true});
        var TILES=[
          {tpl:'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
           ref:'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
           max:16,att:'Tiles &copy; Esri'},
          {tpl:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
           ref:null,max:19,att:'Tiles &copy; Esri'}
        ];
        function drawTiles(t){
          L.tileLayer(t.tpl,{maxZoom:t.max,attribution:t.att}).addTo(dml);
          if(t.ref){ L.tileLayer(t.ref,{maxZoom:t.max}).addTo(dml); }
        }
        function probeTiles(t,cb){
          var u=t.tpl.replace('{z}','1').replace('{x}','1').replace('{y}','0');
          var im=new Image();
          im.onload=function(){cb(true)};
          im.onerror=function(){cb(false)};
          im.src=u;
        }
        probeTiles(TILES[0],function(ok){
          if(ok){drawTiles(TILES[0]);return;}
          probeTiles(TILES[1],function(ok2){
            if(ok2){drawTiles(TILES[1]);return;}
            fail();
          });
        });
        var dio=L.divIcon({className:'pin',html:'<span></span>',iconSize:[12,12],iconAnchor:[6,6]});
        var dm=[];
        pts.forEach(function(pt){
          var mk=L.marker([pt[1],pt[2]],{icon:dio,title:pt[0]}).bindPopup('<b>'+pt[0]+'</b><br>'+pt[3]);
          dm.push({m:mk,r:pt[3],ll:[pt[1],pt[2]]});
        });
        var dshow=function(reg){
          var vis=[];
          dm.forEach(function(o){
            if(reg==='*'||o.r===reg){
              if(!dml.hasLayer(o.m)) o.m.addTo(dml);
              vis.push(o.ll);
            } else if(dml.hasLayer(o.m)){ dml.removeLayer(o.m); }
          });
          for(var ci=0;ci<dcards.length;ci++){
            dcards[ci].hidden = !(reg==='*'||dcards[ci].getAttribute('data-region')===reg);
          }
          if(vis.length){ dml.fitBounds(vis,{padding:[50,50],maxZoom:(reg==='*'?3:5)}); }
        };
        dbtns.forEach(function(btn){
          btn.addEventListener('click',function(){
            dbtns.forEach(function(b){ b.classList.remove('is-on'); b.setAttribute('aria-pressed','false'); });
            btn.classList.add('is-on'); btn.setAttribute('aria-pressed','true');
            dshow(btn.getAttribute('data-region'));
          });
        });
        dshow('*');
      }catch(err){ fail(); }
    } else { fail(); }
  }
})();
"""

ORDER = ["top", "about", "supply", "detail", "parts", "process", "why", "dest", "contact"]


def esc(s):
    return s


def esc_attr(v):
    return v.replace("&", "&amp;").replace('"', "&quot;")


def nav_html(P, key):
    out = []
    for k, lab in P["nav"]:
        cur = ' class="is-on" aria-current="page"' if k == key else ""
        out.append('<a href="%s"%s>%s</a>' % (P["file"][k], cur, lab))
    return "".join(out)


def drawer_html(P, key):
    out = []
    for i, (k, lab) in enumerate(P["nav"]):
        cur = ' class="is-on"' if k == key else ""
        out.append('<a href="%s"%s>%s <i>%02d</i></a>' % (P["file"][k], cur, lab, i))
    return "".join(out)


def langsw_html(P, key):
    other = P["other_prefix"] + P["file"][key]
    return ('<span class="langsw"><a class="is-on" href="%s">%s</a>'
            '<a href="%s">%s</a></span>' % (P["file"][key], P["lang_self"], other, P["lang_other"]))


def header_html(P, key):
    return """<header class="hdr" id="top">
  <div class="wrap hdr__top">
    <a class="brand" href="%s">
      <span class="brand__mark">JP</span>
      <span class="brand__txt"><span class="brand__name">Shinsei Export</span>
      <span class="brand__sub">%s</span></span>
    </a>
    <div class="hdr__right">
      %s
      <a class="btn btn--pri btn--sm" href="%s">%s</a>
      <button class="burger" id="burger" aria-label="%s" aria-expanded="false"><span></span></button>
    </div>
  </div>
  <div class="hdr__nav"><div class="wrap"><nav class="nav" aria-label="Sections">%s</nav></div></div>
</header>
<div class="drwr" id="drwr">%s<div class="drwr__foot">%s</div></div>""" % (
        P["file"]["top"], P["brand_sub"], langsw_html(P, key), P["file"]["contact"], P["cta"], P["menu"],
        nav_html(P, key), drawer_html(P, key), langsw_html(P, key))


def ticker_html(P):
    unit = "".join("<span>%s</span><b>/</b>" % t for t in P["ticker"])
    return '<div class="tick"><div class="tick__row">%s%s</div></div>' % (unit, unit)


def rail_html(P):
    return ""
    items = "".join('<a href="%s"><span class="rail__bar"></span><span class="rail__t">%s</span></a>'
                    % (P["file"][k], lab) for lab, k in P["rail"])
    return '<aside class="rail" aria-label="%s"><span class="rail__h">%s</span>%s</aside>' % (P["rail_title"], P["rail_title"], items)


def phead_html(P, key, d):
    return """<section class="phead grain"><div class="phead__code">%s</div>
  <div class="wrap phead__in">
    <p class="crumb"><a href="%s">%s</a><i>/</i><span>%s</span></p>
    <h1 class="h1">%s</h1>
    <p class="lead">%s</p>
  </div></section>""" % (d["code"], P["file"]["top"], P["nav"][0][1], d["crumb"], d["h1"], d["lead"])


def next_html(P, key):
    i = ORDER.index(key)
    nk = ORDER[(i + 1) % len(ORDER)]
    lab = dict((k, l) for k, l in P["nav"])[nk]
    return ('<section class="next"><div class="wrap next__in"><span class="next__l">%s</span>'
            '<a class="next__t" href="%s">%s <span aria-hidden="true">&rarr;</span></a></div></section>'
            % (P["next_label"], P["file"][nk], lab))


def footer_html(P, key):
    F = P["foot"]
    s = '<footer class="ftr"><div class="wrap"><div class="ftr__grid"><div>'
    s += '<p class="ftr__name">%s</p><p class="ftr__sub">%s</p></div>' % (F["name"], F["sub"])
    s += '<nav aria-label="Footer">%s</nav></div>' % nav_html(P, key)
    s += ('<div class="ftr__bar"><span>%s</span><span>%s</span>'
          '<span class="ftr__mail"><a href="mailto:%s">%s</a></span>'
          '<a class="btt" href="#top">%s &uarr;</a></div></div></footer>'
          % (F["copy"], F["note"], P["email"], P["email"], F["back"]))
    return s


def shell(P, key, body, title, desc):
    return """<!DOCTYPE html>
<html lang="%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:type" content="website">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
%s
%s
<style>%s</style>
</head>
<body>
%s
%s
%s
<main>
%s
</main>
%s
<script>%s</script>
</body>
</html>
""" % (P["html_lang"], title, desc, title, desc, seo_head(P, key, title, desc), HEAD_EXTRA.get(key, ""), CSS, header_html(P, key), ticker_html(P), rail_html(P),
       body, next_html(P, key), JS)


# ------------------------------------------------------------------ pages
def tpl_top(P):
    d = P["p"]["top"]
    strip = []
    for c in d["strip"]:
        inner = '<span class="strip__lab">%s</span><p class="strip__val">%s</p><p>%s</p>' % (c["lab"], c["val"], c["text"])
        if c["bullets"]:
            inner += "<ul>" + "".join("<li>%s</li>" % b for b in c["bullets"]) + "</ul>"
        if c["link"]:
            lab, k = c["link"]
            inner += '<a class="link-m" href="%s">%s <span>&rarr;</span></a>' % (P["file"][k], lab)
        strip.append('<div class="strip__c">%s</div>' % inner)
    strip.append('<div class="strip__c strip__main"><span class="strip__lab">%s</span>'
                 '<p class="strip__val">%s</p><p>%s</p></div>'
                 % (d["strip"][2]["lab"], d["strip"][2]["val"], d["strip"][2]["text"]))
    strip = strip[:2] + [strip[-1]]

    toc = []
    for k, lab in P["nav"][1:]:
        i = "%02d" % (P["nav"].index((k, lab)))
        toc.append('<a class="toc__i" href="%s"><span class="toc__n">%s</span><span><span class="toc__t">%s</span>'
                   '<span class="toc__d">%s</span></span></a>' % (P["file"][k], i, lab, d["toc"][k]))

    mini = []
    for i, t in enumerate(d["steps"]):
        mini.append('<div class="mini__c"><span class="mini__n">%02d</span><span class="mini__t">%s</span></div>'
                    % (i + 1, t))

    regions = "".join('<span class="chip"><b>%02d</b>%s</span>' % (i + 1, r) for i, r in enumerate(d["regions"]))

    pre = "" if P["code"] == "en" else "../"
    A = IMG_ALT[P["code"]]
    band = ('<section class="shband shband--hero"><img src="%simg/hero-factory-1440.jpg" width="1440" height="810" '
            'alt="%s" decoding="async" fetchpriority="high"></section>' % (pre, esc_attr(A["band"])))
    shots = ('<div class="shots rv">'
             '<figure><img src="%simg/engine-900.jpg" width="900" height="675" alt="%s" decoding="async"></figure>'
             '<figure><img src="%simg/container-900.jpg" width="900" height="675" alt="%s" decoding="async"></figure>'
             '<figure><img src="%simg/loading-900.jpg" width="900" height="675" alt="%s" decoding="async"></figure>'
             '</div>') % (pre, esc_attr(A["engine"]), pre, esc_attr(A["container"]), pre, esc_attr(A["loading"]))

    return """<section class="hero grain">
  <div class="hero__glow"></div>
  <div class="wrap hero__in">
    <span class="tag">%s</span>
    <div class="hero__grid">
      <div>
        <h1 class="h1">%s</h1>
        <div class="hero__body"><p>%s</p><p>%s</p></div>
        <div class="hero__cta">
          <a class="btn btn--pri" href="%s">%s <span aria-hidden="true">&rarr;</span></a>
          <a class="btn btn--ghost" href="%s">%s</a>
        </div>
      </div>
      <div class="stamp"><span><b>%s</b>%s<br>%s</span></div>
    </div>
    <div class="strip">%s</div>
  </div>
</section>
%s
<section class="sect">
  <div class="wrap">
    <div class="sh rv"><div class="sh__l"><p class="eyebrow"><span class="code">00</span> %s</p>
      <h2 class="h2">%s</h2></div><p class="lead">%s</p></div>
    <div class="toc rv">%s</div>
  </div>
</section>

<section class="sect on-mist">
  <div class="wrap">
    <div class="sh rv"><div class="sh__l"><p class="eyebrow"><span class="code">05</span> %s</p>
      <h2 class="h2">%s</h2></div>
      <p class="lead">%s</p></div>
    %s
    <div class="mini rv">%s</div>
    <p class="rv" style="margin-top:1.6rem"><a class="btn btn--ghost" href="%s">%s</a></p>
  </div>
</section>

<section class="sect">
  <div class="wrap">
    <div class="sh rv"><div class="sh__l"><p class="eyebrow"><span class="code">07</span> %s</p>
      <h2 class="h2">%s</h2></div><p class="lead">%s</p></div>
    <div class="regions rv">%s</div>
  </div>
</section>

<section class="band">
  <div class="wrap band__in rv">
    <div><p class="eyebrow"><span class="code">08</span> %s</p><h2 class="h2">%s</h2>
      <p class="lead" style="color:#C3D2E0">%s</p></div>
    <p style="margin:0"><a class="btn btn--pri" href="%s">%s <span aria-hidden="true">&rarr;</span></a></p>
  </div>
</section>""" % (
        d["tag"], d["h1"], d["body"][0], d["body"][1], P["file"]["contact"], d["cta1"], P["file"]["process"], d["cta2"],
        d["stamp"][0], d["stamp"][1], d["stamp"][2],
        "".join(strip), band, d["toc_h2"], d["toc_h2"], d["toc_lead"], "".join(toc),
        d["steps_h2"], d["steps_h2"], P["p"]["process"]["lead"], shots, "".join(mini), P["file"]["process"], d["cta2"],
        d["dest_h2"], d["dest_h2"], d["dest_lead"], regions,
        d["cta_h2"], d["cta_h2"], d["cta_lead"], P["file"]["contact"], d["cta1"])


def tpl_about(P):
    d = P["p"]["about"]
    specs = "".join('<div class="specs__r"><dt>%s</dt><dd><i>%02d</i>%s</dd></div>' % (k, i + 1, v)
                    for i, (k, v) in enumerate(d["specs"]))
    body = phead_html(P, "about", d) + """
<section class="sect">
  <div class="wrap">
    <div class="about__grid">
      <div class="about__copy rv">%s</div>
      <div class="specs rv"><p class="specs__h">%s</p><dl>%s</dl></div>
    </div>
  </div>
</section>""" % ("".join("<p>%s</p>" % p for p in d["body"]), d["specs_h"], specs)
    return d["title"], d["desc"], body


def tpl_supply(P):
    d = P["p"]["supply"]
    steps = "".join('<div class="steps__c"><span class="steps__n">%s</span><h3 class="h3">%s</h3><p>%s</p></div>'
                    % s for s in d["steps"])
    brands = "".join('<span class="chip">%s</span>' % b for b in d["brands"])
    body = phead_html(P, "supply", d) + """
<section class="sect">
  <div class="wrap">
    <div class="sh sh--tight sh--one rv"><div class="sh__l"><h2 class="h2">%s</h2></div></div>
    <div class="about__copy rv" style="max-width:74ch">%s</div>
    <div class="steps rv" style="margin-top:clamp(1.8rem,4vw,3rem)">%s</div>
    <div class="brands rv"><p class="brands__h">%s</p><div class="chipset">%s</div></div>
  </div>
</section>""" % (d["h1"], "".join("<p>%s</p>" % p for p in d["body"]), steps, d["brands_h"], brands)
    return d["title"], d["desc"], body


def tpl_detail(P):
    d = P["p"]["detail"]
    chips = "".join('<span class="chip"><b>%02d</b>%s</span>' % (i + 1, x) for i, x in enumerate(d["items"]))
    body = phead_html(P, "detail", d) + """
<section class="sect">
  <div class="wrap">
    <div class="chips rv">%s</div>
  </div>
</section>
<section class="sect on-mist">
  <div class="wrap">
    <div class="sh sh--one rv"><div class="sh__l"><p class="eyebrow"><span class="code">04</span> %s</p>
      <h2 class="h2">%s</h2></div></div>
    <div class="about__copy rv" style="max-width:74ch"><p>%s</p></div>
    <p class="rv" style="margin-top:1.6rem"><a class="btn btn--ink" href="%s">%s <span aria-hidden="true">&rarr;</span></a></p>
  </div>
</section>""" % (chips, d["next_h"], d["next_h"], d["next_p"], P["file"]["parts"],
                 dict(P["nav"])["parts"])
    return d["title"], d["desc"], body


def tpl_parts(P):
    d = P["p"]["parts"]
    blocks = "".join('<div class="blk"><span class="idx">%s</span><h3>%s</h3><p>%s</p></div>' % b
                     for b in d["blocks"])
    body = phead_html(P, "parts", d) + """
<section class="sect on-mist">
  <div class="wrap">
    <div class="blocks rv">%s</div>
  </div>
</section>""" % blocks
    return d["title"], d["desc"], body


def tpl_process(P):
    d = P["p"]["process"]
    steps = "".join('<div class="rstep"><div class="rstep__top"><span class="rstep__n">%s</span>'
                    '<span class="rstep__k">%s%s</span></div><h3>%s</h3><p>%s</p></div>'
                    % (s[0], STEP_WORD[P["code"]], s[0], s[1], s[2]) for s in d["steps"])
    body = phead_html(P, "process", d) + """
<section class="sect on-mist">
  <div class="wrap"><div class="route rv">%s</div></div>
</section>""" % steps
    return d["title"], d["desc"], body


def tpl_why(P):
    d = P["p"]["why"]
    items = "".join('<div class="why__c"><h3><span>%s</span>%s</h3><p>%s</p></div>' % i for i in d["items"])
    body = phead_html(P, "why", d) + """
<section class="sect">
  <div class="wrap"><div class="why rv">%s</div></div>
</section>""" % items
    return d["title"], d["desc"], body


def tpl_dest(P):
    d = P["p"]["dest"]
    cards = []
    pts = []
    for i, (rlab, countries) in enumerate(d["countries"]):
        lis = []
        for name, lat, lng in countries:
            lis.append("<li>%s</li>" % name)
            pts.append([name, lat, lng, rlab])
        cards.append('<div class="ctry__c" data-region="%s"><h3 class="ctry__h"><span>%02d</span>%s</h3><ul>%s</ul></div>'
                     % (esc_attr(rlab), i + 1, rlab, "".join(lis)))
    btns = ['<button type="button" class="is-on" data-region="*" aria-pressed="true">%s</button>' % d["filter_all"]]
    for rlab, countries in d["countries"]:
        btns.append('<button type="button" data-region="%s" aria-pressed="false">%s</button>'
                    % (esc_attr(rlab), rlab))
    data = json.dumps(pts, ensure_ascii=False).replace("&", "&amp;")
    band = ('<section class="shband"><img src="%simg/port-1440.jpg" width="1440" height="810" '
            'alt="%s" decoding="async"></section>'
            % (("" if P["code"] == "en" else "../"), esc_attr(IMG_ALT[P["code"]]["port"])))
    body = phead_html(P, "dest", d) + """
%s
<section class="sect on-mist">
  <div class="wrap">
    <div class="rfilter rv" role="group" aria-label="%s">%s</div>
    <div class="mapwrap rv">
      <div class="map" id="destMap" data-map='%s'></div>
      <p class="mapnote">%s</p>
      <p class="mapnote" id="destMapFallback" hidden>%s</p>
    </div>
  </div>
</section>
<section class="sect">
  <div class="wrap">
    <div class="sh sh--one rv"><div class="sh__l"><p class="eyebrow"><span class="code">07</span> %s</p>
      <h2 class="h2">%s</h2></div></div>
    <div class="ctry rv">%s</div>
    <div class="dest__grid rv"><h3>%s</h3><p>%s</p></div>
  </div>
</section>""" % (band, d["countries_eyebrow"], "".join(btns), data, d["map_note"], d["map_fallback"],
                 d["countries_eyebrow"], d["countries_h2"], "".join(cards), d["h3"], d["body"])
    return d["title"], d["desc"], body


def tpl_contact(P):
    d = P["p"]["contact"]
    fields = []
    for fid, lab, typ, ac, req, dlab in d["fields"]:
        star = "<i>*</i>" if req else ""
        fields.append('<div class="f%s"><label for="%s">%s%s</label><input id="%s" name="%s" type="%s" '
                      'autocomplete="%s"%s data-label="%s"></div>'
                      % ("", fid, lab, star, fid, fid, typ, ac, ' data-req="1" required' if req else "", dlab))
    fields[0] = fields[0].replace('<div class="f">', '<div class="f f--full">')
    fields.append('<div class="f f--full"><label for="message">%s<i>*</i></label>'
                  '<textarea id="message" name="message" required data-req="1" data-label="%s"></textarea></div>'
                  % (d["message_label"], d["message_label"]))
    notes = "".join("<li>%s</li>" % n for n in d["note"])
    body = phead_html(P, "contact", d) + """
<section class="sect">
  <div class="wrap">
    <div class="contact__grid">
      <div class="note rv"><p class="note__h">%s</p><ul>%s</ul>
        <div class="mailbox"><span class="mailbox__lab">%s</span><a href="mailto:%s">%s</a></div></div>
      <form class="f-grid rv" id="buyerForm" action="https://api.web3forms.com/submit" method="POST" novalidate
            data-agree="%s" data-msg-missing="%s" data-msg-ok="%s" data-msg-sending="%s" data-msg-error="%s">
        <input type="hidden" name="access_key" value="ab948f0c-bad5-4e53-91c0-ab2c894c9dd5">
        <input type="hidden" name="subject" value="Shinsei Export - Buyer application form">
        <input type="hidden" name="from_name" value="Shinsei Export website">
        <input type="hidden" name="botcheck" value="">
        <p class="form__title" style="grid-column:1/-1">%s</p>
        %s
        <label class="f-check f--full" for="agree"><input id="agree" name="agree" type="checkbox" required>
          <span>%s</span></label>
        <p class="form__msg" id="formMsg" role="status"></p>
        <div class="form__foot">
          <button class="btn btn--pri" type="submit">%s <span aria-hidden="true">&rarr;</span></button>
          <span class="form__note">%s &middot; %s: <a href="mailto:%s">%s</a></span>
        </div>
      </form>
    </div>
  </div>
</section>""" % (d["note_h"], notes, d["email_label"], P["email"], P["email"], d["data_agree"], d["msg_missing"], d["msg_ok"], d["msg_sending"], d["msg_error"], d["form_title"],
                 "".join(fields), d["agree"], d["btn"], d["foot_note"], d["email_label"], P["email"], P["email"])
    return d["title"], d["desc"], body


TPL = {"top": tpl_top, "about": tpl_about, "supply": tpl_supply, "detail": tpl_detail,
       "parts": tpl_parts, "process": tpl_process, "why": tpl_why, "dest": tpl_dest, "contact": tpl_contact}


SITE_URL = "https://shinseiexport-sudo.github.io/carexport/"   # live GitHub Pages site
LASTMOD = "2026-10-14"
SITE_NAME = "Shinsei Export"
HEAD_EXTRA = {"dest": '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">\n'
                      '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'}
GSC = "2zKAr9KS1fjXInJx9Lmh07sJubR0UfiaeLRn8hGXsTc"
AREA = ["Africa", "Middle East", "Asia", "South America", "Trinidad & Tobago", "Thailand",
        "South Africa", "Russia", "Philippines", "Peru", "Nigeria", "New Zealand",
        "Mauritius", "Malaysia", "Cyprus", "Bolivia", "Dubai", "Syria", "Pakistan"]
PAGE_TYPE = {"about": "AboutPage", "contact": "ContactPage", "supply": "CollectionPage",
             "detail": "CollectionPage", "parts": "CollectionPage"}
SERVICE_PAGES = ("supply", "detail", "parts", "process", "dest")
SERVICE_TYPE = {"en": "Export of Japanese used engines, transmissions, half cuts and auto parts",
                "ja": "\u65e5\u672c\u88fd\u4e2d\u53e4\u30a8\u30f3\u30b8\u30f3\u30fb\u30c8\u30e9\u30f3\u30b9\u30df\u30c3\u30b7\u30e7\u30f3\u30fb\u30cf\u30fc\u30d5\u30ab\u30c3\u30c8\u30fb\u81ea\u52d5\u8eca\u90e8\u54c1\u306e\u8f38\u51fa"}
SEO = {
 ("en", "top"): ("Japanese Used Engines, Transmissions & Half Cut Exporter | Shinsei Export, Osaka",
   "Direct export from Japan: used Japanese engines (G / D), transmissions, half cuts and body parts, bought at Japanese auto auctions and dismantled in Osaka. Order-based supply for workshops, mechanics and wholesalers in Africa, the Middle East, Asia and South America."),
 ("en", "about"): ("About Shinsei Export | Osaka-Based Japanese Auto Parts Exporter",
   "Shinsei Export is an Osaka-based supplier of Japanese engines, transmissions, half cuts and essential auto parts for overseas workshops and wholesalers. No over-stocking: we buy at major Japanese auto auctions to your order and dismantle them for your container."),
 ("en", "supply"): ("Order-Based Supply System | Used Japanese Engines & Transmissions from Auctions",
   "How our order-based supply works: we purchase the exact vehicles you need from Japanese auto auctions (Toyota, Nissan, Honda, Mazda, Mitsubishi, Subaru, Suzuki, Daihatsu), then dismantle and pack engine + transmission sets, half cuts and body parts."),
 ("en", "detail"): ("Dismantled Parts List | Used Engines, Transmissions, Half Cuts & Body Parts",
   "Parts we dismantle to your order: engines (G / D), transmissions, nose cuts and half cuts, front and rear doors, hoods, tailgates, headlights, taillights, bumpers, suspension components, ABS units and more."),
 ("en", "parts"): ("Available Parts on Request | Engines, Body Parts & Half Cuts | Shinsei Export",
   "No large ready stock. Engines, body parts, half cuts / nose cuts are prepared only after we purchase complete vehicles at Japanese auto auctions for your order."),
 ("en", "process"): ("Export Process | Auction Purchase, Dismantling & Container Shipping from Japan",
   "Our export process step by step: inquiry, confirmation and agreement, auction purchase, dismantling and sorting, container loading, and export from Japan under the agreed shipping terms (FOB Japan, etc.)."),
 ("en", "why"): ("Why Buyers Choose Us | Accurate Vehicle Selection & Safe Container Loading",
   "Accurate vehicle selection, professional dismantling, safe and organized container loading, transparent and honest business, and long-term supply support. All work is handled by our team in Osaka, Japan."),
 ("en", "dest"): ("Shipping Destinations | Africa, Middle East, Asia & South America | Shinsei Export",
   "We export Japanese engines, transmissions, half cuts and dismantled auto parts to Dubai (UAE), Syria, Pakistan, Trinidad & Tobago, Thailand, South Africa, Russia, the Philippines, Peru, Nigeria, New Zealand, Mauritius, Malaysia, Cyprus, Bolivia and many other regions."),
 ("en", "contact"): ("Buyer Application Form | Contact Shinsei Export for Japanese Auto Parts",
   "Request Japanese engines, transmissions, half cuts and body parts. Please read our Trading Terms & Conditions before filling out the buyer application form. All information must be entered in English."),
 ("ja", "top"): ("中古エンジン・トランスミッション・ハーフカットの輸出｜大阪の中古自動車部品輸出業者 Shinsei Export",
   "日本・大阪から、中古エンジン（G／D）、トランスミッション、ハーフカット、ボディパーツを直接輸出。ご注文に合わせてオークションで車両を購入し、分解して、世界各地の整備工場・卸売業者様へ安定供給します。"),
 ("ja", "about"): ("会社概要｜大阪の中古エンジン・ハーフカット輸出業者 Shinsei Export",
   "Shinsei Exportは、海外の整備工場・卸売業者様向けに、日本製エンジン、トランスミッション、ハーフカット、自動車部品を供給する大阪の企業です。大量在庫は保有せず、ご注文に基づいてオークションで車両を購入し、分解します。"),
 ("ja", "supply"): ("受注ベースの供給システム｜オークションからエンジン・ハーフカットを手配",
   "ご指定のモデルに合わせて日本のオークションで車両を購入し、分解。エンジン＋トランスミッションのセット、ハーフカット、ボディパーツをご用意します（トヨタ・日産・ホンダ・マツダ・三菱・スバル・スズキ・ダイハツ）。"),
 ("ja", "detail"): ("分解部品リスト｜中古エンジン・トランスミッション・ハーフカット・ボディパーツ",
   "ご要望に応じて分解できる部品：エンジン（G／D）、トランスミッション、ノーズカット／ハーフカット、ドア、ボンネット、テールゲート、ヘッドライト、バンパー、サスペンション部品、ABSユニットなど。"),
 ("ja", "parts"): ("取扱部品（受注後に手配）｜エンジン・ボディパーツ・ハーフカット",
   "エンジンやボディパーツの大量在庫は保有していません。ご注文に基づき日本のオークションで完成車を購入したのち、ハーフカットやノーズカットなどをご用意します。"),
 ("ja", "process"): ("取引の流れ｜オークションでの購入からコンテナ出港まで",
   "お問い合わせ、内容の確認とご合意、オークションでの購入、分解・仕分け、コンテナへの積み込み、日本からの輸出まで、流れを順にご案内します（FOB JAPAN など）。"),
 ("ja", "why"): ("選ばれる理由｜正確な車両選定と安全なコンテナ積み込み",
   "正確な車両選定、確かな分解、整理されたコンテナ積み込み、透明な取引、長期的な供給サポート。作業はすべて大阪で行っています。"),
 ("ja", "dest"): ("輸出先｜アフリカ・中東・アジア・南米など世界各地へ輸出",
   "日本製エンジン、トランスミッション、ハーフカット、分解済み自動車部品を、ドバイ（UAE）、シリア、パキスタン、トリニダード・トバゴ、タイ、南アフリカ、ロシア、フィリピン、ペルー、ナイジェリア、ニュージーランド、モーリシャス、マレーシア、キプロス、ボリビアなどへ輸出しています。"),
 ("ja", "contact"): ("買い手申請フォーム｜お問い合わせ",
   "日本製エンジン、トランスミッション、ハーフカット、ボディパーツのお見積りはこちら。お申し込みの前に取引条件をご確認ください。"),
}


def seo_head(P, key, title, desc):
    f = P["file"][key]
    ja = P["code"] == "ja"
    base = SITE_URL.rstrip("/") + "/"
    home_dir = "ja/" if ja else ""
    url = base + home_dir + f
    en_url = base + f
    ja_url = base + "ja/" + f
    other_url = (base + f) if ja else (base + "ja/" + f)
    lang = "ja" if ja else "en"
    loc = "ja_JP" if ja else "en_US"
    alt_loc = "en_US" if ja else "ja_JP"
    nav = dict(P["nav"])
    t = html.unescape(title)
    d = html.unescape(desc)
    q = lambda v: v.replace('"', "&quot;")
    out = [
        '<!-- SEO: canonical / hreflang / sitemap base = %s -->' % SITE_URL,
        '<meta name="google-site-verification" content="%s">' % GSC,
        '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">',
        '<link rel="canonical" href="%s">' % url,
        '<link rel="alternate" hreflang="%s" href="%s">' % (lang, url),
        '<link rel="alternate" hreflang="%s" href="%s">' % (("en" if ja else "ja"), other_url),
        '<link rel="alternate" hreflang="x-default" href="%s">' % en_url,
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="%s">' % SITE_NAME,
        '<meta property="og:locale" content="%s">' % loc,
        '<meta property="og:locale:alternate" content="%s">' % alt_loc,
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:title" content="%s">' % q(t),
        '<meta property="og:description" content="%s">' % q(d),
        '<meta property="og:image" content="%simg/hero-factory-1440.jpg">' % base,
        '<meta property="og:image:width" content="1440">',
        '<meta property="og:image:height" content="810">',
        '<meta property="og:image:alt" content="%s">' % q(IMG_ALT[P["code"]]["band"]),
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image" content="%simg/hero-factory-1440.jpg">' % base,
        '<meta name="twitter:title" content="%s">' % q(t),
        '<meta name="twitter:description" content="%s">' % q(d),
    ]
    ld = []
    if key == "top":
        ld.append({"@context": "https://schema.org", "@type": "Organization",
                   "@id": base + "#organization", "name": "Shinsei Export / Shinsei Scrap",
                   "url": base, "description": d, "image": base + "img/hero-factory-1440.jpg",
                   "address": {"@type": "PostalAddress", "addressLocality": "Osaka", "addressCountry": "JP"},
                   "email": "ex@shinsei-ltd.co.jp",
                   "contactPoint": {"@type": "ContactPoint", "contactType": "sales",
                                    "email": "ex@shinsei-ltd.co.jp", "availableLanguage": ["en", "ja"]},
                   "areaServed": AREA, "knowsLanguage": ["en", "ja"]})
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "@id": base + "#website",
                   "url": base, "name": SITE_NAME, "inLanguage": lang,
                   "publisher": {"@id": base + "#organization"}})
    else:
        ld.append({"@context": "https://schema.org", "@type": PAGE_TYPE.get(key, "WebPage"),
                   "url": url, "name": t, "description": d, "inLanguage": lang,
                   "isPartOf": {"@id": base + "#website"}, "about": {"@id": base + "#organization"}})
    if key in SERVICE_PAGES:
        ld.append({"@context": "https://schema.org", "@type": "Service", "name": t,
                   "serviceType": SERVICE_TYPE[P["code"]],
                   "provider": {"@id": base + "#organization"}, "areaServed": AREA, "url": url})
    if key != "top":
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": nav["top"], "item": base + home_dir},
            {"@type": "ListItem", "position": 2, "name": nav[key], "item": url}]})
    for node in ld:
        out.append('<script type="application/ld+json">%s</script>'
                   % json.dumps(node, ensure_ascii=False, separators=(",", ":")))
    return "\n".join(out)


def write_extras():
    base = SITE_URL.rstrip("/") + "/"
    en = PACKS[0]["file"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for k in ORDER:
        en_url = base + en[k]
        ja_url = base + "ja/" + en[k]
        for u in (en_url, ja_url):
            sm += ["  <url>", "    <loc>%s</loc>" % u,
                   '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>' % en_url,
                   '    <xhtml:link rel="alternate" hreflang="ja" href="%s"/>' % ja_url,
                   '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % en_url,
                   "    <lastmod>%s</lastmod>" % LASTMOD, "  </url>"]
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % base)


BAND_BY_KEY = {
    "about":   ("hero-factory-1440.jpg", "container"),
    "supply":  ("port-1440.jpg", "loading"),
    "detail":  ("band-c-1440.jpg", "engine"),
    "parts":   ("hero-factory-1440.jpg", "container"),
    "process": ("port-1440.jpg", "loading"),
    "why":     ("band-c-1440.jpg", "engine"),
    "contact": ("port-1440.jpg", "loading"),
}


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    n = 0
    for P in PACKS:
        sub = OUT if P["code"] == "en" else os.path.join(OUT, "ja")
        os.makedirs(sub, exist_ok=True)
        for k in ORDER:
            if k == "top":
                title = P["p"]["top"]["title"]
                desc = P["p"]["top"]["desc"]
                body = tpl_top(P)
            else:
                title, desc, body = TPL[k](P)
            if k != "top" and k in BAND_BY_KEY:
                _fn, _ak = BAND_BY_KEY[k]
                _pre = "" if P["code"] == "en" else "../"
                body += ('<section class="shband"><img src="%simg/%s" width="1440" height="810" alt="%s" '
                         'decoding="async" loading="lazy"></section>') % (_pre, _fn, esc_attr(IMG_ALT[P["code"]][_ak]))
            if (P["code"], k) in SEO:
                title, desc = SEO[(P["code"], k)]
            html = shell(P, k, body, title, desc)
            with open(os.path.join(sub, P["file"][k]), "w", encoding="utf-8") as fh:
                fh.write(html)
            n += 1
    write_extras()
    web = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")
    imgs = 0
    if os.path.isdir(web):
        dst = os.path.join(OUT, "img")
        os.makedirs(dst, exist_ok=True)
        for fn in sorted(os.listdir(web)):
            if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                shutil.copy2(os.path.join(web, fn), os.path.join(dst, fn))
                imgs += 1
    print("generated", n, "HTML files + robots.txt + sitemap.xml +", imgs, "images into", os.path.normpath(OUT))


if __name__ == "__main__":
    build()
