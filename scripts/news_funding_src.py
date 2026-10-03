"""Sourced figures for 'Reasons for the decline' and 'Public funding vs results' (news), plus one chart.

Every number is copied from the source next to it; gaps are 'not found'; own calculations are labelled.
Funding of VRT as a whole is analysed in the companion repository
https://github.com/STP-KAS/vrt-overall-ratings-10yr-report (not duplicated here).
Run: python scripts/news_funding_src.py
"""
import csv, os
import pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); D = os.path.join(ROOT, "data"); C = os.path.join(ROOT, "charts")
JV = {
    2016: "https://www.vrt.be/nl/assets/files/2024-09/VRTJaarverslag2016.pdf",
    2017: "https://www.vrt.be/nl/assets/files/2024-09/LRN-VRT-Jaarverslag-2017-web-low-2.pdf",
    2018: "https://www.vrt.be/nl/assets/files/2024-09/VRTJaarverslag2018WEB.pdf",
    2019: "https://www.vrt.be/nl/assets/files/2024-09/VRT_Jaarverslag-2019-CORPS-lowlowres.pdf",
    2020: "https://www.vrt.be/nl/assets/files/2024-09/VRT_jaarverslag2020_A4_030_pages_Compressed.pdf",
    2021: "https://www.vrt.be/nl/assets/files/2024-09/Jaarverslag2021.pdf",
    2022: "https://www.vrt.be/nl/assets/files/2024-09/VRTjaarbeeld2022.pdf",
    2023: "https://www.mediaspecs.be/wp-content/uploads/2024/06/vrt-jaarverslag-2023.pdf",
    2024: "https://www.vrt.be/nl/assets/files/2025-06/Jaarverslag-2024.pdf",
    2025: "https://www.vrt.be/nl/assets/files/2026-07/JVS_2025_0.pdf",
}
HICP_URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_aind"
            "?geo=BE&coicop=CP00&unit=INX_A_AVG&format=JSON")
BHO26 = "https://www.vrt.be/nl/assets/files/2025-10/BHO_VRT_2025_digitaal-14-10-2025.pdf"
DIGI = "https://www.imec.be/sites/default/files/2026-03/imec.digimeter-2025-rapport.pdf"
DNR = ("https://smit.research.vub.be/en/policy-brief-93-digital-news-report-2025-wider-access-"
       "weaker-pull-more-channels-less-interest-and-a")


def src(y):
    return ("VRT annual report 2023 (copy hosted by Mediaspecs; secondary)" if y == 2023
            else "VRT jaarbeeld 2022" if y == 2022 else f"VRT annual report {y}")


H = ["year", "section", "item", "value", "unit", "target", "met_as_reported", "source", "source_url",
     "location_in_source", "notes"]
R = []
# ---- costs
SC1 = ("'thema-aanbodsmerk' VRT NWS: digital/other news offer only; TV and radio news programmes were "
       "booked under the TV and radio brands - not comparable with 2021+")
for y, v, ry, loc, note in [
        (2016, 7.9, 2017, "p.191 (prior-year column)", SC1),
        (2017, 8.8, 2017, "p.191", SC1),
        (2018, 9.1, 2018, "p.161", SC1),
        (2019, 11.6, 2019, "p.169", SC1 + "; restated as 18.3 in the 2020 report (p.134)"),
        (2020, 17.6, 2020, "p.134", SC1)]:
    R.append([y, "cost", "VRT NWS cost, digital/other offer only (old scope)", v, "M EUR (nominal)", "", "",
              src(ry), JV[ry], loc + ", table 'kosten per thema-aanbodsmerk'", note])
SC2 = ("from 2021 VRT books all costs of the Information department under VRT NWS, incl. the radio and TV "
       "news programmes (2021 report p.85)")
for y, v, loc in [(2021, 68.9, "p.85"), (2022, "not found", ""), (2023, 82.1, "p.85"), (2024, 92.5, "p.84"),
                  (2025, 92.3, "p.80")]:
    R.append([y, "cost", "VRT NWS cost, all news (new scope)", v, "M EUR (nominal)", "", "",
              src(y) if v != "not found" else "", JV[y] if v != "not found" else "",
              (loc + ", table 'andere aanbodsmerken'") if loc else "",
              SC2 if v != "not found" else "the 2022 jaarbeeld has no cost tables"])
# ---- news KPIs
for y, v, loc in [(2016, 81.0, "p.210"), (2017, 77.5, "p.203"), (2018, 78.9, "p.169"), (2019, 79.7, "p.43"),
                  (2020, 82.6, "p.36"), (2021, 87.0, "KPI 19, p.36"), (2022, 82.4, "KPI 19"),
                  (2023, 82.0, "KPI 19, p.34"), (2024, 81.7, "KPI 19, p.30"), (2025, 83.2, "KPI 19, p.20")]:
    R.append([y, "kpi", "Weekly reach of the total VRT news offer", v, "% of Flemings", ">= 75%", "yes", src(y),
              JV[y], loc, "2016-2020: performance measure; 2021-2025: KPI 19; population 15+/16+ (12+ in 2021)"])
for y, v, loc in [(2020, 78.6, "p.36"), (2021, 80.8, "KPI 19, p.36"), (2022, 76.6, "KPI 19"),
                  (2023, 84.4, "KPI 19, p.34"), (2024, 79.8, "KPI 19, p.30"), (2025, 86.7, "KPI 19, p.20")]:
    R.append([y, "kpi", "Weekly reach of VRT news among 16-24", v, "%", ">= 65% (2021-2025)",
              "yes" if y >= 2021 else "n/a", src(y), JV[y], loc, ""])
for y, tv, rad, web, loc in [(2016, 76, 74, 71, "trust section"), (2017, "not found", "", "", "other question: 80% find VRT news reliable"),
                             (2018, "not found", "", "", ""), (2019, 73, 74, 70, "trust section"),
                             (2020, 75.4, 72.6, 71.4, "trust section"), (2021, 73, 68, 66, "KPI 20, p.36"),
                             (2022, 74, 71, 69, "KPI 20"), (2023, 75, 71, 71, "KPI 20, p.35"),
                             (2024, 75, 72, 73, "KPI 20, p.30"), (2025, 75, 71, 71, "KPI 20, p.20")]:
    R.append([y, "kpi", "Trust in VRT TV as a news source", tv, "% (much) trust", "no numeric target until 2026",
              "n/a", src(y) if tv != "not found" or y == 2017 else "", JV[y] if tv != "not found" or y == 2017 else "",
              loc if tv != "not found" else "",
              (f"radio {rad}%, website {web}%" if rad != "" else loc)])
R += [
    [2019, "kpi", "Investigative reports (Pano)", 17, "reports", ">= 10 (2016-2020)", "yes", src(2019), JV[2019],
     "appendix 'performantiemaatstaven' (p.175 ff.)", ""],
    [2019, "kpi", "Culture items in Het Journaal", 610, "items", ">= 365", "yes", src(2019), JV[2019],
     "appendix 'performantiemaatstaven'", ""],
    [2024, "kpi", "Culture items in Het Journaal (KPI 31)", 647, "items", ">= 365", "yes", src(2024), JV[2024], "KPI 31", ""],
    [2025, "kpi", "Culture items in Het Journaal (KPI 31)", 662, "items", ">= 365", "yes", src(2025), JV[2025], "KPI 31", ""],
    ["2021-2025", "kpi", "Investigative stories (KPI 23)", "see annual reports", "stories", ">= 15 per year", "", src(2025),
     JV[2025], "KPI 23", "yearly counts not copied here"],
    ["2021-2025", "kpi", "Impartiality (KPI 21)", "monitored, no numeric target", "", "", "n/a", src(2025), JV[2025],
     "KPI 21", "VRM study 'Onpartijdigheid van de VRT nieuwsberichtgeving' (2024) referred to; a numeric result: not found"],
    ["2016-2025", "kpi", "Target for Journaal viewers or market share", "not found", "", "", "n/a", "", "", "",
     "no such target in the KPI lists of the 2016-2020, 2021-2025 or 2026-2030 contracts"],
    ["2026-2030", "kpi", "KPI 11: trust in VRT NWS via TV, radio or online", "first result due by 1 June 2027", "",
     ">= 70%", "", "Beheersovereenkomst VRT 2026-2030", BHO26, "KPI 11", ""],
    ["2026-2030", "kpi", "KPI 14: weekly reach of VRT NWS", "first result due by 1 June 2027", "",
     ">= 75% of Flemings, >= 65% of each relevant group", "", "Beheersovereenkomst VRT 2026-2030", BHO26, "KPI 14", ""],
    ["2026-2030", "kpi", "KPI 13: investigative stories", "first result due by 1 June 2027", "",
     ">= 15 in 2026 rising to 20 in 2030", "", "Beheersovereenkomst VRT 2026-2030", BHO26, "KPI 13", ""],
    ["2026-2030", "kpi", "KPI 16: reach of analysis ('duiding') offer", "first result due by 1 June 2027", "",
     ">= 45% of media users, 50% by 2030", "", "Beheersovereenkomst VRT 2026-2030", BHO26, "KPI 16", ""],
    ["2026-2030", "kpi", "KPI 18: culture items in Het Journaal", "first result due by 1 June 2027", "",
     ">= 365 per year", "", "Beheersovereenkomst VRT 2026-2030", BHO26, "KPI 18", ""],
]
# ---- drivers (news)
for item, y0, v0, y1, v1, unit, s, url, loc, note in [
    ("Watch TV evening news (as news source)", 2017, 73, 2026, 51, "%", "SMIT/VUB, Digital News Report Flanders, policy brief 93", DNR, "brief text", "young people: from about 60% to about 1 in 3"),
    ("Use news daily", 2017, 89, 2026, 72, "%", "SMIT/VUB policy brief 93", DNR, "brief text", ""),
    ("Sometimes or often avoid the news", 2017, 48, 2026, 66, "%", "SMIT/VUB policy brief 93", DNR, "brief text", ""),
    ("Very or extremely interested in news", 2017, 62, 2026, 36, "%", "SMIT/VUB policy brief 93", DNR, "brief text", "59% in 2021; not interested 4% -> 18%"),
    ("Social media as main news source, age 18-24", 2017, 23, 2026, 43, "%", "SMIT/VUB policy brief 93", DNR, "brief text", "all ages 16%; under 35: 37%"),
    ("Trust most news most of the time", 2017, 57, 2026, "just under 50", "%", "SMIT/VUB policy brief 93", DNR, "brief text", "61% in 2020"),
    ("Go directly to news sites/apps", 2017, 32, 2026, 44, "%", "SMIT/VUB policy brief 93", DNR, "brief text", ""),
    ("Use VRT NWS online weekly", "", 33, 2026, 40, "%", "SMIT/VUB policy brief 93", DNR, "brief text", "earlier year as stated in the brief"),
    ("Print newspaper as news source", 2017, 47, 2026, 21, "%", "SMIT/VUB policy brief 93", DNR, "brief text", ""),
    ("National TV news daily", 2024, 53, 2025, 51, "%", "imec.digimeter 2025", DIGI, "p.39", "radio news daily 55%"),
    ("News via social media daily", "", "", 2025, 44, "%", "imec.digimeter 2025", DIGI, "p.39", "18-24: 65%, 25-34: 56% (weekly 57% all ages)"),
    ("News via search engines daily", 2024, 22, 2025, 33, "%", "imec.digimeter 2025", DIGI, "p.39", ""),
    ("Watch live TV daily", 2020, 56, 2025, 40, "%", "imec.digimeter 2025", DIGI, "p.23", "25-34: 14%; 65-74: 65%"),
]:
    R.append([f"{y0}->{y1}", "driver", item, f"{v0} -> {v1}", unit, "", "", s, url, loc, note])
with open(os.path.join(D, "news_funding_kpis_drivers.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(H); w.writerows(R)

# ---- own calculation: news cost in 2025 prices and per inhabitant
hicp = {2021: 111.71, 2023: 126.07, 2024: 131.52, 2025: 135.49}
pop = {2021: (6.65, 2021, "p.85"), 2023: (6.77, 2023, "p.85"), 2024: (6.82, 2024, "p.84"), 2025: (6.86, 2025, "p.80")}  # inhabitants of Flanders (M), 1 Jan
cost = {2021: 68.9, 2023: 82.1, 2024: 92.5, 2025: 92.3}
O = []
for y in (2021, 2022, 2023, 2024, 2025):
    c = cost.get(y)
    O.append([y, c if c else "not found", hicp.get(y, 123.26 if y == 2022 else ""),
              round(c * hicp[2025] / hicp[y], 1) if c else "not found",
              pop[y][0] if y in pop else "not found",
              round(c / pop[y][0], 2) if c and y in pop else "not found",
              "own calculation: 2025 prices = nominal x HICP(2025)/HICP(year), Eurostat HICP Belgium (" + HICP_URL +
              "); per inhabitant = cost / inhabitants of Flanders on 1 Jan as stated in the VRT report of that year",
              "new cost scope from 2021 only (all news incl. TV and radio)"])
with open(os.path.join(D, "news_cost_real_owncalc.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "vrt_nws_cost_meur_nominal", "hicp_2015_100", "vrt_nws_cost_meur_2025_prices",
                "inhabitants_flanders_m", "vrt_nws_cost_per_inhabitant_eur_nominal", "method", "caveats"])
    w.writerows(O)

# ---- chart
def covid(a, x0=2019.5, x1=2021.5, ytext=0.985):
    a.axvspan(x0, x1, color="grey", alpha=.08, zorder=0)
    a.text((x0 + x1) / 2, ytext, "COVID-19 years", transform=mtrans.blended_transform_factory(a.transData, a.transAxes),
           ha="center", va="top", fontsize=7.5, color="grey")

df = pd.DataFrame(R, columns=H)
def ser(item):
    s = df[df.item == item].copy(); s = s[s.year.astype(str).str.fullmatch(r"\d{4}")]
    return s.year.astype(int).tolist(), pd.to_numeric(s.value, errors="coerce").tolist()

def plot(a, x, y, col, lab, ls="-", dy=6, fmt="{:.1f}", dx=0):
    seg = []; first = True
    for xi, yi in list(zip(x, y)) + [(None, float("nan"))]:
        if xi is None or pd.isna(yi):
            if seg:
                a.plot([p[0] for p in seg], [p[1] for p in seg], ls=ls, marker="o", color=col, lw=2.2, ms=5,
                       label=lab if first else None); first = False
            seg = []
        else:
            seg.append((xi, yi))
    for xi, yi in zip(x, y):
        if not pd.isna(yi):
            d = dy.get(xi, 6) if isinstance(dy, dict) else dy
            a.annotate(fmt.format(yi), (xi, yi), textcoords="offset points", xytext=(dx, d), ha="left" if dx else "center",
                       va="center" if dx else "baseline", fontsize=7.5, color=col)

fig, ax = plt.subplots(1, 2, figsize=(13, 5.3))
a = ax[0]; covid(a)
x, y = ser("VRT NWS cost, all news (new scope)")
plot(a, x, y, "#c8102e", "All news, nominal (VRT; new scope from 2021)", dy=-13)
plot(a, [o[0] for o in O], [pd.to_numeric(o[3], errors="coerce") for o in O], "#555555", "All news, in 2025 prices (own calculation)", ls="--", dy=7)
x, y = ser("VRT NWS cost, digital/other offer only (old scope)")
plot(a, x, y, "#1f4e9c", "Digital/other news offer only (old scope, not comparable)", ls=":", dy=7)
a.axvline(2020.5, color="k", ls="-.", lw=.9)
a.text(2020.55, 0.30, "cost scope\nchanges (2021)", transform=mtrans.blended_transform_factory(a.transData, a.transAxes), fontsize=7)
a.set_xticks(range(2016, 2026)); a.set_ylim(0, 110); a.set_ylabel("million EUR")
a.set_title("VRT NWS cost as reported by VRT, 2016–2025\n(2022 not found)", fontsize=10)
a.legend(loc="upper left", fontsize=7.5, frameon=False, bbox_to_anchor=(0, 0.93)); a.grid(axis="y", alpha=.3)

a = ax[1]; covid(a)
x, y = ser("Weekly reach of the total VRT news offer"); plot(a, x, y, "#1f4e9c", "Weekly reach of VRT news offer (target ≥ 75%)", dy={2023: -13, 2025: -13})
x, y = ser("Weekly reach of VRT news among 16-24"); plot(a, x, y, "#e76f51", "… among 16–24 (target ≥ 65% from 2021)", dy=0, dx=7)
x, y = ser("Trust in VRT TV as a news source"); plot(a, x, y, "#2a9d8f", "Trust in VRT TV as news source (no target until 2026)", dy=-13, fmt="{:.0f}")
a.axhline(75, color="#1f4e9c", ls=":", lw=1); a.axhline(65, color="#e76f51", ls=":", lw=1)
a.set_xticks(range(2016, 2026)); a.set_xlim(2015.6, 2025.7); a.set_ylim(50, 95); a.set_ylabel("%")
a.set_title("VRT news targets and results (as reported by VRT), 2016–2025", fontsize=10)
a.legend(loc="lower left", fontsize=7.5, frameon=False); a.grid(axis="y", alpha=.3)
fig.text(0.01, 0.01, "Sources: VRT annual reports 2016–2025 (cost tables per brand; performance measures / KPIs 19–20); Eurostat HICP Belgium. "
         "See data/news_funding_kpis_drivers.csv and data/news_cost_real_owncalc.csv.", fontsize=7, color="#555555")
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(C, "news_funding_vs_results.png"), dpi=150); plt.close(fig)
print("rows", len(R)); print(pd.DataFrame(O).iloc[:, :6].to_string())
