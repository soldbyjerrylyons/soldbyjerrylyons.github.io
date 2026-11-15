"""Set every 'Latest available as of <date>' stamp on the site to today (America/New_York).
Jerry 2026-11-15: visitors must see today's date on the numbers, even when the
latest published figures haven't changed. The data period (e.g. Jul-Sep 2026) stays
as it is - only the 'as of' date moves. Run from the repo root:
    python3 _tools/update_asof.py            (stamps existing markers)
    python3 _tools/update_asof.py --add      (also adds a stamp to any Bright source line missing one)
"""
import glob, re, sys, datetime
try:
    from zoneinfo import ZoneInfo
    today = datetime.datetime.now(ZoneInfo("America/New_York")).date()
except Exception:
    today = datetime.date.today()
label = f"{today:%B} {today.year}"
STAMP = '<strong class="as-of">Latest available as of {}.</strong> '
pat = re.compile(r'<strong class="as-of">Latest available as of [^.<]*\.</strong> ')
changed = []
for f in sorted(glob.glob("site-*.html")):
    t = open(f, encoding="utf-8").read()
    n = pat.sub(STAMP.format(label), t)
    if "--add" in sys.argv:
        n = re.sub(r'(<p[^>]*>)(?!<strong class="as-of">)(Based on information from Bright MLS for )',
                   lambda m: m.group(1) + STAMP.format(label) + m.group(2), n)
    if n != t:
        open(f, "w", encoding="utf-8", newline="").write(n)
        changed.append(f)
print("as of", label, "->", ", ".join(changed) if changed else "no changes")
