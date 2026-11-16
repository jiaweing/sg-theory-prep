#!/bin/sh
# rebuild everything: css -> fragments -> page
cd "$(dirname "$0")/.." && python3 -I viz/gen_sheets.py && python3 -I viz/factfix.py && python3 -I build.py
