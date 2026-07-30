#!/bin/sh
# GitHub Pages requires index.html at the repo root to serve the domain's "/",
# but every internal nav link across the site points to site-index.html instead.
# The two files must stay byte-identical. site-index.html is the source of
# truth (it follows the site-*.html naming convention every other page uses),
# so this always copies that direction, even if index.html was edited directly.
set -e
cd "$(dirname "$0")"
cp site-index.html index.html
