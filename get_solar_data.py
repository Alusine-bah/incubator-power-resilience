"""Download 10 years of hourly solar output for each site from PVGIS (European Commission JRC).

PVGIS returns the output of a 1 kWp crystalline-silicon array at the optimal tilt, after its
default 14 percent system loss, hour by hour, plus the outdoor air temperature.
Files are saved to data/pvgis_<site>.csv.gz. Run once; the sizing script then works offline.

Usage:
    python get_solar_data.py                      all sites in solar.py
    python get_solar_data.py mysite 8.0 -11.0     one extra site (name, latitude, longitude)
"""
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from solar import DATA_DIR, SITES, data_path

# Tried in order. PVGIS 5.3 covers 2005 to 2023; 5.2 covers 2005 to 2020. "" = PVGIS picks its
# default radiation database (satellite SARAH3 where it covers the site); PVGIS-ERA5 is a weather
# reanalysis, coarser but available everywhere.
# The last attempt fixes the panels at a 10 degree tilt facing the equator instead of asking PVGIS
# for the optimal angle, in case the optimisation fails close to the equator.
ATTEMPTS = (("v5_3", 2014, 2023, ""), ("v5_3", 2014, 2023, "PVGIS-ERA5"), ("v5_2", 2011, 2020, ""),
            ("v5_3", 2014, 2023, "fixed10"))


def build_url(version, lat, lon, start, end, database=""):
    q = {
        "lat": lat, "lon": lon, "pvcalculation": 1, "peakpower": 1, "loss": 14,
        "pvtechchoice": "crystSi", "mountingplace": "free", "optimalangles": 1,
        "startyear": start, "endyear": end, "outputformat": "json",
    }
    if database == "fixed10":
        q["optimalangles"] = 0
        q["angle"] = 10
        q["aspect"] = 180 if lat < 0 else 0      # PVGIS: 0 = facing south, 180 = facing north
    elif database:
        q["raddatabase"] = database
    return f"https://re.jrc.ec.europa.eu/api/{version}/seriescalc?" + urllib.parse.urlencode(q)


def to_rows(payload):
    """PVGIS JSON -> list of (YYYYMMDDHH, W per kWp, outdoor C). Time is UTC, e.g. '20140101:0010'."""
    rows = []
    for h in payload["outputs"]["hourly"]:
        t = h["time"]
        rows.append((t[:8] + t[9:11], float(h["P"]), float(h["T2m"])))
    return rows


def describe(payload):
    inp = payload.get("inputs", {})
    mount = inp.get("mounting_system", {}).get("fixed", {})
    tilt = mount.get("slope", {}).get("value", "?")
    azimuth = mount.get("azimuth", {}).get("value", "?")
    db = inp.get("meteo_data", {}).get("radiation_db", "?")
    return f"tilt {tilt} deg, azimuth {azimuth} deg, radiation database {db}"


def download(site, lat, lon):
    errors = []
    for version, start, end, database in ATTEMPTS:
        url = build_url(version, lat, lon, start, end, database)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=180) as r:
                    payload = json.load(r)
                rows = to_rows(payload)
                note = f"PVGIS {version} seriescalc, {start}-{end}, {describe(payload)}"
                return rows, note, url
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")[:300]
                errors.append(f"{version} {database or 'default'}: HTTP {e.code} {body.strip()}")
                break                      # a 4xx answer will not change on retry; try the next version
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                errors.append(f"{version} {database or 'default'}: {e}")
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{site}: download failed. " + " | ".join(errors))


def save(site, lat, lon, rows, note, url):
    os.makedirs(DATA_DIR, exist_ok=True)
    with gzip.open(data_path(site), "wt", encoding="ascii", newline="\n") as f:
        f.write(f"# site {site}, latitude {lat}, longitude {lon}\n")
        f.write(f"# source: {note}\n")
        f.write(f"# url: {url}\n")
        f.write("# columns: UTC time YYYYMMDDHH, solar output of a 1 kWp array (W), outdoor air temperature (C)\n")
        for stamp, p, t in rows:
            f.write(f"{stamp},{p:.1f},{t:.1f}\n")


def main():
    if len(sys.argv) == 4:
        sites = [(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))]
    else:
        sites = [(s[0], s[2], s[3]) for s in SITES]
    failed = []
    for site, lat, lon in sites:
        print(f"{site}: downloading (about 10 MB, can take a minute)...", flush=True)
        try:
            rows, note, url = download(site, lat, lon)
        except RuntimeError as e:
            print(f"   {e}")
            failed.append(site)
            continue
        save(site, lat, lon, rows, note, url)
        yearly = sum(p for _, p, _ in rows) / 1000.0 / (len(rows) / 8760.0)
        print(f"   saved {data_path(site)}: {len(rows)} hours, {note}; about {yearly:.0f} kWh per kWp per year")
    print()
    print("All sites downloaded." if not failed else "Failed: " + ", ".join(failed) + ". Paste this output here.")


if __name__ == "__main__":
    main()
