"""Fetch CIM (cim.be) daily TV Top-20 (North = Flanders + Dutch-speaking Brussels)
for a date range and cache the raw HTML responses. Source: https://www.cim.be/nl/televisie
The page loads its tables from POST /nl/tv-media-response (val=daily, date=YYYY-MM-DD, region=north)."""
import sys, os, time, datetime as dt, requests
from concurrent.futures import ThreadPoolExecutor
URL = "https://www.cim.be/nl/tv-media-response"
RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (research; vrt-nws-journaal-10yr-report)"
def fetch(d):
    p = os.path.join(RAW, f"{d}.html")
    if os.path.exists(p) and os.path.getsize(p) > 2000: return d, "cached"
    for a in range(4):
        try:
            r = S.post(URL, data=dict(val="daily", date=d, region="north", pgid=1, year=d[:4], period="yearly_top_100", week=""), timeout=60)
            if r.status_code == 200 and len(r.text) > 500:
                open(p, "w").write(r.text); return d, "ok"
        except Exception as e:
            pass
        time.sleep(3 * (a + 1))
    return d, "fail"
if __name__ == "__main__":
    s = dt.date.fromisoformat(sys.argv[1]); e = dt.date.fromisoformat(sys.argv[2]); w = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    days = [(s + dt.timedelta(i)).isoformat() for i in range((e - s).days + 1)]
    n = 0
    with ThreadPoolExecutor(w) as ex:
        for d, st in ex.map(fetch, days):
            n += 1
            if st == "fail" or n % 100 == 0: print(n, d, st, flush=True)
    print("done", n)
