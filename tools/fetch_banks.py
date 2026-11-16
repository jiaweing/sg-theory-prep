"""Re-download the official Traffic Police practice questions from form.gov.sg and rebuild the question banks.

    python3 tools/fetch_banks.py          # writes src/form/data.json (RTT), src/btt/bank.json, src/ftt/bank.json

Each official practice page is a form.gov.sg form whose sections link to one form per question set. In each set,
every multiple-choice field is followed by a statement field reading "Answer: B) ...". Exact duplicates are dropped.
"""
import json, os, re, sys, urllib.request

API = "https://form.gov.sg/api/v3/forms/"
MAIN = {"rtt": "67d2fcd008bae384d0ace35d", "btt": "67317e882e2ffcb14032e4a2", "ftt": "67d2ad567b868a77419c163b"}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")


def get(form_id):
    req = urllib.request.Request(API + form_id, headers={"User-Agent": "sg-theory-prep (question bank refresh)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["form"]


def clean(s):
    s = re.sub(r"^\s*\(?[A-D]\s*[\)\.]\s*", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.replace("reaction reactions", "reactions")


def rtt_cat(name):
    for k, v in [("Alcohol", "Alcohol"), ("Traffic Rules", "Traffic rules"), ("General", "General"),
                 ("Road Safety", "Road safety"), ("Competency", "Competency"), ("Lane", "Lanes & overtaking")]:
        if name.startswith(k):
            return v
    return name


def fetch(test):
    main = get(MAIN[test])
    sets, out, seen = [], [], set()
    for sec in main["form_fields"]:
        title, sid = sec["title"], sec["description"].strip().rsplit("/", 1)[1]
        fields = get(sid)["form_fields"]
        for i, f in enumerate(fields):
            if f["fieldType"] != "radiobutton":
                continue
            ans = next((g["description"] for g in fields[i + 1:i + 3]
                        if g["fieldType"] == "statement" and "nswer" in (g.get("description") or "")), "")
            m = re.search(r"nswer\s*:?\s*\(?([A-D])\s*[\)\.]", ans)
            idx = next((k for k, o in enumerate(f["fieldOptions"]) if m and re.match(r"\s*\(?" + m.group(1) + r"\s*[\)\.]", o)), None)
            if idx is None:
                at = clean(re.sub(r"^\s*Answer\s*:?\s*", "", ans)).lower().rstrip(".")
                idx = next((k for k, o in enumerate(f["fieldOptions"]) if clean(o).lower().rstrip(".") == at), None)
            if idx is None:
                print("  skipped (no answer found):", f["title"][:70], file=sys.stderr)
                continue
            q, opts = re.sub(r"\s+", " ", f["title"]).strip(), [clean(o) for o in f["fieldOptions"]]
            if (q, tuple(opts)) in seen:
                continue
            seen.add((q, tuple(opts)))
            if title not in sets:
                sets.append(title)
            out.append([q, opts, idx, sets.index(title)])
    return sets, out


if __name__ == "__main__":
    for test in ("rtt", "btt", "ftt"):
        sets, q = fetch(test)
        if test == "rtt":
            path, data = os.path.join(ROOT, "form", "data.json"), {"sets": sets, "cats": [rtt_cat(s) for s in sets], "q": q}
        else:
            path, data = os.path.join(ROOT, test, "bank.json"), {"sets": sets, "q": q}
        with open(path, "w") as fh:
            fh.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")) if test == "rtt" else json.dumps(data, ensure_ascii=False))
        print(f"{test}: {len(q)} questions in {len(sets)} sets -> {os.path.relpath(path)}")
