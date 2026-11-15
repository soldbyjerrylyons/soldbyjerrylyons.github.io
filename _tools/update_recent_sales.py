"""Rebuild the Recently Sold blocks from _tools/recent_sales.csv.

CSV columns: closed_date (YYYY-MM-DD), city, price (whole dollars, blank = not shown), side (Buyer/Seller/Both).
Only closings where Jerry represented a side. No street addresses or client names (privacy).
Writes:
  site-recently-sold.html  <!-- RECENTLY-SOLD:START/END -->       all sales
  site-index.html           <!-- RECENTLY-SOLD-HOME:START/END -->  newest 6, then copies to index.html
usage: python3 _tools/update_recent_sales.py   (run from the website repo root)
"""
import csv, datetime, re, shutil, sys

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
SIDE = {"buyer": "Represented the buyer", "seller": "Represented the seller",
        "both": "Represented the buyer and seller"}

def load():
    rows = []
    with open("_tools/recent_sales.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = datetime.date.fromisoformat(r["closed_date"].strip())
            side = SIDE.get(r["side"].strip().lower())
            if not side:
                sys.exit(f"ERROR bad side: {r}")
            price = r["price"].strip()
            rows.append((d, r["city"].strip(), int(price) if price else None, side))
    rows.sort(key=lambda x: x[0], reverse=True)
    return rows

def card(d, city, price, side):
    p = f"${price:,}" if price else "Sold"
    return (
        '        <div class="card"><div class="card-body">\n'
        '          <span style="display:inline-block;background:var(--maroon);color:#fff;font-size:.72rem;font-weight:700;letter-spacing:.06em;padding:3px 9px;border-radius:4px;">SOLD</span>\n'
        f'          <div style="font-size:1.5rem;font-weight:700;color:var(--ink);margin-top:10px;">{p}</div>\n'
        f'          <div style="font-weight:600;margin-top:2px;">{city}, MD</div>\n'
        f'          <small>{side} &middot; Closed {MONTHS[d.month-1]} {d.year}</small>\n'
        '        </div></div>'
    )

def put(path, tag, html):
    t = open(path, encoding="utf-8").read()
    pat = re.compile(rf"(<!-- {tag}:START -->).*?(<!-- {tag}:END -->)", re.S)
    if not pat.search(t):
        sys.exit(f"ERROR no {tag} block in {path}")
    new = pat.sub(lambda m: m.group(1) + "\n" + html + "\n      " + m.group(2), t, count=1)
    if new != t:
        open(path, "w", encoding="utf-8", newline="").write(new)
        print("updated", path)
    return new != t

rows = load()
first_year = min(r[0].year for r in rows)
summary = (f'      <p class="center" style="color:var(--text-soft);margin:0 0 18px;">{len(rows)} closed sales since {first_year}'
           f' &middot; buyers and sellers across Maryland</p>')
grid_all = '      <div class="grid-3">\n' + "\n".join(card(*r) for r in rows) + "\n      </div>"
grid_home = '      <div class="grid-3">\n' + "\n".join(card(*r) for r in rows[:6]) + "\n      </div>"
put("site-recently-sold.html", "RECENTLY-SOLD", summary + "\n" + grid_all)
if put("site-index.html", "RECENTLY-SOLD-HOME", grid_home):
    shutil.copyfile("site-index.html", "index.html")
print(f"ok: {len(rows)} sales, newest {rows[0][0]}")
