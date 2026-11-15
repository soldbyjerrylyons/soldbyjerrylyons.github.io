"""Build the homepage 'Next Open House' box from _tools/open_houses.json.

open_houses.json = list of open houses Jerry is hosting:
  {"address": "123 Main St, Town, MD 21000", "start": "2026-11-21T11:00:00-05:00",
   "end": "2026-11-21T13:00:00-05:00", "price": 450000 or null, "beds": 3 or null, "baths": 2 or null}
One entry per open house date (Sat + Sun = two entries). Times are America/New_York with the offset
(-05:00 in winter, -04:00 in summer). Price/beds/baths only if they come from the listing record; else null.

Shows the 2 soonest open houses that haven't ended. Each card carries data-end, and a small script on the page
hides it once that time passes (and hides the whole box when none are left), so a past open house never shows
even if nobody rebuilds the site. No open houses ahead = the block is left empty.
Writes site-index.html <!-- NEXT-OPEN-HOUSE:START/END --> and copies it to index.html.
usage: python3 _tools/update_next_open_house.py   (from the website repo root)
"""
import datetime, html, json, re, shutil, sys

items = json.load(open("_tools/open_houses.json", encoding="utf-8"))
now = datetime.datetime.now(datetime.timezone.utc)
up = []
for it in items:
    s = datetime.datetime.fromisoformat(it["start"]); e = datetime.datetime.fromisoformat(it["end"])
    if s.tzinfo is None or e.tzinfo is None or e <= s:
        sys.exit(f"ERROR bad times: {it}")
    if e > now:
        up.append((s, e, it))
up.sort(key=lambda x: x[0])
up = up[:2]

def hour(d):
    h = d.strftime("%I").lstrip("0"); m = d.strftime("%M")
    return h + ("" if m == "00" else ":" + m) + d.strftime("%p").lower()

def card(s, e, it):
    addr = html.escape(it["address"])
    when = f'{s.strftime("%a")}, {s.strftime("%b")} {s.day} &middot; {hour(s)}&ndash;{hour(e)}'
    facts = []
    if it.get("price"): facts.append(f'${int(it["price"]):,}')
    if it.get("beds"): facts.append(f'{it["beds"]} bd')
    if it.get("baths"): facts.append(f'{it["baths"]} ba')
    facts_html = f'\n          <p style="color:var(--text-soft);font-size:.9rem;margin-top:4px;">{" &bull; ".join(facts)}</p>' if facts else ""
    maps = "https://www.google.com/maps/search/?api=1&query=" + re.sub(r"\s+", "+", it["address"])
    return (
        f'        <div class="card oh-item" data-end="{e.isoformat()}"><div class="card-body">\n'
        f'          <span style="display:inline-block;background:var(--maroon);color:#fff;font-size:.72rem;font-weight:700;letter-spacing:.06em;padding:3px 9px;border-radius:4px;">OPEN HOUSE</span>\n'
        f'          <div style="font-weight:700;color:var(--ink);margin-top:10px;">{when}</div>\n'
        f'          <div style="font-weight:600;margin-top:2px;">{addr}</div>{facts_html}\n'
        f'          <p style="margin-top:12px;"><a class="btn btn-secondary btn-sm" href="{html.escape(maps)}" target="_blank" rel="noopener">Directions &#8599;</a></p>\n'
        f'        </div></div>'
    )

if up:
    n = len(up)
    block = (
        '  <section class="section" id="next-open-house" style="padding:34px 0;">\n'
        '    <div class="container">\n'
        f'      <h2 class="center" style="margin:0 auto 18px;">Upcoming Open House{"s" if n > 1 else ""}</h2>\n'
        f'      <div class="grid-3" style="grid-template-columns:repeat({n},1fr);max-width:{420 if n == 1 else 860}px;margin:0 auto;">\n'
        + "\n".join(card(*u) for u in up) + "\n"
        '      </div>\n'
        '      <p class="center" style="margin-top:16px;"><a href="site-open-houses.html">See all open houses &rarr;</a></p>\n'
        '    </div>\n'
        '  </section>\n'
        '  <script>(function(){var n=Date.now(),s=document.getElementById("next-open-house");if(!s)return;var left=0;'
        's.querySelectorAll(".oh-item").forEach(function(c){if(Date.parse(c.getAttribute("data-end"))<=n){c.remove();}else{left++;}});'
        'if(!left){s.remove();}else{var g=s.querySelector(".grid-3");g.style.gridTemplateColumns="repeat("+left+",1fr)";if(left===1){g.style.maxWidth="420px";}}})();</script>'
    )
else:
    block = ""

h = open("site-index.html", encoding="utf-8").read()
pat = re.compile(r"(<!-- NEXT-OPEN-HOUSE:START -->).*?(<!-- NEXT-OPEN-HOUSE:END -->)", re.S)
if not pat.search(h):
    sys.exit("ERROR no NEXT-OPEN-HOUSE block in site-index.html")
new = pat.sub(lambda m: m.group(1) + ("\n" + block + "\n  " if block else "\n  ") + m.group(2), h, count=1)
if new != h:
    open("site-index.html", "w", encoding="utf-8", newline="").write(new)
    shutil.copyfile("site-index.html", "index.html")
    print("updated homepage open house box")
print(f"ok: {len(up)} upcoming open house(s) shown")
