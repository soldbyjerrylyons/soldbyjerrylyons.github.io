"""Review badge: "★★★★★ 5.0 average · N client reviews on Google and Zillow".

Counts every .testimonial in site-reviews.html inside <!-- REVIEWS-GOOGLE --> and <!-- REVIEWS-PAST-TEAM --> (the Zillow
block), reads each one's star rating from its aria-label ("5 out of 5 stars"), and writes the badge into
<!-- REVIEW-BADGE:START/END --> on site-index.html (copied to index.html) and site-reviews.html.
Shown only once there are at least MIN_REVIEWS reviews; below that the blocks stay empty. Run it after
update_home_review.py whenever reviews change. usage: python3 _tools/update_review_badge.py  (website repo root)
"""
import re, shutil, sys

MIN_REVIEWS = 5
rev = open("site-reviews.html", encoding="utf-8").read()
stars, sources = [], set()
for block, src in (("REVIEWS-GOOGLE", "Google"), ("REVIEWS-PAST-TEAM", "Zillow")):
    m = re.search(rf"<!-- {block}:START -->(.*?)<!-- {block}:END -->", rev, re.S)
    if not m:
        sys.exit(f"ERROR no {block} block")
    for t in re.split(r'<div class="testimonial', m.group(1))[1:]:
        r = re.search(r'aria-label="(\d(?:\.\d)?) out of 5 stars"', t)
        if not r:
            sys.exit(f"ERROR a {src} review has no star rating")
        stars.append(float(r.group(1))); sources.add(src)

n = len(stars)
if n >= MIN_REVIEWS:
    avg = sum(stars) / n
    where = " and ".join(s for s in ("Google", "Zillow") if s in sources)
    def badge(light):
        color = "#fff" if light else "var(--ink)"
        return (f'      <p class="review-badge" style="margin-top:12px;font-weight:600;color:{color};{"" if light else "text-align:center;margin:-8px auto 18px;"}">'
                f'<span class="stars" style="margin:0 6px 0 0;{"color:#fff;" if light else ""}" aria-hidden="true">{"&#9733;" * round(avg) + "&#9734;" * (5 - round(avg))}</span>'
                f'{avg:.1f} average &middot; {n} client reviews on {where}</p>\n      ')
    home, page = "\n" + badge(False), "\n" + badge(True)
else:
    home = page = "\n      "

def put(path, body):
    h = open(path, encoding="utf-8").read()
    pat = re.compile(r"(<!-- REVIEW-BADGE:START -->).*?(<!-- REVIEW-BADGE:END -->)", re.S)
    if not pat.search(h):
        sys.exit(f"ERROR no REVIEW-BADGE block in {path}")
    new = pat.sub(lambda m: m.group(1) + body + m.group(2), h, count=1)
    if new != h:
        open(path, "w", encoding="utf-8", newline="").write(new); return True
    return False

if put("site-index.html", home):
    shutil.copyfile("site-index.html", "index.html")
put("site-reviews.html", page)
print(f"ok: {n} reviews, badge {'shown' if n >= MIN_REVIEWS else f'hidden (needs {MIN_REVIEWS})'}")
