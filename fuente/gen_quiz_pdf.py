import json, re, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
Q, GUIA, LM = d["Q"], d["GUIA"], d["LM"]
out = open(sys.argv[2], "w", encoding="utf-8")
w = lambda s="": out.write(s + "\n")

# Destinos con nombre del PDF de apuntes (para enlazar "Teorema 20.16", etc.)
APUNTES = "https://decostruttivismo.github.io/MAT2514-repaso/pdf/MAT2514_apuntes_completos.pdf"
DESTS = set(json.load(open(sys.argv[3], encoding="utf-8"))) if len(sys.argv) > 3 else None
PG = {g["n"] for g in GUIA}


def ap(dest, texto):
    """Enlace a un destino del PDF de apuntes (si existe)."""
    if DESTS is not None and dest not in DESTS:
        return texto
    return r"\href{%s\#nameddest=%s}{%s}" % (APUNTES, dest, texto)


def prob(n, texto):
    return r"\hyperlink{prob-%d}{%s}" % (n, texto) if n in PG else texto


def enlaces(p):
    """Enlaza referencias a los apuntes y a los problemas de la guía (texto fuera de math)."""
    p = re.sub(r"(Teorema|Proposición|Lema|Corolario|Definición|Ejemplo|Observación)(s?) (\d+\.\d+)",
               lambda m: ap("teorema." + m.group(3), m.group(0)), p)
    p = re.sub(r"Ejercicio (A?\w+\.\d+)", lambda m: ap("ejercicio." + m.group(1), m.group(0)), p)
    p = re.sub(r"(Problemas? )((?:\d+(?:\([a-c]\))?)(?:(?:, | y )\d+(?:\([a-c]\))?)*)",
               lambda m: m.group(1) + re.sub(r"(\d+)(\([a-c]\))?",
                                             lambda k: prob(int(k.group(1)), k.group(0)), m.group(2)), p)
    return p


def tx(s, links=True):
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
        if links:
            p = enlaces(p)
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
    cl = ("Clases " if len(q["cl"]) > 1 else "Clase ") + ", ".join(ap("section.%d" % c, str(c)) for c in q["cl"])
    return r"\textsc{%s} · %s" % (tx(q["tema"], False), cl)


def probs(pr):
    if not pr:
        return ""
    return ("Problemas " if len(pr) > 1 else "Problema ") + ", ".join(prob(n, str(n)) for n in pr)


w(r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noshorthands,es-nodecimaldot]{babel}
\usepackage{lmodern,microtype}
\usepackage{amsmath,amssymb,mathtools}
\usepackage[margin=2.3cm]{geometry}
\usepackage{enumitem,xcolor,titlesec}
\usepackage[colorlinks,linkcolor=acento,urlcolor=acento,citecolor=acento,bookmarksnumbered]{hyperref}
\usepackage{needspace}
\usepackage{xcolor}\definecolor{acento}{HTML}{1F5F8B}\definecolor{ok}{HTML}{1F7A4A}\definecolor{bad}{HTML}{B23A2E}
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
\textbf{Cómo navegar.} El documento es clickeable. En la Parte 1, el número de cada afirmación lleva a su respuesta; desde la respuesta se va al ejemplo y ejercicio, y desde el ejercicio a su solución. Las menciones de un problema de la guía llevan a su enunciado en el Apéndice. Las referencias del tipo ``Teorema 20.16'' y los números de clase abren los \href{%s}{apuntes completos} en el lugar exacto (se necesita conexión a internet).
""" % (len(Q), APUNTES))
w(r"\tableofcontents\newpage")

# Parte 1
w(r"\parte{Parte 1. Las afirmaciones}")
w(r"Marque V o F. La respuesta está en la Parte 2, con el mismo número: haga clic en el número para ir a ella.")
w(r"\begin{enumerate}[leftmargin=2.2em,itemsep=8pt,label=\textbf{\arabic*.}]")
for i, q in enumerate(Q):
    w(r"\item[\hyperlink{r-%d}{\textbf{%d.}}] \hypertarget{q-%d}{}{\small %s}\hfill \textbf{V}\,\fbox{\rule{0pt}{6pt}\hspace{6pt}}\quad\textbf{F}\,\fbox{\rule{0pt}{6pt}\hspace{6pt}}\par %s\hfill{\footnotesize\hyperlink{r-%d}{ver respuesta}}"
      % (i + 1, i + 1, i + 1, cabecera(i, q), tx(q["s"]), i + 1))
w(r"\end{enumerate}")

# Parte 2
w(r"\newpage\parte{Parte 2. Respuestas y justificaciones}")
for i, q in enumerate(Q):
    n = i + 1
    color, val = ("ok", "Verdadero") if q["v"] else ("bad", "Falso")
    w(r"\needspace{6\baselineskip}")
    w(r"\subsection*{\hypertarget{r-%d}{}%d.\ \textcolor{%s}{%s}}" % (n, n, color, val))
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
    refs = [ap(LM[x][0], LM[x][1]) for x in q.get("l", []) if x in LM]
    linea = []
    if refs:
        linea.append(r"\textbf{En los apuntes:} " + " · ".join(refs))
    if q.get("pr"):
        linea.append(r"\textbf{Guía:} " + probs(q["pr"]))
    if linea:
        w(r"\par\smallskip{\small " + r" \quad ".join(linea) + "}")
    w(r"\par{\small \hyperlink{e-%d}{Ejemplo y ejercicio de esta pregunta} \quad·\quad \hyperlink{q-%d}{volver a la afirmación}}" % (n, n))

# Parte 3
w(r"\newpage\parte{Parte 3. Ejemplos y ejercicios}")
w(r"Para cada pregunta del quiz, un ejemplo tomado de los apuntes y un ejercicio. Las soluciones de los ejercicios están en la Parte 4.")
for i, q in enumerate(Q):
    n = i + 1
    e, x = q["e"], q["x"]
    w(r"\needspace{6\baselineskip}")
    w(r"\subsection*{\hypertarget{e-%d}{}Pregunta %d \normalfont\small(%s)}" % (n, n, cabecera(i, q)))
    ref = ""
    if e.get("l") and e["l"] in LM:
        ref = r" {\small(en los apuntes: %s)}" % ap(LM[e["l"]][0], LM[e["l"]][1])
    w(r"\bloque{Ejemplo}")
    w(r"\textit{%s}%s" % (tx(e["t"]), ref))
    pasos(e["p"])
    w(r"\bloque{\hypertarget{x-%d}{}Ejercicio %d}" % (n, n))
    w(tx(x["t"]))
    w(r"\par{\small \hyperlink{s-%d}{Ver solución} \quad·\quad \hyperlink{r-%d}{volver a la respuesta de la pregunta %d}}" % (n, n, n))

# Parte 4
w(r"\newpage\parte{Parte 4. Soluciones de los ejercicios}")
for i, q in enumerate(Q):
    n = i + 1
    x = q["x"]
    w(r"\needspace{6\baselineskip}")
    w(r"\subsection*{\hypertarget{s-%d}{}Solución del ejercicio %d}" % (n, n))
    w(r"\emph{%s}" % tx(x["t"]))
    pasos(x["p"])
    w(r"\par{\small \hyperlink{x-%d}{volver al ejercicio} \quad·\quad \hyperlink{r-%d}{respuesta de la pregunta %d}}" % (n, n, n))

# Apéndice
w(r"\newpage\parte{Apéndice. Problemas de la guía del examen}")
w(r"La guía tiene 17 problemas. Los Problemas~3, 7 y 8 se resolvieron en el taller de la Clase 43 y no estarán en el examen; los Problemas 15 y 16 son complementarios.")
for g in GUIA:
    w(r"\needspace{5\baselineskip}")
    comp = r" {\normalfont\small(complementario)}" if g.get("comp") else ""
    w(r"\subsection*{\hypertarget{prob-%d}{}Problema %d. %s%s}" % (g["n"], g["n"], tx(g["t"], False), comp))
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
        w(r"\par{\small\textbf{Preguntas del quiz relacionadas:} %s}" % ", ".join(r"\hyperlink{r-%d}{%d}" % (t["i"], t["i"]) for t in its))

w(r"\end{document}")
out.close()
