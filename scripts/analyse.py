"""Build annual/monthly aggregates and charts from data/cim_daily_top20_news.csv.
Daily figures = CIM daily Top 20, North (Flanders + Dutch-speaking Brussels), 4+ incl. guests,
Live+VOSDAL (+ online viewing from 2020 onwards, see README methodology)."""
import os, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates
ROOT = os.path.join(os.path.dirname(__file__), ".."); D = os.path.join(ROOT, "data"); C = os.path.join(ROOT, "charts")
os.makedirs(C, exist_ok=True)
CIM = "https://www.cim.be/nl/televisie"
raw = pd.read_csv(os.path.join(D, "cim_daily_top20_news.csv"))
alldays = pd.read_csv(os.path.join(D, "cim_days_available.csv"))  # date, n_rows (days for which CIM returned a Top 20)
alldays["date"] = pd.to_datetime(alldays.date)
raw["date"] = pd.to_datetime(raw.date)
raw["mins"] = raw.start.str.slice(0, 2).astype(int) * 60 + raw.start.str.slice(3, 5).astype(int)
def pick(prog_re, lo, hi, chan_re):
    m = raw.programme.str.fullmatch(prog_re) & raw.channel.str.fullmatch(chan_re) & raw.mins.between(lo, hi)
    s = raw[m].sort_values(["date", "mins"]).groupby("date").first()   # regular broadcast closest to slot
    return s
series = {
    "VRT 19:00 Journaal": pick(r"HET 7 UUR-JOURNAAL|VRT NWS JOURNAAL", 18*60+45, 19*60+30, r"EEN|VRT 1"),
    "VRT 13:00 Journaal": pick(r"HET 1 UUR-JOURNAAL|VRT NWS JOURNAAL", 12*60+45, 13*60+30, r"EEN|VRT 1"),
    "VTM NIEUWS 19:00 (context)": pick(r"NIEUWS 19U VTM|NIEUWS VTM", 18*60+45, 19*60+30, r"VTM"),
    "VTM NIEUWS 13:00 (context)": pick(r"NIEUWS 13U VTM", 12*60+45, 13*60+30, r"VTM"),
}
daily = []
for k, s in series.items():
    t = s[["viewers", "rank", "start", "duration"]].copy(); t["broadcast"] = k; daily.append(t.reset_index())
daily = pd.concat(daily); daily.to_csv(os.path.join(D, "daily_journaal_viewers.csv"), index=False)

def yr_stats(s, days, label):
    out = []
    for y, g in days.groupby(days.date.dt.year):
        dd = g.date; n_days = len(dd)
        v = s.reindex(dd)["viewers"]
        wk = v[dd.dt.weekday.values < 5]
        found = v.notna().sum()
        mx = v.idxmax() if found else None
        out.append(dict(year=y, broadcast=label, cim_days_available=n_days, days_in_top20=int(found),
                        coverage_pct=round(100*found/n_days, 1),
                        mean_viewers_days_in_top20=round(v.mean()) if found else None,
                        median_viewers_days_in_top20=round(v.median()) if found else None,
                        weekday_mean=round(wk.mean()) if wk.notna().any() else None,
                        weekday_coverage_pct=round(100*wk.notna().sum()/max(len(wk),1), 1),
                        max_viewers=int(v.max()) if found else None, max_date=mx.date().isoformat() if found else None,
                        period=f"{dd.min().date()}..{dd.max().date()}"))
    return out
rows = []
for k, s in series.items(): rows += yr_stats(s, alldays, k)
ann = pd.DataFrame(rows); ann["source_url"] = CIM
ann["metric"] = "CIM daily Top 20 viewers (4+, North, Live+VOSDAL+Guests; +Online from 2020)"
ann.to_csv(os.path.join(D, "annual_from_cim_daily_top20.csv"), index=False)
# Same-period comparison Jan 1 - Sep 30 (to compare 2026 YTD fairly)
ytd = []
for k, s in series.items():
    for y, g in alldays[(alldays.date.dt.month <= 9)].groupby(alldays.date.dt.year):
        v = s.reindex(g.date)["viewers"]
        ytd.append(dict(year=y, broadcast=k, jan_sep_mean=round(v.mean()) if v.notna().any() else None,
                        jan_sep_weekday_mean=round(v[g.date.dt.weekday.values < 5].mean()) if v.notna().any() else None,
                        coverage_pct=round(100*v.notna().sum()/len(g), 1)))
pd.DataFrame(ytd).to_csv(os.path.join(D, "jan_sep_comparison.csv"), index=False)
# monthly
mon = []
for k, s in series.items():
    m = s["viewers"].resample("MS").agg(["mean", "count"]).reset_index(); m["broadcast"] = k; mon.append(m)
mon = pd.concat(mon); mon.to_csv(os.path.join(D, "monthly_from_cim_daily_top20.csv"), index=False)

# ---------- Chart 1: annual averages ----------
full = ann[(ann.year >= 2017)]
YCOL = "mean_viewers_days_in_top20"
fig, ax = plt.subplots(figsize=(11, 6.2))
sty = {"VRT 19:00 Journaal": ("#c8102e", "-", "o"), "VRT 13:00 Journaal": ("#1f4e9c", "-", "s"),
       "VTM NIEUWS 19:00 (context)": ("#c8102e", ":", None), "VTM NIEUWS 13:00 (context)": ("#1f4e9c", ":", None)}
for k, (col, ls, mk) in sty.items():
    g = full[full.broadcast == k]
    ax.plot(g.year, g[YCOL] / 1000, color=col, ls=ls, marker=mk, lw=2.4 if mk else 1.4,
            alpha=1 if mk else .6, label=k)
    if mk:
        for x, yv in zip(g.year, g[YCOL]):
            ax.annotate(f"{yv/1000:.0f}k", (x, yv/1000), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8, color=col)
ax.axvspan(2019.5, 2021.5, color="grey", alpha=.08); ax.text(2020.5, ax.get_ylim()[1]*0.97, "COVID-19 years", ha="center", fontsize=8, color="grey")
ax.axvline(2019.5, color="k", ls="--", lw=.8); ax.text(2019.55, 120, "CIM adds online\nviewing (2020→)", fontsize=7.5)
ax.set_xticks(range(2017, 2027)); ax.set_xticklabels([str(y) if y < 2026 else "2026\n(Jan–Oct 2)" for y in range(2017, 2027)])
ax.set_ylabel("average viewers per broadcast (thousands)"); ax.set_ylim(0, None)
ax.set_title("VRT NWS Journaal (Eén / VRT 1): average viewers per broadcast, 2017–2026 (all days)\n"
             "Source: CIM daily Top 20, Flanders + Dutch-speaking Brussels, 4+, Live+VOSDAL(+online from 2020)", fontsize=10.5)
ax.legend(fontsize=8.5, loc="lower left"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(C, "annual_journaal_13u_19u.png"), dpi=150); plt.close(fig)

# ---------- Chart 2: monthly trend ----------
fig, ax = plt.subplots(figsize=(12, 6.6))
for k, col in [("VRT 19:00 Journaal", "#c8102e"), ("VRT 13:00 Journaal", "#1f4e9c")]:
    g = mon[mon.broadcast == k]
    ax.plot(g["date"], g["mean"] / 1000, color=col, lw=1, alpha=.45, label=k + " (monthly avg)")
    roll = g.set_index("date")["mean"].rolling(12, center=True, min_periods=10).mean()
    ax.plot(roll.index, roll / 1000, color=col, lw=2.8, label=k + " (12-month rolling avg)")
for k, col in [("VTM NIEUWS 19:00 (context)", "#c8102e")]:
    g = mon[mon.broadcast == k]
    ax.plot(g["date"], g["mean"] / 1000, color=col, lw=1, ls=":", alpha=.7, label="VTM NIEUWS 19:00 (context)")
top = mon["mean"].max() / 1000 * 1.12
ev = [("2020-03-15", "COVID-19 lockdown"), ("2020-11-30", "Martine Tanghe\nfarewell"), ("2022-02-24", "Russia invades\nUkraine"),
      ("2023-05-01", "Eén → VRT 1"), ("2024-06-09", "Elections\n9 June 2024")]
for d, t in ev:
    x = pd.Timestamp(d); ax.axvline(x, color="grey", lw=.7, ls="--"); ax.text(x, top * 0.99, t, fontsize=7.2, rotation=90, va="top", ha="right", color="dimgrey")
for d, t in [("2020-01-01", "online added"), ("2021-06-11", "online live streams added")]:
    x = pd.Timestamp(d); ax.axvline(x, color="k", lw=.9, ls="-.")
    ax.text(x, 60, t, fontsize=7, rotation=90, va="bottom", ha="left")
ax.set_ylim(0, top); ax.set_ylabel("viewers (thousands)")
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_title("VRT NWS Journaal 13:00 and 19:00 – monthly average viewers, Oct 2016 – Sep 2026\n"
             "Source: CIM daily Top 20 (North, 4+, Live+VOSDAL; online viewing incl. from 2020)\nThin = monthly average · thick = 12-month rolling average · dash-dot = CIM method changes", fontsize=10)
ax.legend(fontsize=8.5, loc="lower left"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(C, "monthly_journaal_13u_19u.png"), dpi=150); plt.close(fig)
print(ann[ann.broadcast.str.startswith("VRT")].to_string())

# ---------- Long-format master CSV: one figure per row, each with its source ----------
JV = {2016: "https://www.vrt.be/nl/assets/files/2024-09/VRTJaarverslag2016.pdf",
      2017: "https://www.vrt.be/nl/assets/files/2024-09/LRN-VRT-Jaarverslag-2017-web-low-2.pdf",
      2018: "https://www.vrt.be/nl/assets/files/2024-09/VRTJaarverslag2018WEB.pdf",
      2019: "https://www.vrt.be/nl/assets/files/2024-09/VRT_Jaarverslag-2019-CORPS-lowlowres.pdf",
      2020: "https://www.vrt.be/nl/assets/files/2024-09/VRT_jaarverslag2020_A4_030_pages_Compressed.pdf"}
CIMY = "https://www.cim.be/nl/televisie (Jaar > Marktaandelen / Top 100, regio Noord)"
M = []
def add(year, broadcast, metric, value, unit, src_name, src_url, note=""):
    M.append(dict(year=year, broadcast=broadcast, metric=metric, value=value, unit=unit, source=src_name, source_url=src_url, notes=note))
for _, r in ann.iterrows():
    part = "partial year: " + r.period if r.year in (2016, 2026) else ""
    meth = "Live+VOSDAL+Guests, TV only" if r.year < 2020 else "Live+VOSDAL+Guests + same-day online (online live streams counted from 11 Jun 2021)"
    note = "; ".join(x for x in [part, meth, f"coverage {r.coverage_pct}% of {r.cim_days_available} CIM days"] if x)
    add(r.year, r.broadcast, "avg viewers per broadcast (all days)", r.mean_viewers_days_in_top20, "viewers", "CIM daily Top 20 (computed)", CIM, note)
    add(r.year, r.broadcast, "avg viewers per broadcast (Mon-Fri)", r.weekday_mean, "viewers", "CIM daily Top 20 (computed)", CIM, note)
    add(r.year, r.broadcast, "median viewers per broadcast", r.median_viewers_days_in_top20, "viewers", "CIM daily Top 20 (computed)", CIM, note)
    add(r.year, r.broadcast, "best day of year", r.max_viewers, "viewers", "CIM daily Top 20", CIM, f"date {r.max_date}; {meth}")
# Published figures (copied verbatim from the cited documents)
reach = {2016: (1919559, 32.0, 63.7), 2017: (1841411, 30.7, 61.1), 2018: (1784923, 29.4, 59.7), 2019: (1749894, 28.9, 58.3), 2020: (1987954, 32.9, 60.3)}
for y, (n, pct, wk) in reach.items():
    src = JV[y] if y != 2017 else JV[2018]
    add(y, "All VRT TV journaal broadcasts", "avg daily reach", n, "people", f"VRT jaarverslag {y if y != 2017 else 2018}", src, f"{pct}% of Flemings 4+")
    add(y, "All VRT TV journaal broadcasts", "weekly reach", wk, "% of Flemings", f"VRT jaarverslag {y if y != 2017 else 2018}", src, "")
for y in range(2021, 2026):
    add(y, "All VRT TV journaal broadcasts", "avg daily reach", "not found", "", "VRT jaarverslag (no longer reported)", "", "VRT annual reports 2021-2025 no longer publish this figure")
ms = {2016: 32.6, 2017: 30.1}
for y, v in ms.items(): add(y, "Eén (channel)", "TV market share, 4+, full day", v, "%", "VRT jaarverslag 2017 (source CIM/GfK)", JV[2017], "")
for y, v in {2018: 30.36, 2019: 29.62, 2020: 30.92, 2021: 32.49, 2022: 32.01, 2023: 31.66, 2024: 32.17, 2025: 30.27}.items():
    add(y, "Eén / VRT 1 (channel)", "TV market share, 4+, 02-26h", v, "%", "CIM yearly market shares", CIMY, "")
best = {2018: ("2018-06-18", 1337.9), 2019: ("2019-01-21", 1134.7), 2020: ("2020-11-30", 2030.6), 2021: ("2021-01-20", 1367.7),
        2022: ("2022-02-24", 1229.3), 2023: ("2023-03-20", 1199.3), 2024: ("2024-07-01", 1178.3), 2025: ("2025-01-27", 1084.0)}
for y, (dte, v) in best.items():
    add(y, "VRT 19:00 Journaal", "best-watched broadcast in CIM yearly Top 100 (thousands)", v, "thousand viewers", "CIM yearly Top 100", CIMY, f"date {dte}; yearly-top metric (Live+7, incl. online where applicable)")
web = {2016: (270140, "deredactie.be site; app +63,437/day"), 2017: (401971, "vrtnws.be site + app"), 2018: (446928, "site; app +150,496/day"),
       2019: (550714, "site + app"), 2020: (960009, "site + app (unique browsers)")}
for y, (v, n) in web.items():
    add(y, "VRT NWS online", "avg daily unique visitors", v, "visitors/browsers", f"VRT jaarverslag {y}" if y != 2017 else "VRM toezichtsrapport VRT 2017",
        JV[y] if y != 2017 else "https://www.vlaamseregulatormedia.be/sites/default/files/2025-01/vrt2017.pdf", n)
add(2020, "VRT 19:00 Journaal", "record broadcast 27 Mar 2020 (COVID)", 1748370, "viewers", "VRT jaarverslag 2020", JV[2020], "")
add(2020, "VRT 19:00 Journaal", "Martine Tanghe's last Journaal 30 Nov 2020", 2001867, "viewers", "VRT NWS", "https://www.vrt.be/vrtnws/nl/2020/11/30/martine-tanghe-op-bezoek-bij-koning-filip-ik-ben-blij-en-trots/", "best-watched Journaal ever")
add(2016, "VRT 19:00 Journaal", "22 Mar 2016 (Brussels attacks)", 1383976, "viewers", "Showbizzsite (CIM day top 10)", "https://www.showbizzsite.be/nieuws/kijkcijfers-dinsdag-22-maart-2016-1499876", "")
add(2016, "VRT 13:00 Journaal", "22 Mar 2016 (Brussels attacks)", 682099, "viewers", "Showbizzsite (CIM day top 10)", "https://www.showbizzsite.be/nieuws/kijkcijfers-dinsdag-22-maart-2016-1499876", "")
pd.DataFrame(M).to_csv(os.path.join(D, "vrt_journaal_10yr_data.csv"), index=False)
print("master rows", len(M))
