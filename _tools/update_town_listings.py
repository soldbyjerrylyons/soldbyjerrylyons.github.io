"""Monthly "This Month" box on the town pages.

Rule (Jerry 2026-11-15, "only keep the 405"): the ONLY Baltimore number shown
anywhere public is Bright MLS's Baltimore Metro ("Baltimore area") figure from
the ONE shared record, data/market-numbers.json months[0].baltimore_metro.
Never show Baltimore County or Baltimore City figures. Never a town estimate.
No outside downloads.
Run from the repo root:  python _tools/update_town_listings.py
Prints what changed; exits 1 (and changes nothing) if the record can't be read.
"""
import html, json, re, sys

RECORD = "data/market-numbers.json"

# page -> town shown (every box shows the Baltimore area / Bright MLS Baltimore Metro figures)
PAGES = {
    "site-owings-mills.html": "Owings Mills",
    "site-pikesville.html":   "Pikesville",
    "site-reisterstown.html": "Reisterstown",
    "site-timonium.html":     "Lutherville-Timonium",
    "site-baltimore.html":    "Baltimore City",
}
START, END = "<!-- MONTHLY-LISTINGS:START -->", "<!-- MONTHLY-LISTINGS:END -->"


def money(v):
    v = float(v)
    return f"${v/1e6:.2f}M" if v >= 1e6 else f"${round(v/1000):,}K"


def pct(v):
    v = float(v)
    return ("+" if v > 0 else "&minus;" if v < 0 else "") + f"{abs(v):.1f}%"


def block(town, m):
    bm = m.get("baltimore_metro")
    if not bm or not bm.get("median_home_price"):
        return None
    month = m["month_label"]
    notice = html.escape(bm["notice"], quote=False).replace("®", "&reg;")
    tiles = [f'<div class="stat"><div class="num">{money(bm["median_home_price"])}</div><div class="lbl">Baltimore area median home price, {month} ({bm.get("median_home_price_change_text") or pct(bm["median_home_price_change_pct"]) + " vs. a year ago"})</div></div>']
    if bm.get("median_days_on_market") is not None:
        tiles.append(f'<div class="stat"><div class="num">{bm["median_days_on_market"]}</div><div class="lbl">Baltimore area median days on market, {month}</div></div>')
    if bm.get("new_listings") is not None:
        tiles.append(f'<div class="stat"><div class="num">{int(bm["new_listings"]):,}</div><div class="lbl">Baltimore area new listings, {month} ({pct(bm["new_listings_change_pct"])})</div></div>')
    tiles = "\n          ".join(tiles)
    return f"""{START}
        <h3 style="margin-top:20px;text-transform:none;font-size:1.1rem;">This Month in the Baltimore Area, {month}</h3>
        <div class="stats" style="grid-template-columns:repeat(auto-fit,minmax(130px,1fr));">
          {tiles}
        </div>
        <p style="margin-top:6px;color:var(--text-soft);font-size:.78rem;text-transform:none;">Figures are for the whole Baltimore area (Bright MLS Baltimore Metro), which includes {town}; not specific to {town}. {notice} Updated monthly.</p>
        {END}""", month


def main():
    try:
        rec = json.load(open(RECORD, encoding="utf-8"))
        m = rec["months"][0]
    except Exception as e:
        print(f"ERROR: could not read {RECORD}: {e}")
        sys.exit(1)
    new = {}
    for page, town in PAGES.items():
        b = block(town, m)
        if not b:
            print(f"ERROR: baltimore_metro missing in {RECORD} months[0]")
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
