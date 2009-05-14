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
     "tab:sigs:props"
     "sec:readers"
     "fig:rds:callgraph"
     "sec:readers:reader"
     "tab:rds:meth"
     "sec:readers:detect"
     "sec:readers:readerror"
     "sec:readers:add"
     "sec:writers"
     "fig:wrts:callgraph"
     "tab:wrts:meth"
     "sec:graphs"
     "sec:figs"
     "sec:curs"
     "sec:ext")
    (TeX-add-symbols
     '("module" 1)
     '("meth" 1)
     '("att" 1)
     "sig"
     "rds"
     "rdserr"
     "wrts"
     "wrtserr")
    (TeX-run-style-hooks
     "wasysym"
     "graphicx"
     "a4wide"
     "babel"
     "english"
     "latex2e"
     "art11"
     "article"
     "a4paper"
     "11pt")))

