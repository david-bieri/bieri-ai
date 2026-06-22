"""
figures.py — captions for figures and tables, shared across pptx and LaTeX/Beamer.

Captions live once in captions.yaml. The caption_mode toggle decides how a caption
is realized for the chosen target:

    off    image only; the pptx slide carries the text          (deck default)
    host   emit a LaTeX figure/table environment with \\caption  (papers, Beamer)
    baked   draw the caption into the image itself (charts only; standalone use)

Usage
-----
    from figures import caption_for, latex_figure, latex_table, pptx_caption

    # pptx deck: put text on the slide, image stays clean
    c = pptx_caption("supply_fan")          # -> {"title":..., "source":...}

    # paper / Beamer: real float with numbering + \\ref
    tex = latex_figure("supply_fan", "figures_pdf/supply_fan.pdf")
    # -> \\begin{figure}... \\includegraphics... \\caption{...}\\label{fig:supply_fan} ...

    # table from a tidy DataFrame
    tex = latex_table("elasticity_summary", df)
"""
from __future__ import annotations
from pathlib import Path
import yaml

_CAPS = None


def _caps() -> dict:
    global _CAPS
    if _CAPS is None:
        _CAPS = yaml.safe_load((Path(__file__).resolve().parent / "captions.yaml").read_text())
    return _CAPS


def caption_for(key: str) -> dict:
    """Return the raw caption record (short, caption, source, kind)."""
    return _caps()[key]


def dump_json(out: str = "captions.json") -> str:
    """Export captions.yaml -> captions.json so the JS deck builder (slide_lib.js
    figureSlide) can pull a figure's caption without a YAML parser. Run in the
    figures build (Makefile)."""
    import json
    Path(out).write_text(json.dumps(_caps(), indent=2))
    return out


# ----------------------------------------------------------------- pptx ------
def pptx_caption(key: str) -> dict:
    """Slide-side text for a deck: the short title and the source line.
    The embedded image carries NO caption (caption_mode='off')."""
    c = caption_for(key)
    return {"title": c.get("short", key), "source": c.get("source", "")}


# -------------------------------------------------------- LaTeX / Beamer -----
def latex_figure(key: str, image: str, *, placement: str = "htbp",
                 width: str = "0.8\\linewidth", label_prefix: str = "fig") -> str:
    """Emit a LaTeX figure float with \\caption + \\label (caption_mode='host').
    `source`, if present, is set as a small caption footnote via threeparttable."""
    c = caption_for(key)
    src = c.get("source", "")
    foot = (f"\n    \\begin{{tablenotes}}\\footnotesize\\itshape\n"
            f"      \\item {src}\n    \\end{{tablenotes}}") if src else ""
    body = (f"  \\includegraphics[width={width}]{{{image}}}" if not src else
            f"  \\begin{{threeparttable}}\n"
            f"    \\includegraphics[width={width}]{{{image}}}{foot}\n"
            f"  \\end{{threeparttable}}")
    return (f"\\begin{{figure}}[{placement}]\\centering\n"
            f"{body}\n"
            f"  \\caption{{{c['caption'].strip()}}}\n"
            f"  \\label{{{label_prefix}:{key}}}\n"
            f"\\end{{figure}}\n")


def beamer_figure(key: str, image: str, *, width: str = "0.85\\linewidth") -> str:
    """Beamer-friendly: centered graphic + a small caption line (no float numbering)."""
    c = caption_for(key)
    src = c.get("source", "")
    src_line = f"\n  \\par\\smallskip{{\\scriptsize\\itshape\\color{{gray}} {src}}}" if src else ""
    return (f"\\begin{{center}}\n"
            f"  \\includegraphics[width={width}]{{{image}}}{src_line}\n"
            f"\\end{{center}}\n")


def latex_table(key: str, df, *, placement: str = "htbp", index: bool = False,
                label_prefix: str = "tab", dec: int = 3) -> str:
    """Emit a booktabs table float from a tidy DataFrame (caption_mode='host').
    AER conventions: horizontal rules only (no vlines/shading), leading-zero
    decimals, source note last. Warns past 9 columns."""
    import warnings
    c = caption_for(key)
    cols = list(df.columns)
    ncol = len(cols) + (1 if index else 0)
    if ncol > 9:
        warnings.warn(f"AER style: table '{key}' has {ncol} columns (>9). Consider splitting.")

    def _cell(v):
        # AER: leading zero on decimals (0.357, never .357); ints/text untouched.
        if isinstance(v, float):
            return f"{v:.{dec}f}"
        return str(v)

    align = ("l" if index else "") + "r" * len(cols)
    header = " & ".join(str(x) for x in cols) + " \\\\"
    rows = [" & ".join(_cell(v) for v in r.tolist()) + " \\\\" for _, r in df.iterrows()]
    body = "\n    ".join(rows)
    src = c.get("source", "")
    foot = (f"\n  \\begin{{tablenotes}}\\footnotesize\\itshape\\item {src}\\end{{tablenotes}}"
            if src else "")
    inner = (f"  \\begin{{tabular}}{{{align}}}\n    \\toprule\n    {header}\n"
             f"    \\midrule\n    {body}\n    \\bottomrule\n  \\end{{tabular}}")
    if src:
        inner = f"  \\begin{{threeparttable}}\n{inner}{foot}\n  \\end{{threeparttable}}"
    return (f"\\begin{{table}}[{placement}]\\centering\n"
            f"  \\caption{{{c['caption'].strip()}}}\n"
            f"  \\label{{{label_prefix}:{key}}}\n"
            f"{inner}\n"
            f"\\end{{table}}\n")
