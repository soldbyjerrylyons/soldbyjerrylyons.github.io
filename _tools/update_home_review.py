"""Copy the newest review card from site-reviews.html onto the homepage.

Newest = the FIRST .testimonial card inside <!-- REVIEWS-GOOGLE:START/END --> (cards are kept newest first).
The whole card is copied as-is (stars, exact words, name, source/date, any disclosure line).
Writes site-index.html <!-- HOME-REVIEW:START/END --> and copies it to index.html.
usage: python3 _tools/update_home_review.py   (run from the website repo root)
"""
import re, shutil, sys

r = open("site-reviews.html", encoding="utf-8").read()
m = re.search(r"<!-- REVIEWS-GOOGLE:START -->(.*?)<!-- REVIEWS-GOOGLE:END -->", r, re.S)
if not m:
    sys.exit("ERROR no REVIEWS-GOOGLE block")
c = re.search(r'(<div class="testimonial"[^>]*>.*?</div>)\s*(?=<div class="testimonial"|$)', m.group(1).strip(), re.S)
if not c:
    sys.exit("ERROR no review card found")
card = c.group(1)
# a card is one outer div with inner divs/ps; make sure tags are balanced
if card.count("<div") != card.count("</div>"):
    sys.exit("ERROR card div mismatch")
card = re.sub(r'style="margin-top:16px;"', 'style="max-width:760px;margin:0 auto;"', card, count=1)

h = open("site-index.html", encoding="utf-8").read()
pat = re.compile(r"(<!-- HOME-REVIEW:START -->).*?(<!-- HOME-REVIEW:END -->)", re.S)
if not pat.search(h):
    sys.exit("ERROR no HOME-REVIEW block in site-index.html")
new = pat.sub(lambda x: x.group(1) + "\n      " + card + "\n      " + x.group(2), h, count=1)
if new != h:
    open("site-index.html", "w", encoding="utf-8", newline="").write(new)
    shutil.copyfile("site-index.html", "index.html")
    print("updated homepage review")
else:
    print("homepage review already current")
