"""Monthly "This Month" box on the town pages (Jerry 2026-11-15).

Source: the ONE shared market record, data/market-numbers.json (Maryland
REALTORS Housing Statistics, Bright MLS data). Approved sources only give
COUNTY-level figures, so each town box shows its county's numbers, clearly
labeled as county-wide, with the record's Bright MLS source line. Never a
town-level estimate. No outside downloads.
Run from the repo root:  python _tools/update_town_listings.py
Prints what changed; exits 1 (and changes nothing) if the record can't be read.
"""
import html, json, re, sys

RECORD = "data/market-numbers.json"

# page -> (town shown, county area name exactly as in the record's counties[])
PAGES = {
    "site-owings-mills.html": ("Owings Mills", "Baltimore County"),
    "site-pikesville.html":   ("Pikesville", "Baltimore County"),
    "site-reisterstown.html": ("Reisterstown", "Baltimore County"),
    "site-timonium.html":     ("Lutherville-Timonium", "Baltimore County"),
    "site-baltimore.html":    ("Baltimore City", "Baltimore City"),
}
START, END = "<!-- MONTHLY-LISTINGS:START -->", "<!-- MONTHLY-LISTINGS:END -->"


def money(v):
    v = float(v)
    return f"${v/1e6:.2f}M" if v >= 1e6 else f"${round(v/1000):,}K"


def pct(v):
    v = float(v)
    return ("+" if v > 0 else "&minus;" if v < 0 else "") + f"{abs(v):.1f}%"


def block(town, area, m):
    row = next((c for c in m["counties"] if c["area"] == area), None)
    if not row:
        return None
    month = m["month_label"]
    notice = html.escape(m["notice"], quote=False).replace("®", "&reg;")
    title = f"This Month in {town}" if town != area else "This Month"
    scope = (f"County-wide figures for {area}, which includes {town}; "
             f"not specific to {town}. ") if town != area else ""
    return f"""{START}
        <h3 style="margin-top:20px;text-transform:none;font-size:1.1rem;">{title}: {area}, {month}</h3>
        <div class="stats" style="grid-template-columns:repeat(auto-fit,minmax(130px,1fr));">
          <div class="stat"><div class="num">{money(row['median_sale_price'])}</div><div class="lbl">{area} median sale price, {month} ({pct(row['median_price_change_pct'])} vs. a year ago)</div></div>
          <div class="stat"><div class="num">{int(row['units_sold']):,}</div><div class="lbl">{area} homes sold, {month}</div></div>
          <div class="stat"><div class="num">{row['months_of_inventory']}</div><div class="lbl">{area} months of inventory, {month}</div></div>
        </div>
        <p style="margin-top:6px;color:var(--text-soft);font-size:.78rem;text-transform:none;">{scope}{notice} Updated monthly.</p>
        {END}""", month


def main():
    try:
        rec = json.load(open(RECORD, encoding="utf-8"))
        m = rec["months"][0]
    except Exception as e:
        print(f"ERROR: could not read {RECORD}: {e}")
        sys.exit(1)
    new = {}
    for page, (town, area) in PAGES.items():
        b = block(town, area, m)
        if not b:
            print(f"ERROR: {area} not in {RECORD} months[0]")
            sys.exit(1)
        new[page] = b
    for page, (html_block, month) in new.items():
        text = open(page, encoding="utf-8").read()
        if START not in text:
            print(f"ERROR: no {START} marker in {page}")
            sys.exit(1)
        updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _m: html_block, text, flags=re.S)
        if updated != text:
            open(page, "w", encoding="utf-8", newline="").write(updated)
            print(f"updated {page} -> {month}")
        else:
            print(f"unchanged {page} ({month})")


if __name__ == "__main__":
    main()
