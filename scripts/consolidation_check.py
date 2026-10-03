"""How big is the gap between same-day and consolidated figures for TV news?
Matches every news broadcast in CIM's yearly Top 100 (Live+7, Live+28 incl. online from 1 Jul 2024) with the same
broadcast (same date and title) in the CIM daily Top 20, and writes the ratio daily / yearly.
Needs the local CIM cache (raw_yearly/yearly_top_100_YYYY.html, data/cim_daily_top20_news.csv; not in this repository).
Output: data/consolidation_check_news_daily_vs_yearly.csv"""
import os, re, html, pandas as pd
ROOT = os.path.join(os.path.dirname(__file__), ".."); D = os.path.join(ROOT, "data")
NEWS = re.compile(r"HET 7 UUR-JOURNAAL|HET 1 UUR-JOURNAAL|VRT NWS JOURNAAL|NIEUWS 19U VTM|NIEUWS 13U VTM")
def cells(h):
    for r in re.findall(r"<tr.*?</tr>", h, re.S):
        yield [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
def thousands(v):
    v = v.replace(".", "").replace(",", ".") if "," in v else v
    return int(round(float(v) * 1000))
news = pd.read_csv(os.path.join(D, "cim_daily_top20_news.csv"))
news["programme"] = news.programme.str.strip().str.upper()
out = []
for y in range(2018, 2026):
    p = os.path.join(ROOT, "raw_yearly", f"yearly_top_100_{y}.html")
    for c in cells(open(p, encoding="utf-8").read()):
        if len(c) != 6 or not c[0].isdigit() or not NEWS.fullmatch(c[1].strip().upper()): continue
        dd, mm, yy = c[4].split("/"); d = f"{yy}-{mm}-{dd}"
        m = news[(news.date == d) & (news.programme == c[1].strip().upper())]
        if m.empty: continue
        dv, yv = int(m.viewers.iloc[0]), thousands(c[5])
        basis = ("daily same-day vs yearly Live+7" if d < "2023-07-01" else
                 "daily consolidated Live+7 vs yearly Live+7" if d < "2024-07-01" else "both Live+28 incl. online")
        out.append(dict(date=d, programme=c[1].strip(), channel=c[3], daily_top20_viewers=dv, daily_start=m.start.iloc[0],
                        yearly_top100_viewers=yv, ratio_daily_to_yearly=round(dv / yv, 4), basis=basis,
                        source="CIM daily Top 20 and CIM yearly Top 100 (North, 4+ incl. guests)",
                        source_url="https://www.cim.be/nl/televisie", method="own calculation"))
pd.DataFrame(out).to_csv(os.path.join(D, "consolidation_check_news_daily_vs_yearly.csv"), index=False)
print(pd.DataFrame(out)[["date", "programme", "daily_top20_viewers", "yearly_top100_viewers", "ratio_daily_to_yearly", "basis"]].to_string())
