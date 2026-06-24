# Atlasmancer v0.5 "Civilizations" — Especificación

Estado: propuesta para implementación
Autor del diseño: planificación/producto/narrativa (no código)
Implementación: Codex
Precondición: v0.2-v0.4 cerrados completos (regiones con bioma y `is_island` ya existen y persisten en `campaign.json`)
Referencia previa: [`docs/ROADMAP.md`](ROADMAP.md) "Fase 4: Civilizacion" y release "v0.5 Civilizations"

---

## 0. Qué es v0.5 en una frase

> Cada masa de tierra lo bastante grande se convierte en un **país**: una capital, un gobierno, un recurso principal y una crisis actual — agrupando las regiones que ya existen desde v0.4, sin inventar geografía nueva.

---

## 1. Visión de v0.5 — y otro recorte deliberado de alcance

Igual que en v0.4, `docs/ROADMAP.md` mezcla en la Fase 4 cosas de complejidad muy distinta: países/capitales/fronteras (estructura política sobre geografía que ya existe) junto con rutas comerciales, caminos, rutas marítimas, y una jerarquía de ciudades por tamaño con "servicios" (un concepto que no está definido en ningún otro lado del roadmap todavía). Aplico el mismo criterio que en fases anteriores: lo que tiene un dueño claro y un uso real ahora entra; lo que es especulativo o depende de conceptos que todavía no existen, se difiere explícitamente (sección 3).

La idea central de v0.5: **un país = una masa de tierra** (continente principal, o cualquier isla lo bastante grande). Esto no es una simplificación perezosa, es la única regla que se puede implementar sin inventar todavía un sistema de fronteras políticas dentro de una misma masa de tierra (eso requeriría modelar conflicto, cultura y diplomacia — que es justo lo que el roadmap reserva para v0.6 Facciones). Como beneficio derivado: las capitales quedan automáticamente bien separadas entre sí (están en masas de tierra distintas), sin necesitar lógica de distancia mínima aparte.

Esto también resuelve algo pendiente desde v0.1: hoy **siempre** hay exactamente una capital en cada mundo, sin importar la geografía, porque está hardcodeado. Con v0.5, hay una capital por cada masa de tierra que califique — puede ser cero (mapa muy pequeño o sin tierra suficiente), una (como hoy), o varias (continente principal + islas grandes).

---

## 2. Features exactas

### 2.1 País por masa de tierra

- Toda masa de tierra (la misma agrupación de `_land_mass_ids()` que ya existe desde v0.4) con al menos `MIN_COUNTRY_LAND_TILES` tiles de tierra (constante ajustable, ej. `20` — no es un número final, Codex puede calibrarlo) se convierte en un **país**.
- Masas de tierra más chicas que el umbral no tienen país — sus regiones quedan con `country_id = None`. Sigue siendo una isla válida con su bioma y su descripción, simplemente sin civilización propia todavía. Esto es intencional: no toda roca en el mar necesita un gobierno.
- Cada país recibe **exactamente una capital**: un `Landmark` de `kind="capital"` colocado dentro de su masa de tierra. Esto reemplaza la regla actual de "siempre hay exactamente 1 capital, sin importar la geografía" (`_landmarks()` fuerza el índice 0 a capital) por "una capital por país calificado, en cualquier cantidad que la geografía produzca."
- **Las capitales ya no consumen el presupuesto de `--landmarks`.** Hoy, con `--landmarks 0` no hay ningún landmark, ni siquiera capital. Con v0.5, las capitales se colocan siempre que exista un país calificado, independientemente de `--landmarks`; el flag `--landmarks` sigue controlando solo la cantidad de landmarks decorativos adicionales (village/ruin/tower/oddity), exactamente como hoy. Esto es un cambio de comportamiento deliberado, documentado en la sección 7 — con `--landmarks 0` y un mundo con tierra suficiente, ahora habrá capital(es) donde antes no había nada.

### 2.2 Datos de cada país

Siguiendo el sketch de `docs/ROADMAP.md` sección 6 ("Country"), recortado a los cuatro campos que el propio roadmap exige como criterio de aceptación de esta fase (capital, gobierno, recurso, crisis) — `culture`, `laws`, `allies`, `rivals` quedan fuera, dependen de que existan múltiples países interactuando, que es contenido de v0.6 Facciones:

- **Gobierno + crisis actual**: ya están escritos como pares en `docs/ATLASMANCER_V0.2_SPEC.md` sección 8.2 ("Países", banco futuro) — 6 pares EN/ES listos para usarse tal cual, igual que pasó con el banco de regiones en v0.4.
- **Recurso principal**: banco nuevo (sección 6 de este documento), uno por bioma dominante del país (el mismo cálculo de "bioma dominante" que ya existe para regiones, aplicado a la suma de tiles de todas las regiones del país).
- **Nombre del país**: mismo patrón combinatorio que ya usan el título del mundo y los nombres de región (`TITLE_ADJECTIVES` + `TITLE_NOUNS`), con un tercer salt de RNG distinto a los otros dos, para que título/regiones/países no se repitan nombres entre sí.

### 2.3 Asignación de regiones a país

- Cada `Region` gana un campo `country_id: str | None`. Una región pertenece al país de su masa de tierra (`region.is_island` ya indica si está en la masa principal o no — el `country_id` se deriva directamente de a qué masa de tierra pertenecen sus tiles, el mismo dato que v0.4 ya calcula internamente para `is_island`).
- Cada `Landmark` gana un campo `country_id: str | None`, derivado de en qué región cae su `(x, y)` — costo casi nulo, ya que las regiones de v0.4 cubren todo tile de tierra.

### 2.4 Fronteras

- No se modela una entidad `Border` separada con geometría propia. Una frontera entre dos países, si alguna vez hace falta visualizarla, es simplemente "donde una región de país A es vecina de una región de país B" — información derivable de `region_id` + adyacencia, no necesita almacenarse. Esto satisface el criterio del roadmap ("cada frontera tiene razón geográfica") porque las fronteras heredan la forma de las regiones, que ya tienen razón geográfica desde v0.4.
- En la práctica, con la regla "un país = una masa de tierra", la mayoría de los países de v0.5 no van a tener fronteras terrestres entre sí (están separados por agua). Esto es esperado y correcto para este corte — fronteras compartidas dentro de un mismo continente son del siguiente nivel de sofisticación (ver sección 3).

---

## 3. Qué NO debe entrar todavía

- ❌ Más de un país por masa de tierra (requiere modelar conflicto/cultura — v0.6 Facciones).
- ❌ Caminos, rutas marítimas, rutas comerciales con geometría propia (pathfinding, renderizado de rutas). Nadie las consume todavía — no hay mapa con capas, no hay sistema de viaje.
- ❌ Puertos como propiedad de landmark. Es una bandera derivable casi gratis (landmark adyacente a océano), pero no aporta nada accionable todavía sin rutas marítimas que la usen — se puede agregar después en una tarde sin tocar nada más.
- ❌ Jerarquía de ciudades por tamaño/población, "servicios" por ciudad. El roadmap los menciona pero no los define en ningún lado — no se inventa un concepto nuevo sin un consumidor real.
- ❌ `culture`, `laws`, `allies`, `rivals` en el modelo de país (dependen de que existan múltiples países interactuando).
- ❌ Conflictos/guerras entre países (v0.6 Facciones).

---

## 4. Criterios de aceptación

| # | Criterio |
|---|---|
| 1 | Toda masa de tierra con al menos `MIN_COUNTRY_LAND_TILES` tiles tiene exactamente un país y exactamente una capital. |
| 2 | Masas de tierra por debajo del umbral no tienen país; sus regiones tienen `country_id = None`. |
| 3 | Mismo seed → mismos países, mismos nombres, mismo gobierno/recurso/crisis, misma capital (determinismo, igual que el resto del motor). |
| 4 | `--landmarks 0` en un mundo con tierra suficiente sigue produciendo capital(es) — solo omite los landmarks decorativos. |
| 5 | Cada país tiene `government`, `resource`, `current_crisis` no vacíos, y un `capital_landmark_id` que apunta a un `Landmark` real de `kind="capital"`. |
| 6 | Toda región con país tiene `country_id` apuntando a un país real; toda región sin país calificado tiene `country_id = None`. |
| 7 | Todo landmark situado dentro de una región con país tiene el mismo `country_id` que esa región. |
| 8 | Los textos de gobierno/crisis/recurso respetan `--locale`, igual que el resto del contenido narrativo. |
| 9 | `campaign.json` incluye `countries[]` con entradas reales; `--open` reconstruye `World.countries` y los `country_id` de regiones/landmarks exactamente — round-trip completo (ver Bloque B sugerido). |

---

## 5. Modelo de datos

```python
@dataclass(frozen=True)
class Country:
    id: str                     # "co-01"
    name: str
    government: str
    resource: str
    current_crisis: str
    capital_landmark_id: str
    region_ids: tuple[str, ...]
```

Cambios en dataclasses existentes:

- `Region` gana `country_id: str | None = None`.
- `Landmark` gana `country_id: str | None = None`.
- `World` gana `countries: tuple[Country, ...] = ()`.

En `campaign.json`, cada entrada de `countries[]` refleja `Country` tal cual; `regions[]` y `landmarks[]` ganan el campo `country_id` (puede ser `null`).

---

## 6. Textos nuevos EN/ES

Gobierno + crisis: reutilizar tal cual los 6 pares ya escritos en `docs/ATLASMANCER_V0.2_SPEC.md` sección 8.2.

Recurso principal por bioma dominante del país — banco nuevo:

| Bioma dominante | EN | ES |
|---|---|---|
| forest | timber tall enough to frame a fleet | madera lo bastante alta para armar una flota |
| drylands | dyes worth more than the caravans that carry them | tintes que valen más que las caravanas que los cargan |
| grassland | grain enough to outlast any siege | grano suficiente para resistir cualquier sitio |
| mountains | ore that never quite runs out | mineral que nunca termina de agotarse |
| snow | furs thick enough to trade for a winter | pieles lo bastante gruesas para cambiarlas por un invierno |

Etiqueta de export nueva (mismo namespace `export.*`):

| Clave | EN | ES |
|---|---|---|
| `export.countries_label` | Countries | Países |
| `export.capital_label` | Capital | Capital |
| `export.government_label` | Government | Gobierno |
| `export.resource_label` | Resource | Recurso |
| `export.crisis_label` | Current crisis | Crisis actual |

---

## 7. Riesgos

- **Cambio de comportamiento para seeds existentes**: hoy siempre hay exactamente 1 capital, en cualquier geografía; después de v0.5, el número de capitales depende de cuántas masas de tierra califiquen. Para el mismo seed, esto puede significar más capitales que antes (si hay islas grandes) o, en mapas casi sin tierra, ninguna. Documentar en `CHANGELOG.md` exactamente como se hizo para el cambio de conectividad de `_neighbors()` en v0.4 — ya es el tercer cambio de este tipo en el proyecto, así que conviene que quede claro que es esperado, no un bug.
- **Umbral `MIN_COUNTRY_LAND_TILES` mal calibrado**: muy bajo y cualquier islita de 6 tiles se convierte en una "nación" con gobierno y crisis propios, lo cual se siente ridículo. Muy alto y mapas pequeños (ej. `--width 24 --height 12`, el mínimo soportado) podrían terminar sin ningún país. Empezar en `20` y ajustar con pruebas reales en varios tamaños de mapa.
- **Reincidencia del problema de v0.4**: agregar `countries` a `World` significa, otra vez, que `campaign_loader.py` tiene que aprender a reconstruirlo en `--open`, exactamente el mismo punto donde apareció el bug de islas. Mismo cuidado: escribir primero el test de round-trip completo (`World` reconstruido == original, campo por campo, incluyendo `country_id` en cada región y cada landmark) antes de dar el bloque por terminado.
- **Tentación de adelantar rutas/fronteras visuales**: una vez que existen países, es tentador dibujar líneas de frontera o rutas comerciales en el HTML/PNG "ya que están los datos". Resistir — eso es trabajo de presentación que no se pidió en esta fase y no tiene todavía un caso de uso real (nadie navega el mapa con pan/zoom todavía).

---

## 8. Lista priorizada de tareas para Codex

Recomendado dividir en dos bloques, como se hizo en v0.4 — el riesgo principal está otra vez en la integración con persistencia, no en el algoritmo en sí.

### Bloque A — motor de países

1. `Country` dataclass (sección 5).
2. Detección de masas de tierra calificadas: reusar `_land_mass_ids()` (ya existe desde v0.4), filtrar por `MIN_COUNTRY_LAND_TILES`.
3. Colocar una capital por masa de tierra calificada — esto reemplaza la lógica actual en `_landmarks()` que fuerza el índice 0 a `kind="capital"` sin importar geografía. Las capitales se generan independientemente del presupuesto de `--landmarks`.
4. `--landmarks 0` sigue produciendo capitales si hay tierra calificada — verificar explícitamente con un test (criterio #4).
5. Asignar `country_id` a cada `Region` según su masa de tierra.
6. Asignar `country_id` a cada `Landmark` según en qué región cae.
7. Nombrado de país: mismo patrón `TITLE_ADJECTIVES`/`TITLE_NOUNS` con un salt de RNG nuevo y distinto al de regiones/título.
8. Banco de gobierno/crisis (reutilizar v0.2 sección 8.2) y recurso principal (sección 6 de este documento) en `locales/en.json`/`es.json`, namespace `content.governments`/`content.crises`/`content.resources` (o el esquema de claves que prefieras, mientras tenga test de paridad EN/ES como los demás).
9. `World.countries: tuple[Country, ...]`; `generate_world()` lo puebla.
10. Tests: determinismo, umbral respetado, `--landmarks 0` con capitales, `country_id` correcto en regiones y landmarks, textos en locale correcto.

### Bloque B — persistencia y exports (después de que A esté aprobado)

11. `atlasmancer/renderers/campaign.py`: serializar `world.countries`; agregar `country_id` a cada entrada de `regions[]`/`landmarks[]`; subir `SCHEMA_VERSION` a `"0.5.0"`; quitar `"countries"` de `RESERVED_FOR`.
12. `atlasmancer/campaign_loader.py`: aceptar `"0.5.0"`; reconstruir `World.countries` y los `country_id` de regiones/landmarks al hacer `--open`; archivos v0.2-v0.4 sin países siguen abriendo con `countries=()` y `country_id=None` en todo.
13. `localize_world()`: extender la traducción por índice de catálogo a `government`/`current_crisis`/`resource` de cada país.
14. Exponer países en Markdown/HTML (sección con nombre, gobierno, recurso, crisis, capital) — igual que se hizo con regiones en v0.4 Bloque B.
15. Tests de round-trip completo (el punto más importante, no saltárselo), apertura de archivos viejos sin países, traducción cross-locale de textos de país.

Orden recomendado: Bloque A completo y aprobado → Bloque B.
