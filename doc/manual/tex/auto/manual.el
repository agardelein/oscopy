(TeX-add-style-hook "manual"
 (lambda ()
    (LaTeX-add-labels
     "sec:intro"
     "sec:itf"
     "fig:itf"
     "sec:user"
     "sec:data"
     "sec:fileinter"
     "fig:fileinter"
     "sec:viewinter"
     "fig:viewinter"
     "sec:sigs"
     "sec:readers"
     "sec:writers"
     "sec:graphs"
     "sec:figs"
     "sec:curs"
     "sec:ext")
    (TeX-run-style-hooks
     "graphicx"
     "a4wide"
     "babel"
     "english"
     "latex2e"
     "art11"
     "article"
     "a4paper"
     "11pt")))

