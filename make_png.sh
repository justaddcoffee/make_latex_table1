make_latex_table.py -i tableone.txt -o output.tex --prepend prepend.txt --append append.txt
perl -p -i -e 's/\\textbackslash\{\}hspace\\\{3mm\\\}/\\hspace\{3mm\}/' output.tex
pdflatex output.tex
which convert
convert output.tex output.png
open output.pdf
