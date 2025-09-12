# Dexter Technical Paper (LaTeX)

This folder contains a minimal LaTeX project to generate a research-style PDF for the Dexter paper.

## Files
- `main.tex`: Paper source (uses natbib, xelatex).
- `refs.bib`: Bibliography entries.
- `Makefile`: Convenience targets to build/clean.

## Build

Prerequisites (macOS):
- Pandoc
- BasicTeX/TeXLive with `xelatex` and common packages

Install:
```
brew install pandoc
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install xetex collection-fontsrecommended geometry fancyhdr titlesec titling \
  hyperref xcolor microtype upquote bookmark kvoptions etoolbox ifxetex ifluatex fontspec \
  unicode-math url csquotes natbib
```

Build PDF:
```
make -C "$(dirname \"$0\")" pdf
# or
cd techical_paper/technical_paper_tex && make pdf
```

Output: `technical_paper.pdf`

Note: The architecture figure references `../../docs/System_Architecture.png`. Ensure the path remains valid.


