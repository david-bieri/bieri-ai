# Makefile — regenerate every figure in one command.  Lives in tools/.
#   make            # diagrams + charts + captions.json
#   make diagrams   # every template *.tikz -> figures_pdf/*.pdf (+ PNG preview)
#   make charts     # build_charts.py + dump captions.json
#   make clean
#
# Paths default to the monorepo layout (Makefile in tools/, skills alongside).
# Override on the command line, e.g.  make REPO=/path/to/bieri-ai
# Requires: pdflatex (+ newpx, tex-gyre, pgfplots, binhex), pdftoppm,
#           python3 (+ matplotlib, pandas, pyyaml).

REPO        ?= ..
DIAGRAMS    ?= $(REPO)/skills/teaching-diagrams
CHARTS      ?= $(REPO)/skills/teaching-charts
TIKZ_DIR    ?= $(DIAGRAMS)/assets
STY_DIR     ?= $(DIAGRAMS)/scripts
CHART_DIR   ?= $(CHARTS)/scripts
OUT         ?= $(REPO)/build/figures
PDF_DIR     ?= $(OUT)/figures_pdf
PNG_DIR     ?= $(OUT)/render
DPI         ?= 150

TIKZ := $(wildcard $(TIKZ_DIR)/*.tikz)
PDFS := $(patsubst $(TIKZ_DIR)/%.tikz,$(PDF_DIR)/%.pdf,$(TIKZ))
PNGS := $(patsubst $(TIKZ_DIR)/%.tikz,$(PNG_DIR)/%.png,$(TIKZ))

.PHONY: all diagrams charts clean dirs
all: diagrams charts

diagrams: dirs $(PDFS) $(PNGS)

dirs:
	@mkdir -p $(PDF_DIR) $(PNG_DIR)

# Compile a TikZ body to a cropped PDF. TEXINPUTS makes bieri-tikz.sty +
# _standalone.tex (in STY_DIR) and the template resolvable; copy the body in so
# \input{NAME.tikz} resolves from the output dir.
$(PDF_DIR)/%.pdf: $(TIKZ_DIR)/%.tikz $(STY_DIR)/bieri-tikz.sty $(STY_DIR)/_standalone.tex | dirs
	cp $< $(PDF_DIR)/$*.tikz
	cd $(PDF_DIR) && TEXINPUTS="$(abspath $(STY_DIR)):" \
	  pdflatex -interaction=nonstopmode -halt-on-error -jobname=$* \
	  "\def\bieribody{$*.tikz}\input{_standalone.tex}"
	@rm -f $(PDF_DIR)/$*.aux $(PDF_DIR)/$*.log $(PDF_DIR)/$*.tikz

$(PNG_DIR)/%.png: $(PDF_DIR)/%.pdf | dirs
	pdftoppm -png -r $(DPI) -singlefile $< $(PNG_DIR)/$*

# Charts + caption bridge. PYTHONPATH lets build_charts import chart_lib/figures.
charts: dirs
	cd $(CHART_DIR) && PYTHONPATH="$(abspath $(CHART_DIR))" \
	  python3 -c "import figures; figures.dump_json('$(abspath $(OUT))/captions.json')"
	cd $(CHART_DIR) && PYTHONPATH="$(abspath $(CHART_DIR))" OUT="$(abspath $(OUT))" \
	  python3 build_charts.py

clean:
	rm -rf $(OUT)
