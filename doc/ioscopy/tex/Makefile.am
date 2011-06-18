MASTER=ioscopy-manual
DESTDIR=../pdf
OUTDIR=../out
LATEX=pdflatex
LATEXOPTS=-output-directory $(OUTDIR)

FIGS=

../pdf/$(MASTER).pdf: pdf-local

pdf-local: $(FIGS)
	$(LATEX) $(LATEXOPTS) $(MASTER)
	$(LATEX) $(LATEXOPTS) $(MASTER)
	mv $(OUTDIR)/$(MASTER).pdf $(DESTDIR)

clean-local:
	rm $(OUTDIR)/* $(DESTDIR)/$(MASTER).pdf $(FIGS)

../pdf/%.pdf : ../dot/%.dot
	dot -Tps2 $< > ../eps/tmp.eps
	epstopdf --outfile=$@ ../eps/tmp.eps
	rm -f ../eps/tmp.eps