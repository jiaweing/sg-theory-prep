#!/bin/sh
# Build the single-file app: draw the diagrams, apply fact-check fixes, assemble, then wrap as a standalone page.
set -e
cd "$(dirname "$0")"
sh src/viz/all.sh
python3 - <<'PY'
body = open('src/rtt-cheatsheet.html').read()
head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>')
open('index.html', 'w').write(head + body + '</body></html>')
print('index.html written')
PY
