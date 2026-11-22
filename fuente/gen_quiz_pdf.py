import json, re, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
Q, GUIA, LM = d["Q"], d["GUIA"], d["LM"]
out = open(sys.argv[2], "w", encoding="utf-8")
w = lambda s="": out.write(s + "\n")


def tx(s):
    """Convierte un texto (HTML ligero + LaTeX en $...$) a LaTeX."""
    parts = re.split(r"(\\\[.*?\\\]|\$[^$]*\$)", s)
    res = []
    for i, p in enumerate(parts):
        if i % 2:
            res.append(p)
            continue
        p = p.replace("\\", r"\textbackslash{}")
        for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")]:
            p = p.replace(a, b)
        p = re.sub(r"<b>(.*?)</b>", r"\\textbf{\1}", p)
        p = p.replace("«", "\\guillemotleft{}").replace("»", "\\guillemotright{}")
        res.append(p)
    return "".join(res)


def pasos(lst):
    """Lista de pasos: '#n ' numerado, '> ' subpaso, '\\[' display, otro: texto."""
    if not lst:
        return
    w(r"\begin{pasos}")
    insub = False
    for x in lst:
        sub = x.startswith("> ")
        if sub and not insub:
            w(r"\begin{subpasos}"); insub = True
        if not sub and insub:
            w(r"\end{subpasos}"); insub = False
        m = re.match(r"^#(\d+) ", x)
        if sub:
            w(r"\item " + tx(x[2:]))
        elif m:
            w(r"\item[(%s)] " % m.group(1) + tx(x[m.end():]))
        elif x.startswith("\\["):
            w(r"\item[] " + x)
        else:
            w(r"\item[] " + tx(x))
    if insub:
        w(r"\end{subpasos}")
    w(r"\end{pasos}")


def cabecera(i, q):
    cl = ("Clases " if len(q["cl"]) > 1 else "Clase ") + ", ".join(map(str, q["cl"]))
    return r"\textsc{%s} · %s" % (tx(q["tema"]), cl)


def probs(pr):
    if not pr:
        return ""
    return ("Problemas " if len(pr) > 1 else "Problema ") + ", ".join(map(str, pr))


w(r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noshorthands,es-nodecimaldot]{babel}
\usepackage{lmodern,microtype}
\usepackage{amsmath,amssymb,mathtools}
\usepackage[margin=2.3cm]{geometry}
\usepackage{enumitem,xcolor,titlesec}
\usepackage[hidelinks]{hyperref}
\usepackage{needspace}
\definecolor{acento}{HTML}{1F5F8B}\definecolor{ok}{HTML}{1F7A4A}\definecolor{bad}{HTML}{B23A2E}
\newcommand{\R}{\mathbb{R}}\newcommand{\N}{\mathbb{N}}\newcommand{\Q}{\mathbb{Q}}
\newcommand{\K}{\mathcal{K}}\newcommand{\M}{\mathbb{M}}
\DeclareMathOperator{\diam}{diam}\DeclareMathOperator{\dis}{dis}\DeclareMathOperator{\dist}{dist}
\newcommand{\cl}[1]{\overline{#1}}\newcommand{\norm}[1]{\lVert #1\rVert}\newcommand{\abs}[1]{\lvert #1\rvert}
\providecommand{\lt}{<}\providecommand{\gt}{>}
\newlist{pasos}{itemize}{2}\setlist[pasos]{label={},leftmargin=2.4em,labelsep=0.6em,itemsep=2pt,topsep=3pt}
\newlist{subpasos}{itemize}{2}\setlist[subpasos]{label={},leftmargin=1.6em,itemsep=1pt,topsep=1pt}
\titleformat{\section}{\Large\bfseries\color{acento}}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries}{}{0pt}{}
\newcommand{\parte}[1]{\section*{#1}\addcontentsline{toc}{section}{#1}}
\emergencystretch=3em
\newcommand{\bloque}[1]{\par\smallskip\noindent\textbf{\color{acento}#1}\par}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\title{Análisis Real (MAT2514)\\[4pt]\large Quiz de repaso: verdadero o falso, con respuestas, ejemplos y ejercicios}
\author{Prof. Mircea Petrache --- 2026, segundo semestre}
\date{}
\begin{document}
\maketitle
\thispagestyle{empty}""")

w(r"""\noindent Esta es la versión en PDF del quiz del sitio de repaso
(\url{https://decostruttivismo.github.io/MAT2514-repaso/}).
Cada afirmación es verdadera o falsa, y cada una corresponde a un error que descuenta puntos en los problemas de la guía del examen.

\begin{itemize}[leftmargin=1.4em,itemsep=1pt]
\item \textbf{Parte 1.} Las %d afirmaciones, para responder sin ver la solución.
\item \textbf{Parte 2.} La respuesta de cada una con su justificación paso a paso, cuándo la afirmación sí es verdadera, y dónde aparece en la guía y en los apuntes.
\item \textbf{Parte 3.} Para cada pregunta, un ejemplo tomado de los apuntes y un ejercicio.
\item \textbf{Parte 4.} Las soluciones de los ejercicios.
\item \textbf{Apéndice.} Los enunciados de los problemas de la guía del examen, a los que se refieren las respuestas.
\end{itemize}
Las referencias del tipo ``Teorema 20.16'' remiten a los apuntes completos (\texttt{MAT2514\_apuntes\_completos.pdf}).
""" % len(Q))
w(r"\tableofcontents\newpage")

# Parte 1
w(r"\parte{Parte 1. Las afirmaciones}")
w(r"Marque V o F. La respuesta está en la Parte 2, con el mismo número.")
w(r"\begin{enumerate}[leftmargin=2.2em,itemsep=8pt,label=\textbf{\arabic*.}]")
for i, q in enumerate(Q):
    w(r"\item \label{q%d}{\small %s}\hfill \textbf{V}\,\fbox{\rule{0pt}{6pt}\hspace{6pt}}\quad\textbf{F}\,\fbox{\rule{0pt}{6pt}\hspace{6pt}}\par %s"
      % (i + 1, cabecera(i, q), tx(q["s"])))
w(r"\end{enumerate}")

# Parte 2
w(r"\newpage\parte{Parte 2. Respuestas y justificaciones}")
for i, q in enumerate(Q):
    n = i + 1
    color, val = ("ok", "Verdadero") if q["v"] else ("bad", "Falso")
    w(r"\needspace{6\baselineskip}")
    w(r"\subsection*{%d.\ \textcolor{%s}{%s}}\label{r%d}" % (n, color, val, n))
    w(r"{\small %s}\par" % cabecera(i, q))
    w(r"\emph{%s}" % tx(q["s"]))
    w(r"\bloque{Justificación}")
    pasos(q["p"])
    if not q["v"] and q.get("y"):
        w(r"\bloque{¿Y cuándo es verdadero?}")
        pasos(q["y"])
    if q.get("g"):
        w(r"\bloque{En la guía del examen}")
        pasos(q["g"])
    refs = [LM[x][1] for x in q.get("l", []) if x in LM]
    linea = []
    if refs:
        linea.append(r"\textbf{En los apuntes:} " + " · ".join(refs))
    if q.get("pr"):
        linea.append(r"\textbf{Guía:} " + probs(q["pr"]))
    if linea:
        w(r"\par\smallskip{\small " + r" \quad ".join(linea) + "}")
    w(r"\par{\small Ejemplo y ejercicio: Parte 3, pregunta %d.}" % n)

# Parte 3
w(r"\newpage\parte{Parte 3. Ejemplos y ejercicios}")
w(r"Para cada pregunta del quiz, un ejemplo tomado de los apuntes y un ejercicio. Las soluciones de los ejercicios están en la Parte 4.")
for i, q in enumerate(Q):
    n = i + 1
    e, x = q["e"], q["x"]
    w(r"\needspace{6\baselineskip}")
    w(r"\subsection*{Pregunta %d \normalfont\small(%s)}" % (n, cabecera(i, q)))
    ref = ""
    if e.get("l") and e["l"] in LM:
        ref = r" {\small(en los apuntes: %s)}" % LM[e["l"]][1]
    w(r"\bloque{Ejemplo}")
    w(r"\textit{%s}%s" % (tx(e["t"]), ref))
    pasos(e["p"])
    w(r"\bloque{Ejercicio %d}" % n)
    w(tx(x["t"]))

# Parte 4
w(r"\newpage\parte{Parte 4. Soluciones de los ejercicios}")
for i, q in enumerate(Q):
    n = i + 1
    x = q["x"]
    w(r"\needspace{6\baselineskip}")
    w(r"\subsection*{Solución del ejercicio %d}" % n)
    w(r"\emph{%s}" % tx(x["t"]))
    pasos(x["p"])

# Apéndice
w(r"\newpage\parte{Apéndice. Problemas de la guía del examen}")
w(r"La guía tiene 17 problemas. Los Problemas 3, 7 y 8 se resolvieron en el taller de la Clase 43 y no estarán en el examen; los Problemas 15 y 16 son complementarios.")
for g in GUIA:
    w(r"\needspace{5\baselineskip}")
    comp = r" {\normalfont\small(complementario)}" if g.get("comp") else ""
    w(r"\subsection*{Problema %d. %s%s}" % (g["n"], tx(g["t"]), comp))
    if g.get("intro"):
        w(tx(g["intro"]))
    w(r"\begin{enumerate}[label=(\alph*),leftmargin=2.2em,itemsep=2pt]")
    for p in g["parts"]:
        w(r"\item[(%s)] %s" % (p["l"], tx(p["t"])))
    w(r"\end{enumerate}")
    if g.get("sug"):
        w(r"{\small\itshape %s}" % tx(g["sug"]))
    its = sorted(g.get("its", []), key=lambda t: t["i"])
    if its:
        w(r"\par{\small\textbf{Preguntas del quiz relacionadas:} %s}" % ", ".join(str(t["i"]) for t in its))

w(r"\end{document}")
out.close()
