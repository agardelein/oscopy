(TeX-add-style-hook "manual"
 (lambda ()
    (LaTeX-add-labels
     "sec:intro"
     "sec:obj"
     "sec:itf"
     "sec:sigs"
     "sec:graphs"
     "sec:figs")
    (TeX-run-style-hooks
     "a4wide"
     "latex2e"
     "art11"
     "article"
     "a4paper"
     "11pt")))

