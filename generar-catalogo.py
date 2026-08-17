#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el catálogo del Banco de tablero-facilitacion.html a partir de las fichas
reales del skill `facilitacion` (references/estructuras/*.md).

Uso:
    python3 generar-catalogo.py [CARPETA_CON_FICHAS] [--html tablero-facilitacion.html]

- Toma nombres, números y fuentes de la semilla de abajo (verificada contra
  references/indice.md y references/fundamentos/matchmaker.md).
- De cada ficha lee la línea "Tiempo: … | Grupo: … | Tipo: …" y el primer
  párrafo de "## Para qué sirve", y con eso sobrescribe la semilla.
- Escribe catalogo-facilitacion.json y, si encuentra el HTML, reemplaza el
  bloque entre las marcas CATALOGO_INICIO / CATALOGO_FIN.

Las fichas se reconocen por el número al inicio del nombre de archivo
(01-…, 64…, 69…, con o sin guion).
"""
import json, re, sys, unicodedata
from pathlib import Path

LS = "Liberating Structures"
PK = "Parker"
GS = "Gamestorming"
EP = "Alforja / educación popular"
HT = "Hope y Timmel"

# n, nombre, fuente, tipo, propósitos, fases, gMin, gMax, minMin, minMax, escritura, movimiento, para qué sirve
SEMILLA = [
 (1,"1-2-4-Todos (1-2-4-All)",LS,"apertura / desarrollo",["abrir ideas de todas las voces"],["divergente","convergente"],2,None,12,15,False,False,"Involucra a todas las personas a la vez en generar preguntas, ideas y sugerencias: a solas, en pareja, en cuarteto y al pleno."),
 (2,"Redes improvisadas (Impromptu Networking)",LS,"apertura",["conectar al arrancar"],["divergente"],8,None,20,20,False,True,"Comparte retos y expectativas en rondas rápidas de dos: teje red y confianza en minutos."),
 (3,"Nueve porqués (9 Whys)",LS,"apertura / desarrollo",["aclarar el propósito"],["divergente"],5,None,20,20,False,False,"Encuentra el propósito profundo de un trabajo preguntando por qué importa, una y otra vez."),
 (4,"Preguntas endiabladas (Wicked Questions)",LS,"desarrollo",["nombrar tensiones y paradojas"],["gemido"],5,None,25,40,True,False,"Formula las paradojas que el grupo tiene que sostener a la vez, en vez de resolverlas de un solo lado."),
 (5,"Entrevistas apreciativas (Appreciative Interviews)",LS,"apertura / desarrollo",["descubrir lo que ya funciona"],["divergente"],5,None,40,60,False,False,"Descubre y difunde los éxitos que el grupo ya tiene, a partir de historias contadas en parejas."),
 (6,"Destrucción creativa (TRIZ)",LS,"desarrollo",["dejar de hacer lo contraproducente"],["divergente","gemido"],5,None,35,35,False,False,"Vuelve visible y detenible lo contraproducente: primero se inventa el peor resultado posible."),
 (7,"Soluciones del 15% (15% Solutions)",LS,"cierre",["pasar a la acción"],["cierre"],3,None,15,20,False,False,"Encuentra qué puede hacer cada quien con su propio poder y recursos, sin pedirle permiso a nadie."),
 (8,"Consultoría Troika (Troika Consulting)",LS,"desarrollo",["ayuda entre pares"],["gemido","convergente"],3,None,25,35,False,False,"Cada persona recibe ayuda práctica de otras dos sobre un reto propio, en rondas de consulta."),
 (9,"Qué / Y qué / Ahora qué (W³)",LS,"cierre",["analizar o cerrar una sesión","pasar a la acción"],["convergente","cierre"],5,None,25,70,False,False,"Lee juntos lo que pasó, qué significa y qué sigue, separando los hechos de las interpretaciones."),
 (10,"Diálogo de descubrimiento y acción (DAD)",LS,"desarrollo",["descubrir lo que ya funciona"],["divergente"],5,None,25,70,False,False,"Descubre las prácticas que ya funcionan dentro del propio grupo y desata su difusión."),
 (11,"Cambia y comparte (Shift & Share)",LS,"desarrollo",["difundir innovaciones internas"],["divergente"],10,None,45,90,False,True,"Difunde el trabajo de varias personas en estaciones cortas y simultáneas, sin presentaciones al pleno."),
 (12,"25/10 Cosecha de ideas (25/10 Crowdsourcing)",LS,"desarrollo / cierre",["abrir ideas de todas las voces","priorizar"],["divergente","convergente"],12,None,30,30,True,True,"Genera ideas audaces y deja que el propio grupo elija las mejores puntuándolas mientras circulan."),
 (13,"Multitudes sabias (Wise Crowds)",LS,"desarrollo",["ayuda entre pares"],["gemido","convergente"],4,None,45,75,False,False,"Convierte al grupo en consultor de una persona a la vez, con quien consulta escuchando en silencio."),
 (14,"Especificaciones mínimas (Min Specs)",LS,"desarrollo / cierre",["priorizar"],["convergente"],5,None,35,50,True,False,"Reduce las reglas a las imprescindibles para dejar la mayor libertad posible de acción."),
 (15,"Prototipos de improvisación (Improv Prototyping)",LS,"desarrollo",["difundir innovaciones internas"],["divergente"],5,None,35,70,False,True,"Ensaya en escena las respuestas a situaciones difíciles hasta encontrar las que sí funcionan."),
 (16,"Heurísticas de ayuda (Helping Heuristics)",LS,"desarrollo",["ayuda entre pares"],["divergente"],5,None,25,45,False,False,"Practica cuatro maneras de ayudar y descubre cuál abre la conversación y cuál la cierra."),
 (17,"Café de conversación (Conversation Café)",LS,"desarrollo",["conversación profunda sin debate"],["gemido"],5,None,40,70,False,False,"Da sentido a un tema difícil en rondas con objeto de palabra, sin discusión cruzada ni debate."),
 (18,"Pecera de experiencia (User Experience Fishbowl)",LS,"desarrollo",["difundir innovaciones internas"],["divergente"],10,None,45,90,False,True,"El grupo escucha a quienes ya vivieron la experiencia conversar entre sí, y luego les pregunta."),
 (19,"Escuchado, visto, respetado (HSR)",LS,"apertura / desarrollo",["conectar al arrancar","duelo o transición difícil"],["gemido"],5,None,25,45,False,False,"Practica la escucha profunda en parejas a partir de una experiencia de no haber sido escuchado."),
 (20,"Dibujar juntos (Drawing Together)",LS,"desarrollo",["conversación profunda sin debate"],["divergente","gemido"],5,None,40,40,False,False,"Revela intuiciones y sentidos que no salen con palabras, dibujando con cinco símbolos simples."),
 (21,"Guion gráfico del diseño (Design Storyboards)",LS,"desarrollo / cierre",["diseñar la propia reunión"],["convergente"],5,None,35,70,True,False,"Arma paso a paso la secuencia de una sesión o un proceso, con tiempos y responsables."),
 (22,"Entrevista al invitado (Celebrity Interview)",LS,"apertura / desarrollo",["difundir innovaciones internas"],["divergente"],10,None,30,60,False,False,"Convierte la ponencia de una autoridad o experta en una entrevista útil y cercana al grupo."),
 (23,"Tejido de redes sociales (Social Network Webbing)",LS,"desarrollo",["coordinarse entre áreas o actores","mapear actores"],["divergente","convergente"],5,None,60,70,True,False,"Dibuja quién conoce a quién para ver de dónde puede venir el apoyo que hace falta."),
 (24,"Lo que necesito de ti (What I Need From You)",LS,"desarrollo",["coordinarse entre áreas o actores"],["convergente"],7,60,55,70,False,False,"Cada función pide en voz alta lo que necesita de las otras y recibe respuesta clara: sí, no, lo intentaré."),
 (25,"Plaza de opciones (Options Place / Open Space)",LS,"desarrollo",["agenda construida por los participantes"],["divergente"],5,None,90,180,True,True,"Deja que las personas convoquen y conduzcan las sesiones sobre lo que de verdad les importa."),
 (26,"Relaciones generativas STAR",LS,"desarrollo",["nombrar tensiones y paradojas"],["gemido"],5,None,30,60,True,False,"Evalúa la calidad de las relaciones del grupo y muestra dónde puede surgir lo nuevo."),
 (27,"Matriz de acuerdo y certeza (Agreement & Certainty)",LS,"desarrollo",["nombrar tensiones y paradojas","priorizar"],["convergente"],5,None,25,40,True,True,"Ordena los retos en simples, complicados, complejos o caóticos para elegir cómo abordarlos."),
 (28,"Etnografía simple (Simple Ethnography)",LS,"desarrollo",["descubrir lo que ya funciona"],["divergente"],5,None,60,120,True,True,"Observa de cerca lo que la gente hace de verdad, no lo que dice que hace."),
 (29,"Autonomía integrada (Integrated~Autonomy)",LS,"desarrollo",["nombrar tensiones y paradojas"],["gemido"],5,None,40,60,True,False,"Sale del «o esto o aquello» encontrando cómo conviven lo común y lo autónomo."),
 (30,"Incertidumbres críticas (Critical Uncertainties)",LS,"desarrollo",["estrategia ante incertidumbre"],["convergente"],5,None,55,80,True,False,"Prepara estrategias que sirvan en varios futuros posibles, no solo en el que esperamos."),
 (31,"Planeación por ecociclo (Ecocycle Planning)",LS,"desarrollo",["dejar de hacer lo contraproducente","estrategia ante incertidumbre"],["convergente"],5,None,60,95,True,True,"Ubica cada actividad en su ciclo de vida para ver qué crece, qué estorba y qué conviene soltar."),
 (32,"Panarquía (Panarchy)",LS,"desarrollo",["estrategia ante incertidumbre"],["gemido"],5,None,60,90,True,False,"Mira cómo se influyen los cambios en distintas escalas, del grupo a la región."),
 (33,"Del propósito a la práctica (Purpose-to-Practice)",LS,"desarrollo",["aclarar el propósito","estrategia ante incertidumbre"],["convergente"],5,None,90,180,True,False,"Define los cinco elementos que hacen viable una iniciativa: propósito, principios, participantes, estructura y prácticas."),
 (34,"Té loco / Té en calma (Mad Tea | Calm Tea)",LS,"apertura",["abrir ideas de todas las voces","conectar al arrancar"],["divergente"],10,None,15,25,False,True,"Rondas rapidísimas en dos círculos completando frases: destapa lo que el grupo trae, con energía."),
 (35,"Diario en espiral (Spiral Journal)",LS,"cierre",["analizar o cerrar una sesión"],["convergente","cierre"],1,None,20,40,True,False,"Reflexión individual en capas para asentar lo vivido antes de compartirlo."),
 (36,"Espectrograma plegable (Folding Spectrogram)",LS,"desarrollo",["conversación profunda sin debate"],["gemido"],8,None,30,50,False,True,"El grupo se ubica físicamente en una línea de posturas y luego la dobla para que los extremos se escuchen."),
 (37,"Chisme positivo (Positive Gossip)",LS,"apertura",["conectar al arrancar"],["divergente"],6,None,20,30,False,True,"Las personas hablan bien unas de otras en tercera persona: calienta al grupo y construye reconocimiento."),
 (38,"Caminata de principios (Principles Walk-Around)",LS,"desarrollo",["aclarar el propósito"],["convergente"],5,None,30,60,True,True,"El grupo camina entre los principios propuestos y los depura hasta dejar los que de verdad guían."),
 (39,"Patrones de relación en la red (Network Relationship Patterns)",LS,"desarrollo",["coordinarse entre áreas o actores"],["divergente","gemido"],5,None,45,90,True,False,"Hace visibles los patrones de vínculo de una red para ver dónde falta conexión."),
 (40,"Caminar el duelo (Grief Walking)",LS,"desarrollo",["duelo o transición difícil"],["gemido"],4,None,45,90,False,True,"Acompaña a un grupo que perdió algo importante; se usa con extremo cuidado y tiempo suficiente."),
 (41,"Futuro~Presente (Future~Present)",LS,"desarrollo",["estrategia ante incertidumbre","visión de futuro"],["convergente"],5,None,45,90,True,False,"Trabaja desde el futuro deseado hacia el presente para encontrar los primeros pasos."),
 (42,"Hablar con los duendes (Talking with Pixies)",LS,"desarrollo",["nombrar tensiones y paradojas"],["gemido"],4,None,30,60,False,False,"Da voz a lo que el grupo se calla a sí mismo y lo pone sobre la mesa sin culpables."),
 (43,"Desanudar la estrategia (Strategy Knotworking)",LS,"desarrollo",["estrategia ante incertidumbre"],["convergente"],5,None,60,120,True,False,"Desata los nudos que traban una estrategia, uno por uno, con el grupo entero."),
 (44,"Brindis con historia (15 Toasts)",PK,"apertura",["conectar al arrancar"],["divergente"],6,30,30,60,False,False,"Cada persona brinda con una historia sobre un mismo tema: abre autenticidad y confianza en grupos formales o jerárquicos."),
 (45,"Cuaderno previo (workbook)",PK,"antes de la sesión",["conectar al arrancar"],["divergente"],1,None,None,None,True,False,"Prepara al grupo antes de llegar (priming): unas preguntas que ya ponen a pensar. Versión mínima: una pregunta en la invitación."),
 (46,"Presentaciones cruzadas",PK,"apertura",["conectar al arrancar"],["divergente"],6,40,20,40,False,True,"Cada quien presenta a otra persona: honra a los presentes y funde dos grupos que no se conocen, sin ronda sosa."),
 (47,"Combate ritual de posturas (cage match)",PK,"desarrollo",["nombrar tensiones y paradojas"],["gemido"],8,None,45,90,False,False,"Litiga con reglas y en escena la decisión que el grupo evita: buena controversia, sin herida profunda."),
 (48,"Mapa de calor y reglas base",PK,"desarrollo",["conflicto profundo"],["gemido"],5,None,30,60,True,False,"Ubica de antemano qué temas queman y con qué reglas se van a tocar: prepara conversaciones difíciles."),
 (49,"Cierre en dos tiempos",PK,"cierre",["analizar o cerrar una sesión"],["cierre"],3,None,15,30,False,False,"Cierra hacia adentro (qué significó) y hacia afuera (qué sigue), para terminar de verdad."),
 (50,"Lluvia silenciosa y mapa de afinidad",GS,"desarrollo",["abrir ideas de todas las voces"],["divergente","convergente"],4,40,30,60,True,True,"Genera muchas ideas en silencio y las agrupa en patrones que el grupo nombra."),
 (51,"Votación con puntos (Dot Voting)",GS,"cierre / decisión",["priorizar"],["convergente"],4,100,10,20,False,True,"Prioriza entre muchas opciones de forma transparente. Variantes: $100, ranking forzado."),
 (52,"Matriz impacto-esfuerzo (+ quién/qué/cuándo)",GS,"cierre",["pasar a la acción","planear con responsables"],["convergente","cierre"],4,30,30,60,True,True,"Aterriza las ideas en acciones comprometidas con responsable y fecha."),
 (53,"Portada del futuro (Cover Story)",GS,"desarrollo",["visión de futuro"],["divergente"],5,30,45,90,True,False,"Dibuja el futuro ideal ya cumplido, como portada de revista, para construir visión compartida."),
 (54,"Lancha y anclas (Speedboat)",GS,"desarrollo",["nombrar tensiones y paradojas"],["divergente","gemido"],4,30,30,60,True,False,"Nombra obstáculos sin señalar culpables. Variante: campo de fuerzas."),
 (55,"Pre-mortem",GS,"desarrollo",["ver riesgos"],["convergente"],4,30,30,60,True,False,"Imagina que el proyecto ya fracasó y pregunta por qué: los riesgos salen al arrancar, no al final."),
 (56,"Mapa de actores (Stakeholder Analysis)",GS,"desarrollo",["mapear actores"],["divergente","convergente"],4,30,45,90,True,False,"Ubica a quién importa por poder e interés y define cómo involucrar a cada quien."),
 (57,"Café del mundo (World Café)",GS,"desarrollo",["conversación profunda sin debate"],["divergente","gemido"],12,None,60,120,True,True,"Conversación profunda en grupos grandes con polinización cruzada entre mesas."),
 (58,"Escala de grados de acuerdo (Gradients of Agreement)","Kaner","cierre / decisión",["medir el acuerdo"],["convergente","cierre"],4,60,15,40,False,False,"Mide el apoyo real a una propuesta en una escala, y pacta la regla de decisión antes de cerrar."),
 (59,"Conversación enfocada (ORID)","ORID / ICA","desarrollo / cierre",["analizar o cerrar una sesión"],["convergente","cierre"],2,None,30,60,False,False,"Procesa cualquier experiencia por los cuatro niveles: datos, reacciones, significado y decisión."),
 (60,"Proceso grupal de voces","Mindell","desarrollo",["conflicto profundo"],["gemido"],5,None,60,180,False,True,"Conflicto profundo: hablar desde los roles del campo, dar voz a los fantasmas, sostener los puntos calientes. Leer antes fundamentos/mindell-fuego.md."),
 (61,"Las seis conversaciones","Block","desarrollo",["construir pertenencia"],["divergente","gemido"],3,12,30,None,False,True,"Invitación, posibilidad, propiedad, disenso, compromiso y dones: convierte a asistentes en dueños de su comunidad."),
 (62,"Mediación interdependiente","adrienne maree brown","desarrollo",["conflicto entre personas"],["gemido"],2,6,90,None,False,False,"Conflicto entre dos o pocas personas dentro de un colectivo: escucha verificada, petición/ofrecimiento/disculpa, acuerdos o límites."),
 (63,"Equipos de cuidado por elementos (Care Bears)","adrienne maree brown","apoyo",["cuidado del grupo"],["divergente","gemido","convergente","cierre"],12,None,10,None,False,True,"Reparte el cuidado del espacio en encuentros largos: tierra, aire, fuego y agua."),
 (64,"Mapas parlantes","Geilfus / DRP","diagnóstico rural",["diagnóstico del territorio"],["divergente"],8,10,60,180,False,True,"Diagnóstico visual del territorio y de la comunidad, sin leer ni escribir. Variantes: mapa social, de recursos, de servicios, diagrama de cuenca."),
 (65,"Caminata y diagrama de corte (transecto)","Geilfus / DRP","diagnóstico rural",["diagnóstico del territorio"],["divergente"],3,5,120,240,False,True,"Diagnóstico caminando el territorio, con acceso a recursos y cambios históricos."),
 (66,"Priorización por pares y árbol de problemas","Geilfus / DRP","análisis",["priorizar"],["convergente"],8,30,60,180,False,False,"Separa el problema de sus causas y ordena por importancia comparando de dos en dos."),
 (67,"Soluciones locales primero","Geilfus / DRP","análisis",["descubrir lo que ya funciona"],["divergente","convergente"],8,30,60,180,False,False,"Encuentra y evalúa lo que la comunidad ya ha probado antes de traer soluciones de fuera. Incluye FODA participativo."),
 (68,"Mapa de ordenamiento, plan de acción y responsabilidades","Geilfus / DRP","planificación",["planear con responsables","pasar a la acción"],["convergente","cierre"],10,40,120,180,False,True,"Del acuerdo al quién hace qué, cuándo y con qué recursos, con el reparto realista frente a las instituciones."),
 (69,"Calendarios estacionales y reloj de uso del tiempo","Geilfus / DRP","diagnóstico rural",["diagnóstico del territorio"],["divergente","convergente"],6,15,60,120,False,False,"Estacionalidad, carga de trabajo y enfoque de género: cuándo pasan las cosas y quién carga el trabajo."),
 (70,"Sociodrama y juego de roles",EP,"técnicas con actuación",["representar para analizar"],["divergente","gemido"],8,40,45,90,False,True,"Poner en escena un hecho real del grupo para poder mirarlo desde afuera y analizarlo entre todos."),
 (71,"Dinámicas de animación y presentación",EP,"animación",["conectar al arrancar"],["divergente"],8,40,10,30,False,True,"Crear ambiente de confianza, presentarse y recuperar la energía del grupo."),
 (72,"El rumor y otros ejercicios de comunicación",EP,"comunicación",["aprender a comunicarse"],["divergente"],8,40,30,60,False,False,"Hacer visible cómo se distorsiona un mensaje y por qué la comunicación de una sola vía es peor."),
 (73,"Ejercicios de abstracción y síntesis",EP,"abstracción",["practicar la síntesis"],["divergente","convergente"],5,40,15,45,True,False,"Ejercitar el resumen, la asociación de conceptos y la distinción entre hecho e interpretación."),
 (74,"La baraja de la planificación",EP,"organización y planificación",["planear con responsables"],["convergente"],8,40,60,90,True,False,"Descubrir jugando cuáles son los pasos de una planificación y en qué orden van."),
 (75,"Vivencias sobre la organización",EP,"organización y planificación",["sentir la organización"],["divergente","gemido"],10,40,45,75,False,True,"Sentir en el cuerpo la diferencia entre la acción espontánea y la acción organizada."),
 (76,"El afiche y la lectura colectiva de imágenes",EP,"análisis con imágenes",["leer imágenes y símbolos","conversación profunda sin debate"],["divergente","gemido"],8,40,60,90,False,False,"Decir en símbolos lo que no se puede decir en argumentos, y descodificarlo entre todos."),
 (77,"Evaluación participativa",HT,"evaluación",["evaluar un proceso largo","analizar o cerrar una sesión"],["convergente","cierre"],10,40,240,None,True,False,"Que el propio grupo evalúe su programa, con sus preguntas e indicadores, y se quede con la información."),
 (78,"Evaluación rápida de un taller",HT,"evaluación",["analizar o cerrar una sesión"],["cierre"],5,40,15,60,True,False,"Ajustar un taller mientras todavía se puede, y cerrarlo aprendiendo."),
 (79,"Valoración de impacto a tres niveles",HT,"evaluación",["evaluar un proceso largo"],["convergente","cierre"],6,30,240,None,True,False,"Valorar qué cambió de verdad en las personas, en la organización y en la comunidad tras años de trabajo."),
]

CAMPOS = ["n","nombre","archivo","fuente","tipo","proposito","fase","grupoMin","grupoMax",
          "minutosMin","minutosMax","requiereEscritura","requiereMovimiento","paraQueSirve",
          "tiempoTexto","grupoTexto"]

def base():
    fichas = {}
    for (n,nombre,fuente,tipo,prop,fase,gmin,gmax,mmin,mmax,esc,mov,para) in SEMILLA:
        fichas[n] = dict(n=n, nombre=nombre, archivo=None, fuente=fuente, tipo=tipo,
                         proposito=prop, fase=fase, grupoMin=gmin, grupoMax=gmax,
                         minutosMin=mmin, minutosMax=mmax, requiereEscritura=esc,
                         requiereMovimiento=mov, paraQueSirve=para,
                         tiempoTexto=None, grupoTexto=None)
    return fichas

def a_minutos(txt):
    """Devuelve (min, max) en minutos a partir de la línea «Tiempo: …» de la ficha."""
    t = txt.replace("–", "-").replace("—", "-").lower()
    vals = []
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*(?:-\s*(\d+(?:[.,]\d+)?)\s*)?(h(?:oras?)?|min|minutos?)", t):
        a = float(m.group(1).replace(",", "."))
        b = float(m.group(2).replace(",", ".")) if m.group(2) else a
        factor = 60 if m.group(3).startswith("h") else 1
        vals += [a * factor, b * factor]
    if "medio día" in t: vals += [240]
    if "día completo" in t or "todo el día" in t: vals += [480]
    if not vals: return (None, None)
    abierto = any(p in t for p in ["varias sesiones", "varios días", "varias horas", "meses",
                                   "proceso de", "según", "todo el evento", "+"])
    # el primer rango de la línea manda para el mínimo; el máximo es el mayor de la línea
    return (int(vals[0]), None if abierto else int(max(vals)))

def a_grupo(txt):
    t = txt.replace("–", "-").replace("—", "-")
    t = re.sub(r"(\d)\s*(?:a|hasta)\s*(\d)", r"\1-\2", t)  # "10 a 300" → "10-300"
    # si la ficha escala con grupos en paralelo, el máximo no es tope de la sesión
    escala = any(p in t.lower() for p in ["paralelo", "por mapa", "por círculo", "por grupo",
                                          "por mesa", "mesas de", "escalable", "en equipos de",
                                          "subgrupo", "cualquier tamaño", "cualquiera"])
    tope = re.match(r"\s*(hasta|máximo|max\.?)\b", t, re.I)  # "hasta 15-20": no hay mínimo
    m = re.search(r"(\d+)\s*-\s*(\d+)\s*(\+)?", t)
    if m:
        gmax = None if (m.group(3) or escala) else int(m.group(2))
        return (None if tope else int(m.group(1)), gmax)
    m = re.search(r"(\d+)\s*(\+|o más)", t)
    if m: return (int(m.group(1)), None)
    m = re.search(r"(\d+)", t)
    return (int(m.group(1)), None) if m else (None, None)

CONECTORES = ("y", "o", "e", "u", "que", "con", "de", "del", "en", "para", "por", "a", "al",
              "como", "pero", "sin", "sobre", "la", "el", "los", "las", "un", "una")

def recortar(p, limite=230):
    """Corta en frase completa; si no se puede, en palabra limpia y con puntos suspensivos."""
    p = re.sub(r"\*\*(.+?)\*\*", r"\1", p).strip()
    if len(p) <= limite: return p
    corte = p[:limite]
    punto = corte.rfind(". ")
    if punto > 90:
        return corte[:punto + 1].strip()
    palabras = corte.rstrip().split(" ")[:-1]          # la última suele venir partida
    while palabras and (palabras[-1].lower().strip(",;:—-") in CONECTORES
                        or palabras[-1] in (",", ";", ":", "—")):
        palabras.pop()
    return " ".join(palabras).rstrip(" ,;:—-") + "…"

def leer_ficha(ruta):
    txt = ruta.read_text(encoding="utf-8")
    lineas = txt.split("\n")
    datos = {"archivo": ruta.name}
    if lineas and lineas[0].startswith("#"):
        datos["nombreFicha"] = lineas[0].lstrip("# ").strip()
    cab = next((l for l in lineas[:6] if "Tiempo:" in l and "Grupo:" in l), None)
    if cab:
        partes = dict()
        for trozo in cab.split("|"):
            if ":" in trozo:
                k, v = trozo.split(":", 1)
                partes[k.strip().lower()] = v.strip()
        if "tiempo" in partes:
            datos["tiempoTexto"] = partes["tiempo"]
            datos["minutosMin"], datos["minutosMax"] = a_minutos(partes["tiempo"])
        if "grupo" in partes:
            datos["grupoTexto"] = partes["grupo"]
            datos["grupoMin"], datos["grupoMax"] = a_grupo(partes["grupo"])
        if "tipo" in partes:
            datos["tipo"] = partes["tipo"]
    m = re.search(r"##\s*Para qué sirve\s*\n+(.+?)(?:\n\s*\n|\n##)", txt, re.S)
    if m:
        datos["paraQueSirve"] = recortar(" ".join(m.group(1).split()))
    cuerpo = txt.lower()
    if re.search(r"sin (necesidad de )?(leer|escribir)|no requiere (leer|escribir|saber)|sin escritura|no saben leer", cuerpo):
        datos["requiereEscritura"] = False
    if re.search(r"camina|de pie|se levantan|estaciones|círculo de pie|recorrido|moverse", cuerpo):
        datos["requiereMovimiento"] = True
    return datos

def numero_de(ruta):
    m = re.match(r"(\d{1,2})", ruta.stem)
    return int(m.group(1)) if m else None

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    carpeta = Path(args[0]) if args else Path(".")
    html = None
    if "--html" in sys.argv:
        html = Path(sys.argv[sys.argv.index("--html") + 1])
    elif (carpeta / "tablero-facilitacion.html").exists():
        html = carpeta / "tablero-facilitacion.html"
    elif Path("tablero-facilitacion.html").exists():
        html = Path("tablero-facilitacion.html")

    fichas = base()
    leidas = []
    for ruta in sorted(carpeta.rglob("*.md")):
        n = numero_de(ruta)
        if n is None or n not in fichas: continue
        datos = leer_ficha(ruta)
        if datos.pop("nombreFicha", None):
            datos["nombre"] = leer_ficha(ruta)["nombreFicha"]
        if not re.match(r"\d{2}-", ruta.name):
            datos["archivo"] = None
        fichas[n].update(datos)
        leidas.append(n)
    catalogo = [fichas[n] for n in sorted(fichas)]

    salida = carpeta / "catalogo-facilitacion.json"
    salida.write_text(json.dumps(catalogo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(catalogo)} técnicas · {len(set(leidas))} con datos leídos de su ficha "
          f"({', '.join(str(x) for x in sorted(set(leidas))) or 'ninguna'})")
    print(f"→ {salida}")

    if html and html.exists():
        js = "const CATALOGO_BASE = " + json.dumps(catalogo, ensure_ascii=False, indent=0).replace("\n", "") + ";"
        js = re.sub(r'(?<=[,{])"', '\n  "', js, count=0) if False else js
        contenido = html.read_text(encoding="utf-8")
        nuevo, hechos = re.subn(r"/\* CATALOGO_INICIO \*/.*?/\* CATALOGO_FIN \*/",
                                "/* CATALOGO_INICIO */\n" + js + "\n/* CATALOGO_FIN */",
                                contenido, flags=re.S)
        if hechos:
            html.write_text(nuevo, encoding="utf-8")
            print(f"→ catálogo embebido en {html}")
        else:
            print(f"! no encontré las marcas CATALOGO_INICIO/FIN en {html}; usa «Importar catálogo .json».")

if __name__ == "__main__":
    main()
