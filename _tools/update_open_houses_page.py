"""Build the Open Houses page (site-open-houses.html) from _tools/open_houses.json.

Same open_houses.json as update_next_open_house.py (one entry per open house date), plus an optional
"image": the open house flyer image URL from that listing's own job (media.flyer). Never another listing's image.

- <!-- WEEKLY-OPEN-HOUSES-START/END -->: one card per address with ALL its upcoming dates (soonest first),
  flyer image, price/beds/baths when known, Directions button. Each date line carries data-end and a small script
  removes past dates/cards on page load, so a finished open house never shows even if nobody rebuilds the page.
- <!-- DEFAULT-TEASER-START/END -->: the "no open houses right now" band from _default-teaser-snippet.html, wrapped in
  <div id="oh-teaser">; hidden while open houses are listed, shown again by the script once they've all passed.
usage: python3 _tools/update_open_houses_page.py   (from the website repo root)
"""
import datetime, html, json, re, sys

PAGE = "site-open-houses.html"
items = json.load(open("_tools/open_houses.json", encoding="utf-8"))
now = datetime.datetime.now(datetime.timezone.utc)

groups = {}
for it in items:
    s = datetime.datetime.fromisoformat(it["start"]); e = datetime.datetime.fromisoformat(it["end"])
    if s.tzinfo is None or e.tzinfo is None or e <= s:
        sys.exit(f"ERROR bad times: {it}")
    if e <= now:
        continue
    g = groups.setdefault(it["address"].strip(), {"dates": [], "info": {}})
    g["dates"].append((s, e))
    for k in ("price", "beds", "baths", "image"):
        if it.get(k) and not g["info"].get(k):
            g["info"][k] = it[k]
cards = sorted(groups.items(), key=lambda kv: min(d[0] for d in kv[1]["dates"]))

def hour(d):
    h = d.strftime("%I").lstrip("0"); m = d.strftime("%M")
    return h + ("" if m == "00" else ":" + m) + d.strftime("%p").lower()

def card(address, g):
    dates = sorted(g["dates"]); info = g["info"]; addr = html.escape(address)
    last_end = max(e for _, e in dates)
    lines = "\n".join(
        f'            <div class="oh-date" data-end="{e.isoformat()}" style="font-weight:700;color:var(--ink);">'
        f'{s.strftime("%A")}, {s.strftime("%b")} {s.day} &middot; {hour(s)}&ndash;{hour(e)}</div>'
        for s, e in dates)
    facts = []
    if info.get("price"): facts.append(f'${int(info["price"]):,}')
    if info.get("beds"): facts.append(f'{info["beds"]} bd')
    if info.get("baths"): facts.append(f'{info["baths"]} ba')
    facts_html = f'\n            <p style="color:var(--text-soft);font-size:.9rem;margin-top:6px;">{" &bull; ".join(facts)}</p>' if facts else ""
    img = ""
    if info.get("image"):
        if not str(info["image"]).startswith("https://"):
            sys.exit(f"ERROR image must be an https URL: {info['image']}")
        img = f'          <img src="{html.escape(info["image"])}" alt="Open house flyer for {addr}" loading="lazy">\n'
    maps = "https://www.google.com/maps/search/?api=1&query=" + re.sub(r"\s+", "+", address)
    return (
        f'        <div class="card oh-card" data-end="{last_end.isoformat()}">\n{img}'
        f'          <div class="card-body">\n'
        f'            <span class="badge">Open House</span>\n'
        f'            <h3 style="margin:10px 0 8px;">{addr}</h3>\n{lines}{facts_html}\n'
        f'            <p style="margin-top:14px;"><a class="btn btn-secondary btn-sm" href="{html.escape(maps)}" target="_blank" rel="noopener">Directions &#8599;</a>'
        f' <a class="btn btn-primary btn-sm" href="#open-house-form">Register</a></p>\n'
        f'          </div>\n        </div>'
    )

n = len(cards)
if n:
    weekly = (
        '\n  <section class="section" id="oh-list">\n'
        '    <div class="container">\n'
        f'      <h2 class="center" style="margin:0 auto 18px;">Upcoming Open House{"s" if n > 1 else ""}</h2>\n'
        f'      <div class="grid-3" style="grid-template-columns:repeat({min(n, 3)},1fr);max-width:{[0, 420, 900, 1200][min(n, 3)]}px;margin:0 auto;">\n'
        + "\n".join(card(a, g) for a, g in cards) + "\n"
        '      </div>\n'
        '    </div>\n'
        '  </section>\n'
        '  <style>@media(max-width:760px){#oh-list .grid-3{grid-template-columns:1fr!important;max-width:420px!important;}}</style>\n'
        '  <script>(function(){var n=Date.now(),s=document.getElementById("oh-list"),t=document.getElementById("oh-teaser");if(!s)return;var left=0;'
        's.querySelectorAll(".oh-card").forEach(function(c){c.querySelectorAll(".oh-date").forEach(function(d){if(Date.parse(d.getAttribute("data-end"))<=n)d.remove();});'
        'if(!c.querySelector(".oh-date")){c.remove();}else{left++;}});'
        'if(!left){s.remove();if(t)t.hidden=false;}else{var g=s.querySelector(".grid-3"),k=Math.min(left,3);g.style.gridTemplateColumns="repeat("+k+",1fr)";g.style.maxWidth=[0,420,900,1200][k]+"px";}})();</script>\n  '
    )
else:
    weekly = "\n  "

snippet = open("_default-teaser-snippet.html", encoding="utf-8").read().strip("\n")
teaser = f'\n  <div id="oh-teaser"{" hidden" if n else ""}>\n{snippet}\n  </div>\n  '

h = open(PAGE, encoding="utf-8").read()
for name, body in (("DEFAULT-TEASER", teaser), ("WEEKLY-OPEN-HOUSES", weekly)):
    pat = re.compile(rf"(<!-- {name}-START -->).*?(<!-- {name}-END -->)", re.S)
    if not pat.search(h):
        sys.exit(f"ERROR no {name} block in {PAGE}")
    h = pat.sub(lambda m: m.group(1) + body + m.group(2), h, count=1)
old = open(PAGE, encoding="utf-8").read()
if h != old:
    open(PAGE, "w", encoding="utf-8", newline="").write(h)
    print("updated open houses page")
print(f"ok: {n} upcoming open house listing(s) on the page")
