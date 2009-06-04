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
     "tab:ctxt:meth"
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
     "sec:figs"
     "tab:figs:meth"
     "tab:figs:key"
     "sec:graphs"
     "sec:graphs:graph"
     "tab:graphs:meth"
     "tab:graphs:props"
     "fig:cursorinter"
     "sec:curs"
     "tab:cursors:meth"
     "tab:cursors:props"
     "sec:ext")
    (TeX-add-symbols
     '("module" 1)
     '("cls" 1)
     '("meth" 1)
     '("att" 1)
     "ctx"
     "sig"
     "rd"
     "rderr"
     "wrt"
     "wrterr"
     "graph"
     "fig"
     "cursor")
    (TeX-run-style-hooks
     "caption"
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

