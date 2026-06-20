# Atlasmancer v0.4 "Geography Engine" — Especificación

Estado: propuesta para implementación
Autor del diseño: planificación/producto/narrativa (no código)
Implementación: Codex
Precondición: v0.2 Foundation y v0.3 Campaign Pack cerrados completos
Referencia previa: [`docs/ROADMAP.md`](ROADMAP.md) "Fase 3: Mundo geografico coherente" y release "v0.4 Geography Engine"

---

## 0. Qué es v0.4 en una frase

> El terreno ya existe (elevación, humedad, biomas, ríos); lo que falta es agruparlo en **regiones con nombre propio, bioma dominante y descripción** — convirtiendo el array `regions[]` de `campaign.json`, vacío desde v0.2, en algo real.

---

## 1. Visión de v0.4 — y una decisión de alcance que me aparto del roadmap literal

`docs/ROADMAP.md` describe la Fase 3 con dos cosas mezcladas: (a) biomas/regiones con lógica real, y (b) una arquitectura de **chunks** para mapas de 10,000×10,000 tiles con ruido determinista por coordenada global y render por ventana — pensada para cuando exista un visor con pan/zoom (la futura app web).

Separo deliberadamente esas dos cosas. (b) es una reescritura estructural del motor (hoy todo el mapa se genera en un array en memoria, acotado a 140×60) para un consumidor — un visor que necesita explorar un mundo más grande de lo que cabe en memoria — que todavía no existe. Construir la infraestructura de chunks ahora sería exactamente el tipo de complejidad especulativa que venimos evitando en cada fase anterior (el contenedor `.wforge`, los subcomandos `create`/`open`/`export`): se construye cuando hay una razón real, no antes.

v0.4 implementa (a) — regiones naturales con nombre, bioma dominante y descripción, más detección de océanos, lagos e islas — sobre el motor actual, sin tocar su arquitectura de generación. (b) queda explícitamente diferido (sección 3) hasta que exista un visor real que lo necesite, probablemente junto a v0.7 Web MVP o una fase dedicada posterior.

Esto también es lo que v0.5 Civilizations va a necesitar primero: no se puede poner un país sobre un mapa que no tiene regiones todavía.

---

## 2. Features exactas

### 2.1 Segmentación de regiones naturales

- Agrupar tiles contiguos del mismo bioma (componentes conexas) usando los biomas de tierra que ya produce `_terrain()`: `;` grassland, `:` drylands, `^` forest, `A` mountains, `*` snow. `.` coast es una franja de transición de 1 tile — se fusiona con la región de tierra adyacente más grande, nunca forma una región propia.
- Cada componente conexa por encima de un tamaño mínimo (evitar "regiones" de 2-3 tiles que son solo ruido del generador) se convierte en una `Region` con nombre, bioma dominante, conteo de tiles y descripción.
- Componentes más chicas que el mínimo no se descartan: se fusionan con la región de tierra vecina más grande (por adyacencia), para que cada tile de tierra siga perteneciendo a alguna región.

### 2.2 Océanos, lagos e islas

- Cuerpos de agua (`~` deep water + `,` shoals) conectados al borde del mapa, o por encima de un tamaño mínimo grande, se clasifican como **océano**.
- Cuerpos de agua completamente encerrados por tierra y por debajo de ese umbral se clasifican como **lago** — es información nueva, hoy el motor no distingue un lago de un fragmento de océano.
- Una masa de tierra que no es la más grande del mapa (no toca el "continente principal") se marca con la propiedad `is_island: true` en su región — no es un `kind` nuevo, una isla sigue teniendo su propio bioma dominante (bosque, montaña, etc.), solo que aislada.

### 2.3 Nombres y descripciones

- Nombre de región: mismo patrón combinatorio que ya usa `_title()` (`TITLE_ADJECTIVES` + `TITLE_NOUNS`, ej. "The Verdant Wilds"), con un salt de RNG distinto al del título del mundo para que no se repitan entre sí ni entre regiones del mismo mapa.
- Descripción: una línea tomada de un banco de contenido por bioma, EN/ES. La mayoría de este banco **ya está escrito** — viene de `docs/ATLASMANCER_V0.2_SPEC.md` sección 8.1 ("Regiones", banco futuro), que en su momento se escribió justo para este momento. Faltan tres entradas nuevas que esa sección no cubría porque el motor todavía no distinguía nieve/océano/lago como conceptos propios — están en la sección 6 de este documento.
- Mapeo bioma del motor → descriptor del banco existente: `forest`→Bosque, `drylands`→Desierto, `grassland`→Llanura, `mountains`→Cordillera. `snow` usa el descriptor nuevo de la sección 6 (no "Tundra": una región de `*` en este motor es nieve de alta montaña, no llanura helada — el matiz importa).

### 2.4 Ríos que no se quedan a medio camino

- Ajuste de calidad en `_river_points()`: hoy un río puede terminar en tierra seca a mitad de mapa si el camino de descenso se queda sin vecinos más bajos. v0.4 corrige esto para que todo río generado termine en un cuerpo de agua (océano o lago) o en el borde del mapa — nunca en la nada.

### 2.5 Integración con `campaign.json` y con `--open` (v0.3)

Esto es el punto más delicado de toda la fase, y la razón por la que no es solo "agregar una función de detección de regiones":

- `World` (en `atlasmancer/generator.py`) gana un campo `regions: tuple[Region, ...]`.
- `atlasmancer/renderers/campaign.py` deja de escribir `"regions": []` a mano — ahora serializa `world.regions` de verdad.
- `atlasmancer/campaign_loader.py` (de v0.3) debe **reconstruir** `world.regions` al hacer `--open`, igual que ya reconstruye landmarks. Si esto no se hace, reabrir una campaña v0.4 y volver a exportarla como `campaign.json` borraría silenciosamente las regiones — exactamente el tipo de pérdida de datos que v0.3 se construyó para evitar. Es el primer caso real donde "el archivo guardado debe ser indistinguible del original" se pone a prueba con datos nuevos.
- `meta.schema_version` sube a `"0.4.0"`. `campaign_loader.SUPPORTED_SCHEMA_VERSIONS` debe aceptar `"0.2.0"`, `"0.3.0"` y `"0.4.0"` — los archivos viejos siguen abriendo bien, simplemente no tienen regiones (se reconstruyen con `regions=()`, no es un error abrir un archivo v0.2/v0.3 sin regiones).
- `reserved_for` en el schema ya no incluye `"regions"` (deja de estar reservado, ahora está implementado). Las demás claves (`countries`, `factions`, `quests`, `dungeons`) siguen igual.

---

## 3. Qué NO debe entrar todavía

- ❌ Arquitectura de chunks, coordenadas globales, ruido determinista por chunk, render por ventana, mapas de 10,000×10,000 (ver sección 1 — diferido explícitamente hasta que exista un visor que lo necesite).
- ❌ Países, fronteras políticas, capitales, rutas comerciales (→ v0.5 Civilizations — depende de que existan regiones, que es justo lo que entrega esta fase).
- ❌ Simulación de placas tectónicas o modelo climático nuevo. El motor ya calcula elevación/humedad/temperatura de forma aproximada para decidir biomas; v0.4 no reemplaza ese cálculo, solo nombra y agrupa lo que ya produce.
- ❌ Más biomas de los que el motor ya genera (desierto cálido distinto de drylands, pantano, jungla, archipiélago como tipo de terreno). El banco de contenido de la sección 8.1 del spec de v0.2 tiene descriptores para biomas que no existen todavía en `_terrain()` — quedan ahí, reservados, hasta que el motor los produzca de verdad. No inventar tiles nuevos en esta fase.
- ❌ Tamaño máximo de mapa mayor a 140×60 (el límite actual de `_clamp`). Eso es consecuencia directa de no construir chunks todavía.

---

## 4. Criterios de aceptación

| # | Criterio |
|---|---|
| 1 | Todo tile de tierra (`;`, `:`, `^`, `A`, `*`, y `.` fusionado) pertenece a exactamente una región. Ningún tile de tierra queda sin región. |
| 2 | Las regiones por debajo del tamaño mínimo no aparecen como entradas propias — se fusionan con la región de tierra vecina más grande. |
| 3 | Mismo seed → mismas regiones, mismos nombres, mismas descripciones, mismo `is_island` por región (determinismo, igual que el resto del motor). |
| 4 | Un cuerpo de agua que toca el borde del mapa se clasifica como océano; uno completamente encerrado por tierra y chico se clasifica como lago. Existe al menos un seed de prueba con un lago real (agua interior, no costera) para verificar esto sin ambigüedad. |
| 5 | Una masa de tierra separada del continente principal tiene `is_island=True` en su región; el continente principal tiene `is_island=False`. |
| 6 | Ningún río generado termina en tierra seca a mitad de mapa — todos llegan a agua o al borde, verificado en al menos 20 seeds distintos. |
| 7 | `campaign.json` (`--format campaign`) incluye `regions[]` con entradas reales (no `[]`) cada vez que el mundo generado tiene al menos una región. |
| 8 | `--open` sobre un archivo v0.4 reconstruye `world.regions` exactamente — round-trip completo, igual que ya se exige para landmarks desde v0.3. |
| 9 | `--open` sobre un archivo v0.2 o v0.3 (sin `regions` en el JSON, o con `regions: []`) sigue abriendo sin error, con `world.regions = ()`. |
| 10 | Las descripciones de región respetan `--locale` igual que el resto del contenido narrativo — texto en inglés y español sin mezclar. |

---

## 5. Modelo de datos

Nuevo dataclass `Region` en `atlasmancer/generator.py`, alineado con el sketch de `docs/ROADMAP.md` sección 6 pero recortado a lo que esta fase realmente puede llenar con datos reales (sin `continent_id`, `danger_level`, `travel_tags` ni `secrets` todavía — esos pertenecen a fases posteriores que dependen de países/facciones/misiones):

```python
@dataclass(frozen=True)
class Region:
    id: str            # "rg-01", "rg-02"... determinista por orden de detección
    name: str          # "The Verdant Wilds"
    kind: str          # "forest" | "drylands" | "grassland" | "mountains" | "snow"
    tile_count: int
    is_island: bool
    description: str
```

En `campaign.json`, cada entrada de `regions[]`:

```json
{
  "id": "rg-01",
  "name": "The Verdant Wilds",
  "kind": "forest",
  "tile_count": 142,
  "is_island": false,
  "description": "A canopy thick enough to lose the sky for days at a time."
}
```

Cuerpos de agua (océanos/lagos) **no** se modelan como `Region` en esta fase — no tienen nombre propio ni descripción individual todavía, son metadata interna usada solo para clasificar islas y para que los ríos sepan dónde terminar. Si más adelante se necesita nombrarlos ("El Mar de Sal", "Lago Hondo"), es una extensión aditiva natural, no un cambio de schema.

---

## 6. Textos nuevos EN/ES

Banco de descripciones por bioma — reutilizar **tal cual** las cuatro entradas ya escritas en `docs/ATLASMANCER_V0.2_SPEC.md` sección 8.1 para Bosque/forest, Desierto/drylands, Llanura/grassland, Cordillera/mountains. Agregar estas tres, nuevas para v0.4:

| Bioma/concepto | EN | ES |
|---|---|---|
| Nieve de alta montaña (`*`) | Peaks high enough that summer never quite arrives. | Picos tan altos que el verano nunca termina de llegar. |
| Océano (cuerpo de agua que toca el borde) | Water wide enough to make every map a guess. | Un agua tan ancha que vuelve cada mapa una suposición. |
| Lago (cuerpo de agua interior) | Water that answers to no tide and no one. | Un agua que no responde a ninguna marea, ni a nadie. |

Etiquetas de export nuevas (mismo namespace `export.*` que ya existe):

| Clave | EN | ES |
|---|---|---|
| `export.regions_label` | Regions | Regiones |
| `landmark` no aplica — esto es independiente del array `LANDMARK_KEYS` existente. | | |

---

## 7. Riesgos

- **Ruido de regiones diminutas**: sin el umbral mínimo de tamaño (criterio #2), un mapa con terreno irregular puede producir 30 "regiones" de 3 tiles cada una — narrativamente inútil. El umbral mínimo es la mitigación; conviene exponerlo como constante ajustable, no como número mágico enterrado.
- **Ruptura silenciosa del round-trip**: esta es la fase donde, por primera vez desde v0.3, se agrega un campo nuevo a `World` que `campaign_loader.py` debe saber reconstruir. Si Codex agrega `regions` al generador y al exportador pero no al loader, todo sigue "funcionando" (los tests existentes de v0.3 no tocan regiones) pero cualquier `--open` perdería las regiones silenciosamente. El criterio #8 existe específicamente para esto — no es opcional.
- **Determinismo del algoritmo de componentes conexas**: una implementación naive que itere sobre un `set()` o un `dict` sin orden fijo puede asignar IDs de región en orden distinto entre corridas aunque el resultado visual sea el mismo. Iterar siempre en un orden fijo (ej. por coordenada `(y, x)` ascendente) para que `rg-01` sea siempre la misma región dado el mismo seed.
- **Tentación de adelantar biomas que no existen** (pantano, jungla, archipiélago como tipo de terreno): el banco de contenido de v0.2 ya tiene descriptores para ellos, lo que puede tentar a "ya que están, los implemento". Resistir — eso depende de cambios al modelo de elevación/humedad que no son parte de esta fase (ver sección 3).

---

## 8. Lista priorizada de tareas para Codex

1. Dataclass `Region` en `atlasmancer/generator.py` (sección 5).
2. Algoritmo de componentes conexas sobre los tiles de tierra (`;`, `:`, `^`, `A`, `*`, fusionando `.`), con orden de iteración fijo y determinista.
3. Fusión de componentes por debajo del umbral mínimo con su vecino de tierra más grande.
4. Clasificación de cuerpos de agua: océano (toca borde o tamaño grande) vs. lago (encerrado, chico) — usado internamente para el punto 5, no expuesto como `Region`.
5. Detección de islas: masa de tierra desconectada del continente principal → `is_island=True` en su región.
6. Nombrado de regiones reutilizando el patrón de `_title()` con un salt de RNG distinto.
7. Banco de descripciones: las cuatro entradas ya escritas en `docs/ATLASMANCER_V0.2_SPEC.md` 8.1 + las tres nuevas de la sección 6 de este documento, en `locales/en.json` y `locales/es.json` bajo `content.regions` (o el namespace que ya uses para `content.*`).
8. Arreglo de continuidad de ríos en `_river_points()` (sección 2.4) — ningún río debe terminar en tierra seca.
9. `World.regions: tuple[Region, ...]`; `generate_world()` lo puebla.
10. `atlasmancer/renderers/campaign.py`: serializar `world.regions` en vez de `"regions": []`; subir `SCHEMA_VERSION` a `"0.4.0"`; quitar `"regions"` de `RESERVED_FOR`.
11. `atlasmancer/campaign_loader.py`: aceptar `"0.4.0"` en `SUPPORTED_SCHEMA_VERSIONS`; reconstruir `world.regions` desde el JSON (con default `()` si el archivo es v0.2/v0.3 y no trae `regions`).
12. Exponer regiones en los exports de texto/HTML existentes (sección `export.regions_label`) — al menos en Markdown y HTML, con su nombre, bioma y descripción; respetar `--audience` (las regiones no tienen datos de DM, así que se muestran igual en `gm` y `player`).
13. Tests: determinismo (mismo seed → mismas regiones), umbral mínimo respetado, clasificación océano/lago con al menos un seed fijo que produzca un lago real, detección de isla, ningún río dead-end en 20+ seeds, round-trip completo de `regions` vía `--open` (incluyendo abrir un archivo v0.2/v0.3 sin regiones sin que truene), `--locale` aplicado a descripciones de región.

Orden recomendado: 1 → 2 → 3 → 9 (regiones básicas generándose) → 4 → 5 (océano/lago/isla) → 6 → 7 (nombres y texto) → 8 (ríos, independiente del resto) → 10 → 11 (persistencia — el punto más importante de no saltarse) → 12 → 13.
