MASTER=manual
DESTDIR=../pdf
OUTDIR=../out
LATEX=pdflatex
LATEXOPTS=-output-directory $(OUTDIR)

pdf:
	$(LATEX) $(LATEXOPTS) $(MASTER)
	$(LATEX) $(LATEXOPTS) $(MASTER)
	mv $(OUTDIR)/$(MASTER).pdf $(DESTDIR)

clean:
	rm $(OUTDIR)/* $(DESTDIR)/$(MASTER).pdf
