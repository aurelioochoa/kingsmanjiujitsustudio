#!/usr/bin/env python3
"""Generate the individual class pages for Kingsman Jiu Jitsu Studio.

Static (no-build) site. The home page index.html is hand-edited; this script
produces pages/clases/<slug>.html for each modalidad, sharing the SAME head,
nav, footer and dev theme toggle as the home page so nav stays consistent
(nav links on subpages point back to the home anchors: ../index.html#…).

Usage:
    python3 scripts/build_pages.py          # writes pages/clases/*.html
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "./"           # href base for home (anchors)
OUT = os.path.join(ROOT, "pages", "clases")

IG = "https://ig.me/m/kingsmanjiujitsustudio"

HEAD = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>document.documentElement.classList.add('js');</script>
<script>try{if(localStorage.getItem('kingsman-theme')==='b')document.documentElement.setAttribute('data-theme','b')}catch(e){}</script>
<title>{TITLE} | Kingsman Jiu Jitsu Studio</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="https://kingsmanjiujitsustudio.com/clases/{SLUG}.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://kingsmanjiujitsustudio.com/clases/{SLUG}.html">
<meta property="og:title" content="{TITLE} | Kingsman Jiu Jitsu Studio">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="https://kingsmanjiujitsustudio.com/assets/logo.jpg">
<meta property="og:locale" content="es_EC">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/jpeg" href="../assets/logo.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css">
</head>
<body>
"""

NAV = """
<header class="site-header">
  <nav class="nav container" aria-label="Principal">
    <a class="brand" href="../index.html#top">
      <img class="brand-logo" src="../assets/logo.jpg" alt="Kingsman Jiu Jitsu Studio" width="40" height="40">
      <span class="brand-word">KINGSMAN<small>JIU JITSU STUDIO</small></span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="Abrir menú">
      <span></span><span></span><span></span>
    </button>
    <ul class="nav-menu" id="nav-menu">
      <li><a class="nav-link" href="../index.html#clases">Clases</a></li>
      <li><a class="nav-link" href="../index.html#horarios">Horarios</a></li>
      <li><a class="nav-link" href="../index.html#planes">Planes</a></li>
      <li><a class="nav-link" href="../index.html#linaje">Linaje</a></li>
      <li><a class="nav-link" href="../index.html#equipo">Equipo</a></li>
      <li><a class="nav-link" href="../index.html#galeria">Galería</a></li>
      <li><a class="nav-link" href="../index.html#videos">Videos</a></li>
      <li><a class="nav-link" href="../index.html#ubicacion">Ubicación</a></li>
      <li><a class="btn btn-gold nav-cta" href="{IG}" target="_blank" rel="noopener">Escríbenos</a></li>
    </ul>
  </nav>
</header>
"""

HERO = """
<section class="hero hero-page" id="top">
  <div class="hero-bg" aria-hidden="true"><div class="hero-glow"></div><div class="hero-grain"></div></div>
  <div class="hero-inner container">
    <div class="hero-copy reveal">
      <p class="kicker">{KICKER}</p>
      <h1 class="wordmark"><span class="wm-line wm-line--sm">{NAME}</span></h1>
      <p class="hero-lede">{LEDE}</p>
      <div class="hero-tags">{CHIPS}</div>
      <div class="hero-actions">
        <a class="btn btn-gold" href="{IG}" target="_blank" rel="noopener">Escríbenos por Instagram</a>
        <a class="btn btn-ghost" href="../index.html#horarios">Ver horarios</a>
      </div>
    </div>
    <figure class="hero-card tilt reveal" data-tilt>
      <img src="../{IMG}" alt="{IMGALT}" loading="eager">
      <figcaption class="hero-card-caption">#jiujitsuparatodos</figcaption>
    </figure>
  </div>
</section>
"""

BODY_CORE = """
<section class="section" id="que">
  <div class="container">
    <header class="section-head reveal">
      <p class="kicker">Qué aprenderás</p>
      <h2 class="section-title">{NAME}</h2>
      <p class="section-sub">{INTRO}</p>
    </header>
    <div class="cards">
      {LEARN}
    </div>
  </div>
</section>

<section class="section section-alt" id="horario">
  <div class="container">
    <header class="section-head reveal">
      <p class="kicker">Cuando entrenar</p>
      <h2 class="section-title">Horarios de {NAME_SLOT}</h2>
    </header>
    <div class="cards-slots">{SLOTS}</div>
  </div>
</section>

<section class="section" id="nivel">
  <div class="container">
    <div class="plan-note reveal">
      {LEVEL}
    </div>
  </div>
</section>
"""

LEARN_TPL = """
      <article class="card tilt reveal" data-tilt>
        <div class="card-ico">{ICON}</div>
        <h3>{T}</h3>
        <p>{D}</p>
      </article>"""

SLOT_TPL = """
      <div class="day"><h3>{DAY}</h3><ul class="slots">{ITEM}</ul></div>"""
SLOT_ITEM = '<li><b>{T}</b><span>{N}</span></li>'

CTA = """
<section class="cta-band">
  <div class="container cta-inner reveal">
    <h2 class="cta-title">¿Listo para entrenar {NAME_SHORT}?</h2>
    <p class="cta-sub">Tu primera clase es gratis. Escríbenos por Instagram y reserva tu espacio en el tatami.</p>
    <div class="hero-actions">
      <a class="btn btn-gold" href="{IG}" target="_blank" rel="noopener">Escríbenos por Instagram</a>
      <a class="btn btn-ghost" href="../index.html#planes">Ver planes</a>
    </div>
  </div>
</section>
"""

FOOTER = """
<footer class="site-footer">
  <div class="container footer-inner">
    <div class="footer-brand">
      <img src="../assets/logo.jpg" alt="Kingsman logo" width="44" height="44">
      <div><b>KINGSMAN</b><small>Jiu Jitsu Studio</small></div>
    </div>
    <p class="footer-tag">El arte suave para todos. Oss.</p>
    <div class="footer-links">
      <a href="https://www.instagram.com/kingsmanjiujitsustudio/" target="_blank" rel="noopener">Instagram</a>
      <a href="../index.html#clases">Clases</a>
      <a href="../index.html#horarios">Horarios</a>
      <a href="../index.html#planes">Planes</a>
      <a href="../index.html#ubicacion">Ubicación</a>
    </div>
  </div>
  <p class="footer-copy">© <span class="yr">2026</span> Kingsman Jiu Jitsu Studio · Guayaquil, Ecuador</p>
</footer>

<!-- Dev A/B design toggle (development only) -->
<div class="dev-toggle" role="group" aria-label="Cambiar diseño de desarrollo">
  <span class="lbl">Diseño</span>
  <button type="button" data-theme-btn="a" aria-pressed="true">A · negro</button>
  <button type="button" data-theme-btn="b" aria-pressed="false">B · claro</button>
</div>

<script src="../animate.js"></script>
</body>
</html>
"""

CLASSES = [
    dict(slug="gi", name="GI — Kimono", name_short="con kimono",
         kicker="Clases · El arte suave en su forma más pura",
         lede="El kimono es el laboratorio donde se perfeccionan las palancas, los estrangulamientos y el juego de guardia. Técnica sobre fuerza, siempre.",
         intro="En GI entrenamos el arte suave con kimono. Es la base de todo el Brazilian Jiu Jitsu: agarres, control de mangas y piernas, y el juego de guardia clásico.",
         img="assets/photos/post03.jpg", imgalta="Entrenamiento de BJJ con kimono en Kingsman",
         chips="<span>Gi</span><span>Todos los niveles</span><span>Mié 17:00</span>",
         learn=[
            ("🥋", "Palancas y sumisiones", "Aprende las llaves clásicas: palanca de brazo, triángulo, estrangulaciones y más."),
            ("🧠", "Juego de guardia", "Desarrolla tu guardia y el control del agarre con el kimono como herramienta."),
            ("🛡️", "Defensa personal", "El GI te enseña a controlar al rival y a resolver situaciones de presión."),
         ],
         slots={"Lunes": [("17:00","BJJ Kids"),("18:00","BJJ Avanzado"),("19:00","Fundamentos")],
                "Martes": [("07:00","Clase privada"),("17:00","BJJ Kids"),("18:00","BJJ Avanzado"),("19:00","Fundamentos")],
                "Miércoles": [("17:00","No-Gi"),("18:00","No-Gi"),("19:00","No-Gi")],
                "Jueves": [("07:00","Clase privada"),("17:00","BJJ Kids"),("18:00","BJJ Avanzado"),("19:00","Fundamentos")],
                "Viernes": [("07:00","Clase privada"),("18:00","Open Mat")]},
         level="<p class='kicker'>Para quién</p><h4>¿Cuál es tu nivel?</h4><p>Tenemos espacio para todos: si nunca has pisado un tatami, empieza en Fundamentos; si ya compites, únete a Avanzado. No importa de dónde vengas, aquí creces.</p>",
         title="GI — Kimono", desc="Clases de Brazilian Jiu Jitsu con kimono en Guayaquil. Técnica sobre fuerza. Síguenos y escríbenos por Instagram."),
    dict(slug="no-gi", name="No-Gi — Sin kimono", name_short="sin kimono",
         kicker="Clases · Velocidad y control",
         lede="Sin tela que agarrar, el No-Gi exige una comprensión más profunda del cuerpo. El estilo más cercano al combate real.",
         intro="El No-Gi es velocidad, adaptabilidad y control. Sin kimono aprendes a leer el cuerpo, a luchar agarres codo y la transición constante entre posiciones.",
         img="assets/photos/post11.jpg", imgalta="Entrenamiento de No-Gi en Kingsman",
         chips="<span>No-Gi</span><span>Todos los niveles</span><span>Mié 17:00–20:00</span>",
         learn=[
            ("⚡", "Velocidad y fluidez", "Movimiento constante: pasadas de guardia, barridos y transiciones rápidas."),
            ("🦵", "Control del cuerpo", "Sin tela que agarrar, el control es técnico: agarres de brazo, pierna y cintura."),
            ("🥊", "Más cerca del combate", "El No-Gi es el estilo más cercano al combate real y a la defensa en el suelo."),
         ],
         slots={"Miércoles": [("17:00","No-Gi"),("18:00","No-Gi"),("19:00","No-Gi")]},
         level="<p class='kicker'>Para quién</p><h4>¿Cuál es tu nivel?</h4><p>El No-Gi funciona para todos los niveles. Ideal si quieres complementar tu GI o competir en la modalidad sin kimono.</p>",
         title="No-Gi — Sin kimono", desc="Clases de No-Gi (Jiu-Jitsu sin kimono) en Guayaquil. Velocidad y control. Escríbenos por Instagram."),
    dict(slug="kids", name="Kids", name_short="con tus hijos",
         kicker="Clases · El Jiu-Jitsu transforma por dentro",
         lede="Disciplina, respeto, confianza y la capacidad de resolver problemas bajo presión. El mejor regalo para un niño.",
         intro="En las clases infantiles los más pequeños aprenden a caer, a levantarse y a respetar, en un ambiente seguro y divertido que forja su carácter.",
         img="assets/photos/post06.jpg", imgalta="Clases de Jiu-Jitsu para niños en Kingsman",
         chips="<span>Kids</span><span>Niños y jóvenes</span><span>Lun · Mar · Jue 17:00</span>",
         learn=[
            ("👊", "Disciplina y respeto", "Valores que se entrenan con cada clase y se aplican en la vida."),
            ("🤸", "Coordinación y motricidad", "Movimiento, caídas controladas y el dominio del propio cuerpo."),
            ("🧩", "Resolver bajo presión", "El Jiu-Jitsu enseña calma e ingenio frente a los problemas."),
         ],
         slots={"Lunes": [("17:00","BJJ Kids")], "Martes": [("17:00","BJJ Kids")], "Jueves": [("17:00","BJJ Kids")]},
         level="<p class='kicker'>Para quién</p><h4>Programa infantil</h4><p>Para niños y jóvenes de todos los niveles. Un espacio donde se divierten mientras aprenden respeto, confianza y autocontrol.</p>",
         title="Kids — Jiu-Jitsu infantil", desc="Clases de Brazilian Jiu Jitsu para niños en Guayaquil. Disciplina, respeto y confianza. Escríbenos por Instagram."),
    dict(slug="fundamentos", name="Fundamentos", name_short="desde cero",
         kicker="Clases · El punto de partida de todo gran luchador",
         lede="Posiciones base, movimientos esenciales y la filosofía del Jiu-Jitsu desde cero, en un ambiente seguro y progresivo.",
         intro="Fundamentos es tu puerta de entrada al arte suave. Sin experiencia previa: aprenderás las posiciones, los movimientos clave y la filosofía que sostiene el Jiu-Jitsu.",
         img="assets/photos/post00.jpg", imgalta="El tatami de Kingsman, un buen lugar para empezar",
         chips="<span>Principiantes</span><span>Desde cero</span><span>Lun · Mar · Jue 19:00</span>",
         learn=[
            ("📍", "Posiciones base", "Guardia, montada, control lateral y la lógica de cada posición."),
            ("🔁", "Movimientos esenciales", "Los barridos y finalizaciones fundamentales del arte suave."),
            ("🧭", "La filosofía", "Aprender a caer, a respirar y a pensar bajo presión."),
         ],
         slots={"Lunes": [("19:00","Fundamentos")], "Martes": [("19:00","Fundamentos")], "Jueves": [("19:00","Fundamentos")]},
         level="<p class='kicker'>Para quién</p><h4>¿Nunca has entrenado?</h4><p>Perfecto, este es tu lugar. No necesitas experiencia ni equipamiento: solo ganas de aprender. Nosotros hacemos el resto.</p>",
         title="Fundamentos — Principiantes", desc="Clases de Fundamentos de Brazilian Jiu Jitsu en Guayaquil para principiantes. Sin experiencia previa. Escríbenos por Instagram."),
    dict(slug="privada", name="Clase privada", name_short="uno a uno",
         kicker="Clases · Entrenamiento uno a uno con el coach",
         lede="Acelera tu progreso y trabaja tus debilidades específicas con la atención completa del profesor.",
         intro="Las clases privadas son el camino más rápido para mejorar. Trabaja de forma individual con nuestro coach técnicas, acondicionamiento y estrategia a tu medida.",
         img="assets/photos/post05.jpg", imgalta="Entrenamiento personalizado en Kingsman",
         chips="<span>Uno a uno</span><span>Personalizado</span><span>Mar · Jue · Vie 07:00</span>",
         learn=[
            ("🎯", "Atención completa", "Todo el foco del profesor en ti, en cada repetición."),
            ("📈", "Avance acelerado", "Corrige errores y sube de nivel en la mitad del tiempo."),
            ("🩹", "Debilidades específicas", "Diseñamos trabajo para tu guardia, tu barrido o tu finalización favorita."),
         ],
         slots={"Martes": [("07:00","Clase privada")], "Jueves": [("07:00","Clase privada")], "Viernes": [("07:00","Clase privada")]},
         level="<p class='kicker'>Para quién</p><h4>¿Buscas resultados rápidos?</h4><p>Ideal para quien compite, para recuperar el ritmo o para comenzar con bases bien plantadas. Escríbenos para coordinar tu horario.</p>",
         title="Clase privada", desc="Entrenamiento personalizado uno a uno en Kingsman Jiu Jitsu Studio (Guayaquil). Acelera tu progreso. Escríbenos por Instagram."),
    dict(slug="open-mat", name="Open Mat", name_short="rodaje libre",
         kicker="Clases · El día de la comunidad",
         lede="Rodaje libre para todos los niveles. Ven a practicar y a compartir con la comunidad del tatami.",
         intro="El Open Mat es el espacio para rodar libre: prueba lo aprendido, conoce compañeros y disfruta el arte suave sin estructura de clase.",
         img="assets/photos/post10.jpg", imgalta="Open Mat y comunidad en Kingsman",
         chips="<span>Rodaje libre</span><span>Todos los niveles</span><span>Viernes 18:00</span>",
         learn=[
            ("🤝", "Rodar con la comunidad", "Encuentra compañeros de tu nivel y de niveles superiores."),
            ("🧪", "Probar lo aprendido", "El mejor laboratorio para pulir tu técnica en situación real."),
            ("😌", "Sin presión", "Sin estructura, sin marcador: un espacio para disfrutar el arte."),
         ],
         slots={"Viernes": [("18:00","Open Mat")]},
         level="<p class='kicker'>Para quién</p><h4>¿Quieres rodar sin estructura?</h4><p>Abierto a todos los niveles de la academia. Ven cuando quieras: el tatami te espera.</p>",
         title="Open Mat", desc="Open Mat semanal en Kingsman Jiu Jitsu Studio (Guayaquil). Rodaje libre para todos los niveles. Escríbenos por Instagram."),
]


def chips_tag(chips):
    return "".join(chips)


def build_slots(daymap):
    out = ""
    for day, items in daymap.items():
        li = "".join(SLOT_ITEM.format(T=t, N=n) for (t, n) in items)
        out += SLOT_TPL.format(DAY=day, ITEM=li)
    return out


def build_learn(cards):
    return "".join(LEARN_TPL.format(ICON=i, T=t, D=d) for (i, t, d) in cards)


def page(c):
    body = HERO
    body += BODY_CORE
    body += CTA
    body += FOOTER
    # HEAD carries literal { } in its inline FOUC-guard JS, so use .replace here
    head = HEAD.replace("{TITLE}", c["title"]).replace("{DESC}", c["desc"]).replace("{SLUG}", c["slug"])
    html = head + (NAV + body).format(
        TITLE=c["title"], DESC=c["desc"], SLUG=c["slug"], IG=IG,
        KICKER=c["kicker"], NAME=c["name"], LEDE=c["lede"], IMG=c["img"],
        IMGALT=c["imgalta"], CHIPS=c["chips"], INTRO=c["intro"],
        LEARN=build_learn(c["learn"]), NAME_SLOT=c["name"], SLOTS=build_slots(c["slots"]),
        LEVEL=c["level"], NAME_SHORT=c["name_short"],
    )
    # Class pages live one dir deeper (/pages/clases/), so every root-relative
    # path needs "../../" — rewrite the one-level prefixes we used in templates.
    html = (html.replace('"../style.css"', '"../../style.css"')
                .replace('"../animate.js"', '"../../animate.js"')
                .replace('"../assets/', '"../../assets/')
                .replace('"../index.html', '"../../index.html'))
    return html


def main():
    os.makedirs(OUT, exist_ok=True)
    for c in CLASSES:
        path = os.path.join(OUT, c["slug"] + ".html")
        with open(path, "w") as f:
            f.write(page(c))
        print("wrote", path)
    print("Done: %d class pages" % len(CLASSES))


if __name__ == "__main__":
    main()