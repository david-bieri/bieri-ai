"""
chart_lib.py — empirical charts for teaching-charts, in Bieri house style.

Covers line (time series), bar, scatter / dot-plot, and box-whisker. Sankey is a
separate engine (plotly) — see sankey() note. All chart types share:

  target      "png"  -> raster for pptx embed (default)
              "pdf"  -> vector for LaTeX/Beamer \\includegraphics
              "pgf"  -> vector whose TEXT is rendered by LaTeX (XCharter), so the
                        chart font matches the diagrams exactly in a LaTeX doc
  caption_mode  "off"  -> no caption baked in; the slide / \\caption carries it (default)
                "baked"-> draw the caption (from captions.yaml) into the image

Data frames are the tidy output of datasources.py (date|value|label, with
.attrs['provenance']), but any DataFrame works.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = Path(__file__).resolve().parent
STYLE = str(_HERE / "bieri.mplstyle")
RED, DARK, GRAY = "#C00000", "#262626", "#808080"

# Register tex-gyre OTFs (Palatino/Heros) so the raster path finds them on Linux.
# On Windows/Office, "Palatino Linotype" is found natively and this is a no-op.
def _ensure_fonts():
    import matplotlib.font_manager as fm
    known = {f.name for f in fm.fontManager.ttflist}
    if "TeX Gyre Pagella" in known:
        return
    import glob
    for pat in ("/usr/share/texmf*/fonts/opentype/public/tex-gyre/texgyrepagella-*.otf",
                "/usr/share/texmf*/fonts/opentype/public/tex-gyre/texgyreheros-regular.otf"):
        for f in glob.glob(pat):
            try:
                fm.fontManager.addfont(f)
            except Exception:
                pass


def _num(x, dec: int = 2) -> str:
    """AER decimal style: fixed decimals with a leading zero (0.357, never .357).
    Python's fixed-point format already keeps the leading zero; this centralizes it."""
    return f"{x:.{dec}f}"


def _use_target(target: str):
    _ensure_fonts()
    plt.style.use(STYLE)
    if target == "pgf":
        matplotlib.use("pgf")
        plt.rcParams.update({
            "pgf.texsystem": "pdflatex",
            "text.usetex": True,
            "pgf.preamble": r"\usepackage{XCharter}\usepackage[xcharter]{newtxmath}",
        })


def _finish(fig, ax, out: str, target: str, key: str | None, caption_mode: str,
            source: str | None):
    # source / provenance line under the axes — unless the host caption owns it
    if source and caption_mode != "host":
        fig.text(0.01, -0.02, source, ha="left", va="top",
                 fontsize=8, style="italic", color=GRAY)
    # optional baked caption (standalone use)
    if caption_mode == "baked" and key:
        from figures import caption_for
        cap = caption_for(key)["caption"].strip()
        fig.text(0.01, -0.10, cap, ha="left", va="top", fontsize=8.5,
                 color=DARK, wrap=True)
    ext = {"png": ".png", "pdf": ".pdf", "pgf": ".pdf"}[target]
    out = str(Path(out).with_suffix(ext))
    fig.savefig(out)
    plt.close(fig)
    return out


def _source_of(df, source):
    if source is not None:
        return source
    return getattr(df, "attrs", {}).get("provenance", "")


# ---------------------------------------------------------------- line -------
def timeseries(df, out, *, ylabel=None, annotate_last=True, target="png",
               caption_mode="off", key=None, source=None):
    _use_target(target)
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["value"], marker="o")
    ax.set_ylabel(ylabel or "")
    ax.margins(x=0.02)
    if annotate_last:
        last = df.iloc[-1]
        ax.annotate(f"{last['value']:.0f}", (last["date"], last["value"]),
                    textcoords="offset points", xytext=(6, 0), color=RED,
                    fontsize=9, va="center")
    return _finish(fig, ax, out, target, key, caption_mode, _source_of(df, source))


# ---------------------------------------------------------------- bar --------
def bar(labels, values, out, *, ylabel=None, horizontal=False, target="png",
        caption_mode="off", key=None, source=""):
    _use_target(target)
    fig, ax = plt.subplots()
    (ax.barh if horizontal else ax.bar)(labels, values, color=RED, edgecolor="none")
    ax.set_ylabel("" if horizontal else (ylabel or ""))
    if horizontal:
        ax.set_xlabel(ylabel or "")
        ax.invert_yaxis()
    return _finish(fig, ax, out, target, key, caption_mode, source)


# ----------------------------------------------------- scatter / dot-plot ----
def scatter(x, y, out, *, xlabel=None, ylabel=None, dotplot=False, target="png",
            caption_mode="off", key=None, source=""):
    """scatter (x,y). Set dotplot=True for a 1-D categorical dot-plot: pass x as
    category labels and y as values (strip plot)."""
    _use_target(target)
    fig, ax = plt.subplots()
    if dotplot:
        for i, (cat, val) in enumerate(zip(x, y)):
            ax.plot(val, i, "o", color=RED)
        ax.set_yticks(range(len(x)))
        ax.set_yticklabels(x)
        ax.set_xlabel(xlabel or "")
    else:
        ax.scatter(x, y, color=RED, edgecolor="none", s=36)
        ax.set_xlabel(xlabel or "")
        ax.set_ylabel(ylabel or "")
    return _finish(fig, ax, out, target, key, caption_mode, source)


# ---------------------------------------------------------- box-whisker ------
def box(groups, labels, out, *, ylabel=None, target="png",
        caption_mode="off", key=None, source=""):
    """groups: list of value-arrays; labels: group names."""
    _use_target(target)
    fig, ax = plt.subplots()
    bp = ax.boxplot(groups, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch in bp["boxes"]:
        patch.set(facecolor="#F2D5D5", edgecolor=RED, linewidth=1.4)
    for k in ("whiskers", "caps", "medians"):
        for art in bp[k]:
            art.set(color=DARK if k != "medians" else RED, linewidth=1.4)
    ax.set_ylabel(ylabel or "")
    return _finish(fig, ax, out, target, key, caption_mode, source)


# ---------------------------------------------------------------- sankey -----
def sankey(*args, **kwargs):
    """Sankey/flow diagrams are a SEPARATE engine: plotly (+ kaleido for static
    export), which handles flows far better than matplotlib's matplotlib.sankey.
        pip install plotly kaleido
        import plotly.graph_objects as go
        fig = go.Figure(go.Sankey(node=..., link=...))
        fig.write_image("flow.pdf")   # or .png
    Keep node/link colors to the house palette (C00000 / 262626 / 808080).
    Not wired here to avoid a heavy default dependency."""
    raise NotImplementedError("Use plotly+kaleido for sankey — see docstring.")
