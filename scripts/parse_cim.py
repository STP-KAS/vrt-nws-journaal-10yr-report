"""Parse cached CIM daily Top-20 HTML (raw/*.html) into data/cim_daily_top20_journaal.csv
(one row per Journaal/news broadcast found in the Flemish (North) daily Top 20)."""
import re, glob, os, csv
ROOT = os.path.join(os.path.dirname(__file__), "..")
def fix(c):
    # Some 2016-2017 CIM rows come back as one malformed string in the title cell, e.g.
    # 'TITLE;" ";"EEN";"20:12:30";"20:37:56";"00:25:27";1.212.156;'  or
    # 'TITLE" "VIER"21:33:26"22:50:58"01:00:301.162.364,'
    if not c[6]:
        m = re.match(r'^(.*?)[;"]+\s*[;"]*"?([A-Za-z0-9 .]+?)"?[;"]*(\d\d:\d\d:\d\d)[;"]*(\d\d:\d\d:\d\d)[;"]*(\d\d:\d\d:\d\d)[;"]*([\d.]+)', c[1])
        if m:
            title, ch, start, end, dur, viewers = m.groups()
            return [c[0], title.strip(), ch.strip(), c[3], start, dur, viewers.strip(".")]
        return None
    return c
def to_int(v):
    # '1.212.156' -> 1212156 ; some autumn-2024 rows carry decimals: '971.420,70' -> 971421
    v = v.strip()
    if "," in v:
        whole, dec = v.split(",", 1); return int(round(float(whole.replace(".", "") + "." + dec)))
    return int(v.replace(".", ""))
rows = []
days = 0; empty = []; avail = []
for f in sorted(glob.glob(os.path.join(ROOT, "raw", "*.html"))):
    d = os.path.basename(f)[:-5]
    h = open(f, encoding="utf-8").read()
    trs = re.findall(r"<tr>(.*?)</tr>", h, re.S)
    cells = [[re.sub("<[^>]+>", "", x).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)] for r in trs]
    cells = [fix(c) for c in cells if len(c) == 7]
    bad = sum(1 for c in cells if c is None); cells = [c for c in cells if c]
    if bad: print('unparsed rows', d, bad)
    if not cells: empty.append(d); continue
    days += 1; avail.append((d, len(cells)))
    for rank, prog, ch, date, start, dur, viewers in cells:
        if re.search(r"JOURNAAL|NIEUWS", prog, re.I):
            rows.append(dict(date=d, rank=int(rank), programme=prog, channel=ch, start=start, duration=dur,
                             viewers=to_int(viewers), n_rows_in_top=len(cells)))
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
with open(os.path.join(ROOT, "data", "cim_daily_top20_news.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(ROOT, "data", "cim_days_available.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["date", "n_rows"]); w.writerows(avail)
print("days with data", days, "empty", len(empty), empty[:5], empty[-5:])
