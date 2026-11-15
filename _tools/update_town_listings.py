"""Monthly "This Month in <Town>" box on the town pages.

Source: Realtor.com Economic Research public monthly data (no login).
Numbers are LISTING data (asking prices, homes for sale), not closed sales;
the box says so. Run from the repo root:  python _tools/update_town_listings.py
Prints what changed; exits 1 (and changes nothing) if the data can't be read.
"""
import csv, io, re, sys, urllib.request, calendar

ZIP_URL = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip.csv"
CTY_URL = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_County.csv"

# page -> (file kind, key, town name shown, area description in the source line)
PAGES = {
    "site-owings-mills.html": ("zip", "21117", "Owings Mills", "ZIP code 21117"),
    "site-pikesville.html":   ("zip", "21208", "Pikesville", "ZIP code 21208"),
    "site-reisterstown.html": ("zip", "21136", "Reisterstown", "ZIP code 21136"),
    "site-timonium.html":     ("zip", "21093", "Lutherville-Timonium", "ZIP code 21093"),
    "site-baltimore.html":    ("county", "24510", "Baltimore City", "Baltimore City"),
}
START, END = "<!-- MONTHLY-LISTINGS:START -->", "<!-- MONTHLY-LISTINGS:END -->"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))


def latest(rows, keycol, key):
    hits = [r for r in rows if r.get(keycol, "").zfill(5) == key]
    if not hits:
        return None
    return max(hits, key=lambda r: r["month_date_yyyymm"])


def money(v):
    v = float(v)
    return f"${v/1e6:.2f}M" if v >= 1e6 else f"${round(v/1000):,}K"


def block(row, town, area):
    ym = row["month_date_yyyymm"]
    month = f"{calendar.month_name[int(ym[4:])]} {ym[:4]}"
    price = money(row["median_listing_price"])
    active = f"{int(float(row['active_listing_count'])):,}"
    dom = str(int(float(row["median_days_on_market"])))
    return f"""{START}
        <h3 style="margin-top:20px;text-transform:none;font-size:1.1rem;">This Month in {town} ({month})</h3>
        <div class="stats" style="grid-template-columns:repeat(auto-fit,minmax(130px,1fr));">
          <div class="stat"><div class="num">{price}</div><div class="lbl">Median asking price, {month}</div></div>
          <div class="stat"><div class="num">{active}</div><div class="lbl">Homes for sale, {month}</div></div>
          <div class="stat"><div class="num">{dom}</div><div class="lbl">Median days on market, {month}</div></div>
        </div>
        <p style="margin-top:6px;color:var(--text-soft);font-size:.78rem;text-transform:none;">Source: Realtor.com&reg; Economic Research monthly housing data for {area}, {month}. Asking prices of homes listed for sale, not closed sale prices; data is reliable but not guaranteed. Updated monthly.</p>
        {END}""", month


def main():
    try:
        data = {"zip": (fetch(ZIP_URL), "postal_code"), "county": (fetch(CTY_URL), "county_fips")}
    except Exception as e:
        print(f"ERROR: could not download Realtor.com data: {e}")
        sys.exit(1)
    new = {}
    for page, (kind, key, town, area) in PAGES.items():
        rows, col = data[kind]
        row = latest(rows, col, key)
        if not row or not row.get("median_listing_price") or not row.get("active_listing_count") or not row.get("median_days_on_market"):
            print(f"ERROR: no complete row for {town} ({key})")
            sys.exit(1)
        new[page] = block(row, town, area)
    for page, (html_block, month) in new.items():
        text = open(page, encoding="utf-8").read()
        if START in text:
            updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: html_block, text, flags=re.S)
        else:
            # insert right after the Bright MLS source paragraph in the "at a Glance" block
            m = re.search(r'(<p [^>]*>Based on information from Bright MLS[^<]*</p>)', text)
            if not m:
                print(f"ERROR: no Bright MLS source line found in {page}")
                sys.exit(1)
            updated = text[:m.end()] + "\n        " + html_block + text[m.end():]
        if updated != text:
            open(page, "w", encoding="utf-8", newline="").write(updated)
            print(f"updated {page} -> {month}")
        else:
            print(f"unchanged {page} ({month})")


if __name__ == "__main__":
    main()
