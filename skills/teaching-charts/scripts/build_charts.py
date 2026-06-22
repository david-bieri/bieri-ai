"""
build_charts.py — regenerate every project chart in one place (called by `make charts`).

Add an entry per chart: a function that produces a tidy frame, plus the render call.
Charts render to BOTH targets by default (PNG for pptx, PDF host-mode for LaTeX) so a
deck or paper rebuild always has a fresh figure. Live data needs API keys + network;
without them, the cache (committed) is used.
"""
from pathlib import Path
import os
import pandas as pd
import chart_lib as C

_OUT = Path(os.environ.get("OUT", ".")).resolve()
PDF = _OUT / "figures_pdf"; PNG = _OUT / "render"
PDF.mkdir(parents=True, exist_ok=True); PNG.mkdir(parents=True, exist_ok=True)


def _both(df, stem, **kw):
    """Render a chart to PNG (pptx) and PDF host-mode (LaTeX)."""
    C.timeseries(df, str(PNG / stem), target="png", **kw)
    C.timeseries(df, str(PDF / stem), target="pdf", caption_mode="host", **kw)
    print("built", stem)


# --- registered charts ------------------------------------------------------
def sunbelt_rents():
    df = pd.DataFrame({
        "date": pd.to_datetime([f"{y}-01-01" for y in range(2021, 2027)]),
        "value": [100, 109, 106, 99, 94, 91],
        "label": ["Sunbelt apartment rent index (2021 = 100)"] * 6,
    })
    df.attrs["provenance"] = ("Stylized fact --- illustrative. "
                              "Source: Federal Reserve Bank of Dallas (Mar 2026); CoStar.")
    _both(df, "sunbelt_rents", ylabel="Rent index (2021 = 100)")


# Example of a live-data chart (uncomment once FRED_API_KEY is set):
# def housing_starts():
#     from datasources import from_registry
#     df = from_registry("housing_starts")
#     _both(df, "housing_starts", ylabel="Housing starts (k, SAAR)")


CHARTS = [sunbelt_rents]   # add housing_starts, etc.

if __name__ == "__main__":
    for fn in CHARTS:
        fn()
    print(f"done: {len(CHARTS)} chart(s)")
