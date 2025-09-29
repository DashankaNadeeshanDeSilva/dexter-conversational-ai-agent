PDF=technical_paper.pdf
TEX=main.tex

all: pdf

pdf:
	pandoc $(TEX) -o $(PDF) --pdf-engine=xelatex --toc

clean:
	rm -f $(PDF) *.aux *.log *.out *.bbl *.blg

.PHONY: all pdf clean

