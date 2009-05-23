MASTER=manual
DESTDIR=../pdf
OUTDIR=../out
LATEX=pdflatex
LATEXOPTS=-output-directory $(OUTDIR)

FIGS=../pdf/itf.pdf\
	 ../pdf/fileinter.pdf \
	../pdf/viewinter.pdf \
	../pdf/readers.pdf \
	../pdf/writers.pdf \
	../pdf/cursorinter.pdf

pdf: $(FIGS)
	$(LATEX) $(LATEXOPTS) $(MASTER)
	$(LATEX) $(LATEXOPTS) $(MASTER)
	mv $(OUTDIR)/$(MASTER).pdf $(DESTDIR)

clean:
	rm $(OUTDIR)/* $(DESTDIR)/$(MASTER).pdf $(FIGS)

../pdf/%.pdf : ../dot/%.dot
	dot -Tps2 $< > ../eps/tmp.eps
	epstopdf --outfile=$@ ../eps/tmp.eps
	rm -f ../eps/tmp.eps