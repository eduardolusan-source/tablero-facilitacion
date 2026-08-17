# Tablero de diagnóstico de facilitación

Herramienta personal de Eduardo Luna Sánchez (UAQ, Campus Concá) para diagnosticar una sesión antes
de diseñarla, y armar con ese diagnóstico un encargo bien redactado para el skill de facilitación.

**No se conecta a nada.** Es un solo archivo HTML sin dependencias ni red: el borrador, los grupos y
el historial viven en el navegador de quien lo abre, y nada sale de ahí. No hay analítica, no hay
servidor, no hay base de datos.

- Página: https://eduardolusan-source.github.io/tablero-facilitacion/
- Archivo local equivalente: `index.html` (funciona igual abriéndolo con doble clic).

## Qué hace

- **Diseñar** — cuatro modos (sesión nueva, rediseñar una reunión que no funciona, conversación
  difícil o mediación, evaluar una sesión que ya pasó). Arma el encargo en vivo, omite lo vacío y
  agrega instrucciones condicionales según el caso (escolaridad diversa, agravios históricos, campo,
  sesión larga, proceso de varias sesiones).
- **Grupos** — lo que no cambia entre sesiones (quiénes son, lugar, materiales, voces que quedan
  fuera, historia previa) se guarda una vez por grupo y se reusa.
- **Banco** — las 79 técnicas con filtros por propósito, fase del rombo, tamaño, tiempo, "sin
  escritura" y "requiere moverse".
- **Guía por función** — las mismas 79 agrupadas por lo que resuelven, con lente para clase.
- **Historial** — encargos guardados, evaluación de una sesión ya diseñada, y respaldo completo en
  un `.json`.

## Regenerar el catálogo

El Banco y la Guía se generan de las fichas del skill de facilitación, que **no** viven en este repo:

```bash
python3 generar-catalogo.py /ruta/a/skill-facilitacion/references/estructuras --html index.html
```

Lee de cada ficha la línea `Tiempo: … | Grupo: … | Tipo: …` y la sección `## Para qué sirve`, y
reescribe el bloque entre las marcas `CATALOGO_INICIO` / `CATALOGO_FIN` del HTML.

## Créditos y licencia

Las estructuras 01–43 provienen de Liberating Structures (Lipmanowicz & McCandless), licencia
**CC BY-SA 4.0**; las descripciones derivadas de ellas se comparten bajo la misma licencia. Las
técnicas 44–79 son resúmenes en palabras propias de ideas de *The Art of Gathering* (Parker),
*Gamestorming* (Gray, Brown & Macanufo), *Facilitator's Guide to Participatory Decision-Making*
(Kaner et al.), *The Art of Focused Conversation* (ICA), *Sitting in the Fire* (Mindell),
*Community* (Block), *Holding Change* (adrienne maree brown) y *80 herramientas para el desarrollo
participativo* (Geilfus, IICA — obra de libre reproducción citando al autor), *Técnicas participativas
para la educación popular* (Vargas y Bustillos, Alforja/CIDE) y *Training for Transformation* (Hope y
Timmel). Este repositorio
contiene solo una línea descriptiva por técnica, no el contenido de las fichas ni de los libros.
