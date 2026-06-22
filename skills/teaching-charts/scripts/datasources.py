"""
datasources.py — tidy data adapters for teaching-charts (empirical figures)

One fetch function per public source; each returns a tidy DataFrame with columns
    date | value | series_id | label | source
and a provenance string ready for the chart's "· In the data …" source line.

Design principles
-----------------
* CACHE-FIRST, reproducible: pulls are cached to data/cache/{source}_{id}.csv and
  committed, so a deck rebuild is deterministic and works offline (the build
  sandbox has no API egress). Pass refresh=True to re-pull.
* PROVENANCE: every frame carries .attrs["provenance"], e.g.
  "Source: FRED · HOUST · retrieved 2026-06-18" — drop straight into the caption.
* KEYS via env vars (FRED_API_KEY, BEA_API_KEY, BLS_API_KEY, CENSUS_API_KEY),
  never in the repo. FRED/BEA/BLS(v2) need a free key; Census is optional for
  light use.
* REGISTRY: series_registry.yaml maps friendly names -> {source, id, transform}
  so deck authors reference concepts ("housing_starts"), not cryptic IDs.

NOTE: live HTTP is intentionally isolated in _http_get(); everything else works
from cache. Endpoints are the documented public REST APIs — confirm exact
params against current docs when you wire a new series.
"""

from __future__ import annotations
import os, json, datetime as _dt
from pathlib import Path
import pandas as pd

CACHE_DIR = Path(__file__).resolve().parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _today() -> str:
    return _dt.date.today().isoformat()


def _cache_path(source: str, series_id: str) -> Path:
    safe = series_id.replace("/", "_").replace(":", "_")
    return CACHE_DIR / f"{source.lower()}_{safe}.csv"


def _http_get(url: str, params: dict) -> dict:
    """Isolated network call (requests). Raises if offline / no egress."""
    import requests  # imported lazily so cache-only use needs no network stack
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _finish(df: pd.DataFrame, source: str, series_id: str, label: str,
            retrieved: str) -> pd.DataFrame:
    df = df[["date", "value"]].copy()
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna().sort_values("date").reset_index(drop=True)
    df["series_id"] = series_id
    df["label"] = label
    df["source"] = source
    df.attrs["provenance"] = f"Source: {source} · {series_id} · retrieved {retrieved}"
    return df


def _load_or_fetch(source, series_id, label, fetch_fn, refresh=False) -> pd.DataFrame:
    cp = _cache_path(source, series_id)
    if cp.exists() and not refresh:
        df = pd.read_csv(cp)
        df.attrs["provenance"] = (
            f"Source: {source} · {series_id} · cached {cp.stat().st_mtime:.0f}"
        )
        # prefer a stored provenance line if present
        meta = cp.with_suffix(".meta")
        if meta.exists():
            df.attrs["provenance"] = meta.read_text().strip()
        return df
    df = fetch_fn()
    df.to_csv(cp, index=False)
    cp.with_suffix(".meta").write_text(df.attrs["provenance"])
    return df


# ---------------------------------------------------------------- FRED -------
def fred(series_id: str, label: str | None = None, refresh: bool = False) -> pd.DataFrame:
    """St. Louis Fed FRED. Needs FRED_API_KEY. e.g. fred('HOUST', 'Housing starts')."""
    label = label or series_id

    def _fetch():
        key = os.environ["FRED_API_KEY"]
        js = _http_get("https://api.stlouisfed.org/fred/series/observations",
                       {"series_id": series_id, "api_key": key, "file_type": "json"})
        df = pd.DataFrame(js["observations"]).rename(columns={"value": "value"})
        return _finish(df, "FRED", series_id, label, _today())

    return _load_or_fetch("FRED", series_id, label, _fetch, refresh)


# ---------------------------------------------------------------- BLS --------
def bls(series_id: str, label: str | None = None, start: int = 2015,
        end: int | None = None, refresh: bool = False) -> pd.DataFrame:
    """Bureau of Labor Statistics v2. Needs BLS_API_KEY. e.g. bls('CUUR0000SA0','CPI-U')."""
    label = label or series_id
    end = end or _dt.date.today().year

    def _fetch():
        key = os.environ["BLS_API_KEY"]
        import requests
        r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                          json={"seriesid": [series_id], "startyear": str(start),
                                "endyear": str(end), "registrationkey": key}, timeout=30)
        r.raise_for_status()
        rows = r.json()["Results"]["series"][0]["data"]
        recs = [{"date": f"{x['year']}-{x['period'][1:]}-01", "value": x["value"]}
                for x in rows if x["period"].startswith("M")]
        return _finish(pd.DataFrame(recs), "BLS", series_id, label, _today())

    return _load_or_fetch("BLS", series_id, label, _fetch, refresh)


# ---------------------------------------------------------------- BEA --------
def bea(table: str, line: str, freq: str = "Q", label: str | None = None,
        refresh: bool = False) -> pd.DataFrame:
    """Bureau of Economic Analysis. Needs BEA_API_KEY. (NIPA table/line; confirm params.)"""
    series_id = f"{table}:{line}:{freq}"
    label = label or series_id

    def _fetch():
        key = os.environ["BEA_API_KEY"]
        js = _http_get("https://apps.bea.gov/api/data", {
            "UserID": key, "method": "GetData", "datasetname": "NIPA",
            "TableName": table, "Frequency": freq, "Year": "ALL", "ResultFormat": "json"})
        data = js["BEAAPI"]["Results"]["Data"]
        recs = [{"date": d["TimePeriod"], "value": d["DataValue"].replace(",", "")}
                for d in data if d.get("LineNumber") == str(line)]
        df = pd.DataFrame(recs)
        df["date"] = df["date"].str.replace("Q1", "-01-01").str.replace("Q2", "-04-01") \
                               .str.replace("Q3", "-07-01").str.replace("Q4", "-10-01")
        return _finish(df, "BEA", series_id, label, _today())

    return _load_or_fetch("BEA", series_id, label, _fetch, refresh)


# ------------------------------------------------------------- Census --------
def census(dataset: str, variable: str, geo: str = "us:1", year: int = 2023,
           label: str | None = None, refresh: bool = False) -> pd.DataFrame:
    """U.S. Census (ACS etc.). CENSUS_API_KEY optional for light use. Cross-sectional;
    returns one row per geography (date = survey year)."""
    series_id = f"{dataset}:{variable}:{year}"
    label = label or series_id

    def _fetch():
        params = {"get": variable, "for": geo}
        if os.environ.get("CENSUS_API_KEY"):
            params["key"] = os.environ["CENSUS_API_KEY"]
        rows = _http_get(f"https://api.census.gov/data/{year}/{dataset}", params)
        hdr, *vals = rows
        idx = hdr.index(variable)
        recs = [{"date": f"{year}-01-01", "value": v[idx]} for v in vals]
        return _finish(pd.DataFrame(recs), "Census", series_id, label, _today())

    return _load_or_fetch("Census", series_id, label, _fetch, refresh)


# --------------------------------------------------------- friendly registry -
def from_registry(name: str, refresh: bool = False) -> pd.DataFrame:
    """Resolve a friendly name via series_registry.yaml and fetch it."""
    import yaml
    reg = yaml.safe_load((Path(__file__).resolve().parent / "series_registry.yaml").read_text())
    spec = reg[name]
    fn = {"FRED": fred, "BLS": bls, "BEA": bea, "Census": census}[spec["source"]]
    df = fn(spec["id"], label=spec.get("label", name), refresh=refresh)
    if spec.get("transform") == "yoy":
        df["value"] = df["value"].pct_change(12) * 100
        df = df.dropna()
    return df
