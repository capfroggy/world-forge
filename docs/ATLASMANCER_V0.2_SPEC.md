# Atlasmancer v0.2 "Foundation" — Especificación

Estado: propuesta para implementación
Autor del diseño: planificación/producto/narrativa (no código)
Implementación: Codex
Reemplaza el nombre de trabajo `world-forge` por **Atlasmancer**.
URL objetivo: https://Atlasmancer.gt.tc
Referencia previa: [`docs/ROADMAP.md`](ROADMAP.md) (este documento concreta la "Fase 0 / v0.2" de ese roadmap)

---

## 0. Qué es v0.2 en una frase

> Convertir el prototipo CLI `world-forge` en **Atlasmancer**: el mismo motor, con identidad propia, bilingüe de verdad (EN/ES), con un formato `campaign.json` versionado y estable, y con una primera mejora real de utilidad para DMs (separación contenido jugador/DM). Sin tocar todavía geografía, países, facciones, misiones generadas ni app web.

---

## 1. Visión de v0.2

- **Identidad**: el proyecto deja de ser un experimento sin nombre ("world-forge") y se convierte en **Atlasmancer**, con un nombre, un comando CLI y un dominio propios. Esto no es cosmético: es lo que permite anunciar el proyecto, recibir contribuciones y versionar promesas hacia el usuario.
- **Multilenguaje real, no decorativo**: hoy el motor tiene **cero** i18n — todo el texto narrativo y de CLI está en inglés, hardcodeado en `generator.py`. v0.2 introduce el primer sistema de locales (EN/ES) y la regla de que ningún texto nuevo visible al usuario puede evitarlo.
- **Formato de mundo portable**: hoy `--format json` exporta el dump interno del generador. v0.2 introduce `campaign.json`, un formato versionado, pensado para sobrevivir a los cambios del motor (geografía, países, facciones llegarán en v0.4–v0.6) sin romper mundos ya guardados.
- **Utilidad real para DMs, ya**: sin esperar a facciones o misiones generadas, v0.2 separa explícitamente "lo que puede ver un jugador" de "lo que solo ve el DM" en cada exportación. Es la mejora de UX para mesa más barata y más valiosa que se puede dar ahora.
- **Puente hacia la app web**: v0.2 no construye la app web, pero deja el schema, el i18n y el branding listos para que v0.7 (Web MVP) no tenga que rehacer decisiones de nombres de campos ni de idioma.

No es una reescritura. Es renombrar, traducir, versionar el formato de salida y separar audiencias — sobre el motor que ya existe.

---

## 2. Features exactas

### 2.1 Rebranding → Atlasmancer
- Nombre de distribución/paquete: `atlasmancer` (antes `world-forge`).
- Comando CLI: `atlasmancer` (antes `world-forge`).
- `--seed`, `--width`, `--height`, `--landmarks`, `--format`, `--output`, `--tile-size` se mantienen (mismos nombres, mismo comportamiento).
- Sin shim de compatibilidad `world-forge`: el proyecto es alpha (`0.1.0`), sin usuarios externos conocidos, así que el rename es limpio. Se documenta en un `CHANGELOG.md` la nota de breaking rename.
- README, `pyproject.toml`, URLs de repo, banners de ayuda (`--help`) y nombre en exports (HTML/Markdown/JSON) reflejan "Atlasmancer".
- El dominio `Atlasmancer.gt.tc` se referencia en README como home futura de la app web (todavía no existe app web en v0.2 — ver sección 3).

### 2.2 Sistema i18n EN/ES
- Carpeta `locales/` con `en.json` y `es.json` (estructura exacta en sección 6).
- Nuevo flag `--locale {en,es}` (default `en`).
- Todo el texto visible pasa a depender del locale:
  - Ayuda de CLI (`--help`, descripciones de flags, mensajes de error).
  - Leyenda de terreno y de landmarks.
  - Encabezados de export (Markdown/HTML): "Legend", "Landmarks", "Hook", "NPC", "Rumor", "Secret", "Danger", "Reward", etc.
  - Los seis bancos de fragmentos narrativos (`NPCS`, `HOOKS`, `SECRETS`, `DANGERS`, `REWARDS`, `ODD_RUMORS`) existen en versión EN y versión ES, **con el mismo largo y mismo orden** en ambos idiomas (ver regla de determinismo en sección 4).
- **Regla de diseño**: los nombres propios generados (ej. "Sol Reach", "Eld Wick") **no se traducen**. Son nombres inventados de fantasía, no palabras con significado — traducirlos rompería la identidad del mundo. Solo se traduce el texto descriptivo alrededor de esos nombres.
- Fallback: si una clave falta en `es.json`, se usa `en.json` y se loggea un warning (no se rompe la ejecución).

### 2.3 `campaign.json` v0.2 (primer formato de mundo portable)
- Nuevo valor de `--format campaign` que emite el nuevo schema versionado (sección 5).
- `--format json` (el dump actual del motor) se mantiene por compatibilidad dentro de la serie 0.x, pero se marca como **deprecated** en `--help` a favor de `--format campaign`.
- El schema incluye metadata de versión (`schema_version`, `generator_version`), `seed`, `locale`, parámetros de generación, el mapa, los landmarks, y **arrays vacíos reservados** (`regions`, `countries`, `factions`, `quests`, `dungeons`) para que la migración a v0.4–v0.6 sea aditiva, no destructiva.
- Determinista: mismo seed + mismo locale + misma versión de generador → mismo `campaign.json` byte a byte (salvo `created_at`).

### 2.4 Separación de audiencia: jugador vs DM
- Nuevo flag `--audience {gm,player}` (default `gm`).
- `--audience player` oculta `secret`, `danger` y `reward` de cada landmark en HTML, Markdown y `campaign.json`; conserva `hook`, `rumor` y `npc` (lo que es razonable compartir con la mesa).
- Aplica a todos los formatos excepto `plain`/`ansi`/`png` (que ya no muestran texto narrativo, solo el mapa).
- Esto es la base mínima de "GM map" vs "player map" que el roadmap pide para fases posteriores, implementada ahora con el modelo de datos actual (sin esperar países/facciones).

### 2.5 Pulido de exports impresos
- Título del mundo, leyenda y etiquetas de sección en HTML/Markdown respetan `--locale`.
- HTML imprimible incluye atributo `lang="en"`/`lang="es"` correcto para accesibilidad/impresión.

### 2.6 `examples/`
- Carpeta `examples/` con un mundo de muestra exportado en ambos idiomas y ambas audiencias (mínimo 4 archivos: `example-en-gm.html`, `example-en-player.html`, `example-es-gm.html`, `example-es-player.html`, más su `campaign.json`).

### 2.7 Tests nuevos
- Test de paridad de longitud/orden entre bancos de fragmentos EN/ES.
- Test de fallback de locale (clave faltante en ES cae a EN sin crashear).
- Test de schema de `campaign.json` (claves requeridas presentes, arrays reservados vacíos en v0.2).
- Test de `--audience player` (verifica que `secret`/`danger`/`reward` no aparecen en el output).
- Test de que `atlasmancer --format plain` sigue funcionando igual que antes del rename (no regresión).

---

## 3. Qué NO debe entrar todavía

Explícitamente fuera de alcance de v0.2 (pertenecen a fases posteriores del roadmap):

- ❌ Continentes, regiones naturales, biomas simulados, elevación/humedad/temperatura (→ v0.4 Geography Engine).
- ❌ Países, capitales políticas, fronteras, rutas comerciales, recursos (→ v0.5 Civilizations).
- ❌ Facciones, NPCs como entidades persistentes con relaciones, misiones generadas, dungeons generados (→ v0.6 Playable Content). En v0.2 los NPCs/hooks/rumores siguen siendo **fragmentos de texto** ligados a un landmark, no entidades con `id` propio.
- ❌ Guardar/abrir mundo por archivo `.wforge`, comandos `create`/`open`/`export` con estado persistente (→ v0.3 Campaign Pack). v0.2 solo define el **formato** `campaign.json`; no construye el flujo de guardado/carga.
- ❌ App web, editor visual, IndexedDB, canvas, React/Svelte (→ v0.6+/v0.7).
- ❌ Más idiomas que EN/ES (el sistema debe estar preparado para más, pero no se entregan más catálogos ahora).
- ❌ Cuentas de usuario, backend, base de datos, monetización.
- ❌ Despliegue real del dominio `Atlasmancer.gt.tc` (eso es v0.7+, cuando exista algo que desplegar).

Si Codex encuentra que una tarea de v0.2 "tira" hacia alguna de estas, la respuesta correcta es dejar un placeholder reservado (como los arrays vacíos del schema), no implementarla parcialmente.

---

## 4. Criterios de aceptación

| # | Criterio |
|---|---|
| 1 | `pip install -e .` instala el comando `atlasmancer`; `world-forge` ya no existe como comando. |
| 2 | `python -m unittest` pasa en verde, incluyendo los tests nuevos de la sección 2.7. |
| 3 | `atlasmancer --seed x --locale en` y `atlasmancer --seed x --locale es` generan el mismo mapa/landmarks (mismas posiciones, mismos nombres propios) con texto descriptivo en el idioma correcto. |
| 4 | Los bancos `content.npcs`, `content.hooks`, `content.secrets`, `content.dangers`, `content.rewards`, `content.rumors` tienen **exactamente el mismo número de entradas** en `en.json` y `es.json` (test automatizado lo verifica). |
| 5 | Pedir un locale no soportado (`--locale fr`) da un error claro y traducido, no un crash. |
| 6 | `atlasmancer --format campaign --output x.json` produce un JSON válido que cumple el schema de la sección 5, con `schema_version: "0.2.0"`. |
| 7 | `atlasmancer --format campaign --audience player` no contiene en ningún punto del JSON las claves `secret`, `danger` ni `reward` con contenido (deben estar ausentes u omitidas, no solo vacías por accidente). |
| 8 | El HTML exportado en `--locale es` tiene `<html lang="es">` y todas las etiquetas de sección en español. |
| 9 | `examples/` contiene los 4 exports de muestra (EN/ES × GM/player) y se generan con un comando documentado en el README. |
| 10 | README documenta cómo agregar un tercer idioma (qué archivo copiar, qué claves no traducir, cómo correr el test de paridad). |
| 11 | Ningún texto del catálogo `content.*` es copia de material de Wizards of the Coast ni de settings con copyright reconocible — todo es contenido original nuevo (regla heredada de `docs/ROADMAP.md` sección 10). |

---

## 5. Modelo de datos inicial — `campaign.json` (schema v0.2.0)

Diseño deliberadamente pequeño: envuelve lo que el motor **ya genera** (mundo + landmarks) con metadata estable, y reserva espacio para lo que vendrá. No incluye `Country`/`Faction`/`Quest`/`Region` como objetos reales todavía — esos llegan con su fase correspondiente y se documentarán como `schema_version` `0.4.0`, `0.5.0`, `0.6.0` cuando exista lógica real detrás.

```json
{
  "meta": {
    "schema_version": "0.2.0",
    "generator": "atlasmancer",
    "generator_version": "0.2.0",
    "world_id": "sha1 corto derivado del seed",
    "seed": "salt-crown",
    "locale": "en",
    "audience": "gm",
    "created_at": "2026-06-19T00:00:00Z",
    "params": {
      "width": 72,
      "height": 28,
      "landmark_count": 9
    }
  },
  "title": "The Salt Expanse of Sol",
  "map": {
    "width": 72,
    "height": 28,
    "legend": {
      "~": "terrain.deep_water",
      ",": "terrain.shoals",
      ".": "terrain.coast",
      ";": "terrain.grassland",
      ":": "terrain.drylands",
      "^": "terrain.forest",
      "A": "terrain.mountains",
      "*": "terrain.snow",
      "|": "terrain.river"
    },
    "ascii": ["~~~~~~~~~~", "..."]
  },
  "landmarks": [
    {
      "id": "lm-01",
      "symbol": "C",
      "kind": "capital",
      "name": "Sol Reach",
      "x": 41,
      "y": 15,
      "public": {
        "hook": "The next full moon will reveal a path that normally is not there.",
        "rumor": "Every seventh bridge is older than the river.",
        "npc": "a masked captain looking for a missing heir"
      },
      "gm": {
        "secret": "A nearby spring is slowly changing anyone who drinks from it.",
        "danger": "a curse that makes compasses lie",
        "reward": "the true name of a dangerous spirit"
      }
    }
  ],
  "regions": [],
  "countries": [],
  "factions": [],
  "quests": [],
  "dungeons": [],
  "reserved_for": {
    "regions": "v0.4 Geography Engine",
    "countries": "v0.5 Civilizations",
    "factions": "v0.6 Playable Content",
    "quests": "v0.6 Playable Content",
    "dungeons": "v0.8 Dungeons & Tactical Maps"
  }
}
```

Notas de diseño:
- `landmarks[].gm` está **ausente** cuando `meta.audience` es `"player"` (no presente como objeto vacío — ausente del JSON), para que un DM pueda enviar el archivo completo a sus jugadores sin riesgo de spoilers en herramientas que muestren JSON crudo.
- `id` de landmark (`lm-01`, `lm-02`...) es nuevo en v0.2: hoy los landmarks no tienen identidad estable, solo posición. Es el primer paso hacia los IDs estables que pide `docs/ROADMAP.md` sección 5.
- `legend` referencia claves de i18n (`terrain.deep_water`) en vez de texto plano, para que una herramienta que lea el JSON pueda traducir la leyenda sin volver a generar el mundo.
- `world_id` se deriva del seed (hash corto), no es aleatorio — así el mismo seed siempre produce el mismo `world_id`, útil para futuras referencias cruzadas (v0.3 Campaign Pack).

---

## 6. Estructura de i18n EN/ES

```text
locales/
  en.json     # idioma base / fallback
  es.json
```

Namespacing de claves (idéntico en ambos archivos):

```text
cli.description
cli.flags.seed
cli.flags.width
cli.flags.height
cli.flags.landmarks
cli.flags.format
cli.flags.locale
cli.flags.audience
cli.flags.tile_size
cli.flags.output
cli.errors.png_requires_output
cli.errors.unsupported_locale

format.plain
format.ansi
format.markdown
format.json
format.json_deprecated_note
format.campaign
format.html
format.png

terrain.deep_water
terrain.shoals
terrain.coast
terrain.grassland
terrain.drylands
terrain.forest
terrain.mountains
terrain.snow
terrain.river

landmark.capital
landmark.village
landmark.ruin
landmark.tower
landmark.oddity

export.legend_label
export.landmarks_label
export.hook_label
export.npc_label
export.rumor_label
export.secret_label
export.danger_label
export.reward_label
export.seed_label
export.audience_player_note

content.npcs[]
content.hooks[]
content.rumors[]
content.secrets[]
content.dangers[]
content.rewards[]
```

Reglas:
- `content.*` son arrays paralelos: `content.hooks[3]` en `es.json` debe ser la traducción/equivalente tonal de `content.hooks[3]` en `en.json`, nunca una entrada reordenada. Esto preserva el determinismo por seed entre idiomas (criterio de aceptación #3).
- Ninguna clave de `content.*` traduce nombres propios — esos siguen viviendo en el generador (`PREFIXES`/`SUFFIXES`/`TITLE_ADJECTIVES`/`TITLE_NOUNS`), fuera de los locales, porque son fonética inventada, no vocabulario.
- Agregar un idioma nuevo = copiar `en.json` → `xx.json`, traducir valores, correr el test de paridad de longitud. No requiere tocar el motor.

---

## 7. Textos UI/CLI en inglés y español

### CLI — descripción y flags

| Clave | EN | ES |
|---|---|---|
| `cli.description` | Generate tiny deterministic fantasy worlds for tabletop campaigns. | Genera mundos de fantasía deterministas y compactos para campañas de mesa. |
| `cli.flags.seed` | Seed text for deterministic worlds. | Texto semilla para generar mundos deterministas. |
| `cli.flags.width` | Map width, from 24 to 140. | Ancho del mapa, de 24 a 140. |
| `cli.flags.height` | Map height, from 12 to 60. | Alto del mapa, de 12 a 60. |
| `cli.flags.landmarks` | Number of named places to add, from 0 to 30. | Número de lugares con nombre a agregar, de 0 a 30. |
| `cli.flags.format` | Output format. | Formato de salida. |
| `cli.flags.locale` | Output language: en or es. | Idioma de salida: en o es. |
| `cli.flags.audience` | Content audience: gm (full secrets) or player (safe to share). | Audiencia del contenido: gm (con secretos) o player (seguro para compartir). |
| `cli.flags.tile_size` | Pixel size for PNG tiles, from 6 to 28. | Tamaño en píxeles de cada celda del PNG, de 6 a 28. |
| `cli.flags.output` | Write output to a file. | Escribe la salida a un archivo. |
| `cli.errors.png_requires_output` | --format png requires --output | --format png requiere --output |
| `cli.errors.unsupported_locale` | Unsupported locale '{locale}'. Available: en, es. | Idioma no soportado '{locale}'. Disponibles: en, es. |

### Formatos

| Clave | EN | ES |
|---|---|---|
| `format.json_deprecated_note` | --format json is deprecated; use --format campaign. | --format json está obsoleto; usa --format campaign. |

### Leyenda de terreno

| Clave | EN | ES |
|---|---|---|
| `terrain.deep_water` | deep water | aguas profundas |
| `terrain.shoals` | shoals | bajíos |
| `terrain.coast` | coast | costa |
| `terrain.grassland` | grassland | pradera |
| `terrain.drylands` | drylands | tierras áridas |
| `terrain.forest` | forest | bosque |
| `terrain.mountains` | mountains | montañas |
| `terrain.snow` | snow | nieve |
| `terrain.river` | river | río |

### Tipos de landmark

| Clave | EN | ES |
|---|---|---|
| `landmark.capital` | capital | capital |
| `landmark.village` | village | aldea |
| `landmark.ruin` | ruin | ruina |
| `landmark.tower` | tower | torre |
| `landmark.oddity` | oddity | rareza |

### Etiquetas de export (Markdown/HTML)

| Clave | EN | ES |
|---|---|---|
| `export.legend_label` | Legend | Leyenda |
| `export.landmarks_label` | Landmarks | Lugares destacados |
| `export.hook_label` | Hook | Gancho |
| `export.npc_label` | NPC | PNJ |
| `export.rumor_label` | Rumor | Rumor |
| `export.secret_label` | Secret | Secreto |
| `export.danger_label` | Danger | Peligro |
| `export.reward_label` | Reward | Recompensa |
| `export.seed_label` | Seed | Semilla |
| `export.audience_player_note` | Player-safe copy — no GM secrets included. | Copia segura para jugadores — sin secretos de DM. |

---

## 8. Templates narrativos originales

Todo el contenido de esta sección es original, en el mismo tono breve y evocador que los bancos ya existentes en el motor (`NPCS`, `HOOKS`, `SECRETS`, `DANGERS`, `REWARDS`, `ODD_RUMORS`). No reutiliza nombres, criaturas ni términos de settings publicados.

**Alcance de implementación**: las filas marcadas **(v0.2)** son contenido nuevo que el motor sí consume ya en esta versión (asentamientos, NPCs, rumores). Las filas marcadas **(banco futuro)** son contenido escrito ahora para que Codex/narrativa no tengan que inventar tono después, pero el motor todavía no las usa (regiones, países, facciones, misiones llegan en v0.4–v0.6).

### 8.1 Regiones (banco futuro — v0.4 Geography Engine)

| Tipo | EN | ES |
|---|---|---|
| Bosque | A canopy thick enough to lose the sky for days at a time. | Una copa tan espesa que pierde el cielo durante días enteros. |
| Desierto | Heat that bends the horizon into something unreliable. | Un calor que dobla el horizonte hasta volverlo poco confiable. |
| Cordillera | Peaks old enough to have outlived their own names. | Picos lo bastante viejos como para haber sobrevivido a sus propios nombres. |
| Costa | A shoreline that rearranges its sandbars every season. | Un litoral que reorganiza sus bancos de arena cada temporada. |
| Pantano | Water that never quite decides if it is land. | Un agua que nunca termina de decidir si es tierra. |
| Tundra | Cold that keeps better secrets than any vault. | Un frío que guarda secretos mejor que cualquier bóveda. |
| Llanura | Grass tall enough to hide a caravan, or a war. | Un pastizal alto como para esconder una caravana, o una guerra. |
| Jungla | Green so dense it swallows roads within a year. | Un verde tan denso que traga caminos en menos de un año. |
| Archipiélago | Islands that trade more rumors than cargo. | Islas que intercambian más rumores que carga. |
| Tierras malditas | Ground where nothing dies completely. | Una tierra donde nada termina de morir. |

### 8.2 Países (banco futuro — v0.5 Civilizations)

Formato de campo: `government` + `current_crisis`.

| Gobierno (EN) | Gobierno (ES) | Crisis actual (EN) | Crisis actual (ES) |
|---|---|---|---|
| a merchant oligarchy that taxes roads more than goods | una oligarquía mercantil que grava más los caminos que la mercancía | the treasury is funding a war nobody has declared | el tesoro financia una guerra que nadie ha declarado |
| a tribal council bound by oaths older than its borders | un consejo tribal unido por juramentos más viejos que sus fronteras | two seats on the council are claimed by the same heir | dos asientos del consejo son reclamados por el mismo heredero |
| a theocratic monarchy ruling in a god's declared absence | una monarquía teocrática que gobierna en ausencia declarada de un dios | the god's silence is starting to look permanent | el silencio del dios empieza a parecer permanente |
| a fractured set of duchies loyal to a crown that no longer meets | un conjunto fracturado de ducados leales a una corona que ya no se reúne | one duchy has started minting its own coin | un ducado ha comenzado a acuñar su propia moneda |
| a military protectorate that promised it was temporary | un protectorado militar que prometió ser temporal | the occupying garrison has stopped sending reports home | la guarnición ocupante dejó de enviar informes a casa |
| an exiled court still issuing laws for a capital it lost | una corte exiliada que sigue dictando leyes para una capital que perdió | a faction inside the court wants to stop pretending | una facción dentro de la corte quiere dejar de fingir |

### 8.3 Asentamientos

**(v0.2 — ya consumido por el motor, descriptor de una línea por tipo de landmark)**

| Tipo | EN | ES |
|---|---|---|
| Capital | A city built around the idea that it will never fall. | Una ciudad construida sobre la idea de que nunca caerá. |
| Aldea | Small enough that every stranger is news by sundown. | Tan pequeña que todo forastero es noticia antes del atardecer. |
| Ruina | A place that kept its shape after it lost its purpose. | Un lugar que conservó su forma después de perder su propósito. |
| Torre | A single structure that refuses to explain itself. | Una sola estructura que se niega a explicarse. |
| Rareza | Somewhere maps disagree on what to call this. | Un lugar donde los mapas no se ponen de acuerdo en cómo llamarlo. |

**(banco futuro — tipos de `Place` del roadmap aún no implementados: puerto, fuerte, templo)**

| Tipo | EN | ES |
|---|---|---|
| Puerto | A harbor that profits equally from trade and smuggling. | Un puerto que se beneficia igual del comercio y el contrabando. |
| Fuerte | Walls maintained by soldiers who forgot which war they're for. | Murallas mantenidas por soldados que olvidaron para qué guerra son. |
| Templo | A shrine that answers fewer prayers than it used to. | Un santuario que responde menos plegarias que antes. |

### 8.4 NPCs — banco nuevo (v0.2, se suma a los 8 existentes en `NPCS`)

| EN | ES |
|---|---|
| a retired mercenary who only takes jobs that bore her | una mercenaria retirada que solo acepta trabajos que la aburran |
| a child who keeps drawing a door that isn't there yet | un niño que sigue dibujando una puerta que todavía no existe |
| a merchant who pays too well for very specific rocks | un mercader que paga demasiado bien por rocas muy específicas |
| a priest who stopped believing but kept the schedule | un sacerdote que dejó de creer pero mantuvo el horario |
| a cartographer who refuses to finish one particular map | una cartógrafa que se niega a terminar un mapa en concreto |
| a soldier counting down to a discharge that keeps getting delayed | un soldado contando los días para una baja que se sigue postergando |
| a beekeeper whose hives produce something that isn't quite honey | un apicultor cuyas colmenas producen algo que no es del todo miel |
| a judge who has never once ruled against the same family | un juez que jamás ha fallado en contra de la misma familia |

### 8.5 Facciones (banco futuro — v0.6 Playable Content)

Formato de campo: `type` + `goal` + `method`.

| Tipo | Goal (EN) | Method (EN) | Goal (ES) | Method (ES) |
|---|---|---|---|---|
| Gremio | control every price within three days' ride | buying out competitors before they can refuse | controlar cada precio a tres días de viaje | comprando competidores antes de que puedan negarse |
| Culto | wake something that was put to sleep on purpose | recruiting the recently grieving | despertar algo que fue dormido a propósito | reclutando a quienes recién perdieron a alguien |
| Casa noble | restore a title that the crown quietly revoked | calling in debts nobody else remembers | restaurar un título que la corona revocó en silencio | cobrando deudas que nadie más recuerda |
| Compañía mercenaria | get paid by both sides of the same war | selling the same information twice | cobrarle a ambos lados de la misma guerra | vendiendo la misma información dos veces |
| Círculo druida | undo one specific act of deforestation | making the forest itself inhospitable to outsiders | revertir un acto específico de deforestación | volviendo el bosque mismo inhóspito para forasteros |
| Sindicato criminal | own the only safe road through the region | making every other road slightly more dangerous | controlar el único camino seguro de la región | volviendo cada otro camino un poco más peligroso |

### 8.6 Misiones (banco futuro — v0.6 Playable Content)

Formato de campo: `type` + `hook` + `objective` + `complication`.

| Tipo | Hook (EN) | Objective (EN) | Complication (EN) |
|---|---|---|---|
| Investigación | A death was ruled natural by someone who wasn't there. | Find who actually signed the report. | The signature belongs to someone three years dead. |
| Rescate | A letter arrives a week after the sender went missing. | Retrace the sender's last known route. | The letter describes a place that doesn't exist on any map. |
| Escolta | A merchant pays double for silence about the cargo. | Deliver the cargo without inspecting it. | Inspecting it becomes unavoidable halfway through. |
| Diplomacia | Two villages claim the same well after a drought. | Broker a water-sharing agreement before the season ends. | A third party benefits from the feud continuing. |
| Caza de monstruo | Livestock vanish without blood, tracks, or sound. | Identify what is actually responsible. | It isn't a monster — it's someone using one as cover. |
| Misterio | A festival tradition suddenly has no one who remembers starting it. | Find the tradition's true origin. | The origin was deliberately erased, not forgotten. |

(EN español, mismas filas, mismo orden — para Codex: estas seis se traducen 1:1 manteniendo la estructura de cuatro campos.)

| Tipo | Gancho (ES) | Objetivo (ES) | Complicación (ES) |
|---|---|---|---|
| Investigación | Una muerte fue declarada natural por alguien que no estuvo presente. | Averiguar quién firmó realmente el informe. | La firma pertenece a alguien que lleva tres años muerto. |
| Rescate | Llega una carta una semana después de que el remitente desapareciera. | Reconstruir la última ruta conocida del remitente. | La carta describe un lugar que no existe en ningún mapa. |
| Escolta | Un mercader paga el doble por silencio sobre la carga. | Entregar la carga sin inspeccionarla. | Inspeccionarla se vuelve inevitable a mitad del camino. |
| Diplomacia | Dos aldeas reclaman el mismo pozo tras una sequía. | Negociar un acuerdo de reparto de agua antes de que termine la temporada. | Un tercero se beneficia de que la disputa continúe. |
| Caza de monstruo | El ganado desaparece sin sangre, huellas ni ruido. | Identificar al verdadero responsable. | No es un monstruo: es alguien usando uno como tapadera. |
| Misterio | Una tradición del festival de pronto no tiene quién recuerde cómo empezó. | Encontrar el origen verdadero de la tradición. | El origen fue borrado a propósito, no olvidado. |

### 8.7 Rumores — banco nuevo (v0.2, se suma a los 6 existentes en `ODD_RUMORS`)

| EN | ES |
|---|---|
| The toll collector hasn't aged in three generations. | El cobrador de peaje no ha envejecido en tres generaciones. |
| Every map of this place disagrees about which way is north. | Cada mapa de este lugar no se pone de acuerdo en dónde queda el norte. |
| The local bread never goes stale, and nobody asks why. | El pan local nunca se pone duro, y nadie pregunta por qué. |
| Dogs refuse to cross the old bridge after dark. | Los perros se niegan a cruzar el puente viejo después del anochecer. |
| The town clock has struck thirteen exactly once, and everyone remembers it differently. | El reloj del pueblo dio las trece exactamente una vez, y todos lo recuerdan distinto. |
| Letters sent from here always arrive a day before they were written. | Las cartas enviadas desde aquí siempre llegan un día antes de ser escritas. |
| The well water tastes like rain that hasn't fallen yet. | El agua del pozo sabe a una lluvia que todavía no ha caído. |
| Nobody in town will say the previous mayor's name out loud. | Nadie en el pueblo dice en voz alta el nombre del alcalde anterior. |

---

## 9. Riesgos

- **Scope creep hacia geografía/civilización**: el riesgo más probable es que, al definir `campaign.json` con arrays `regions`/`countries`/`factions`, alguien empiece a implementarlos "ya que está el schema". Mitigación: los criterios de aceptación exigen explícitamente que esos arrays queden vacíos en v0.2.
- **i18n a medias**: si solo se traduce parte de la superficie (por ejemplo CLI sí, pero exports HTML no), el resultado es peor que no tener i18n — mezcla idiomas dentro de un mismo documento. Mitigación: el test de paridad y el criterio #8 cubren HTML; falta cubrir explícitamente que ninguna cadena quede hardcodeada — recomendar a Codex un grep de strings en inglés sueltas dentro de `renderers/` como parte del PR.
- **Bloqueo de schema antes de tiempo**: fijar `campaign.json` v0.2 demasiado rígido puede forzar una migración rota cuando lleguen regiones/países reales. Mitigación: el campo `reserved_for` documenta intención sin comprometer estructura interna; cualquier cambio futuro a esos arrays es additivo (campo nuevo, no campo renombrado).
- **Calidad y tono dispar entre EN y ES**: una traducción literal puede sonar plana en español, o un fragmento "creativo" en español puede no tener equivalente natural en inglés. Mitigación: los bancos de esta especificación están escritos como pares pensados, no traducidos palabra por palabra; mantener esa práctica para contenido futuro (escribir el par, no traducir después).
- **Riesgo de marca/dominio**: `gt.tc` es un servicio de subdominios gratuitos; algunos navegadores, gestores de contraseñas o filtros corporativos marcan subdominios de hosting gratuito como sospechosos, y no hay garantía de continuidad del servicio a largo plazo. No bloquea v0.2 (no hay despliegue todavía), pero vale la pena decidir antes de v0.7 si el dominio final del proyecto será ese o uno propio, para no tener que migrar URLs ya compartidas por usuarios.
- **Riesgo legal/IP**: bajo en v0.2 porque todo el contenido nuevo es original (sección 8), pero el riesgo crece con cada fase que agregue más volumen de contenido. Mitigación heredada del roadmap: mantener la regla de "original por defecto, atribución si se usa SRD" como gate de revisión, no solo como nota en un documento.
- **Cobertura de tests multiplicada por locale**: agregar `--locale` y `--audience` multiplica la matriz de combinaciones a probar (formato × locale × audiencia). Mitigación: priorizar tests de contrato (paridad de claves, ausencia de campos `gm` en modo player) sobre tests exhaustivos de cada combinación de flags.

---

## 10. Lista priorizada de tareas para Codex

1. **Rename del proyecto**: `pyproject.toml` (`name`, `project.scripts`, URLs), paquete (decidir si el módulo Python interno se renombra de `world_forge` a `atlasmancer` o se mantiene como detalle interno — recomendado: renombrar también el paquete para consistencia), comando CLI, README, banners de `--help`.
2. **Esqueleto de i18n**: crear `locales/en.json` y `locales/es.json` con las claves de la sección 6 (puede empezar con `es.json` como copia de `en.json` para no bloquear; luego rellenar con los textos de la sección 7).
3. **Loader de locale**: función que carga el JSON correcto, aplica fallback a `en` por clave faltante, y loggea el fallback.
4. **Flag `--locale`**: agregar al parser, validar contra locales disponibles, error traducido si es inválido.
5. **Mover bancos narrativos a locale**: migrar `NPCS`, `HOOKS`, `SECRETS`, `DANGERS`, `REWARDS`, `ODD_RUMORS` de constantes Python hardcodeadas a `content.*` en los JSON de locale, agregando las entradas nuevas de la sección 8.4 y 8.7. Mantener la selección por índice/RNG igual que hoy para no romper determinismo de seeds existentes.
6. **Test de paridad EN/ES**: longitud igual en cada array `content.*` entre ambos locales.
7. **Etiquetas de export en locale**: terreno, tipos de landmark, encabezados de Markdown/HTML (sección 7) leídos desde locale en vez de hardcodeados en `generator.py`/`renderers/html.py`.
8. **`lang` attribute en HTML**: setear `<html lang="en">`/`<html lang="es">` según `--locale`.
9. **Flag `--audience`**: agregar al parser con choices `gm`/`player`, default `gm`.
10. **Lógica de audiencia**: en el ensamblado de cada landmark para export, omitir el bloque `gm` (`secret`/`danger`/`reward`) cuando `audience == player`, en Markdown, HTML y campaign.json.
11. **IDs estables de landmark**: agregar `id` (`lm-01`, `lm-02`, ...) a cada landmark generado, determinista por orden de generación.
12. **`world_id` derivado del seed**: hash corto y estable del seed para usar como `world_id`.
13. **Implementar `--format campaign`**: nuevo renderer que produce el JSON de la sección 5, separado del `to_json()` legacy.
14. **Deprecation notice de `--format json`**: mensaje en `--help` y/o warning en stderr apuntando a `--format campaign`.
15. **`examples/`**: script o comando documentado que regenera los 4 archivos de muestra (EN/ES × GM/player) + su `campaign.json`, para que no queden desincronizados del motor.
16. **Tests de contrato**: schema de `campaign.json`, ausencia de campos `gm` en modo player, no-regresión de `--format plain`/`ansi`/`png` tras el rename.
17. **README**: sección "Idiomas" explicando cómo agregar un locale nuevo; actualizar todos los ejemplos de comandos a `atlasmancer`; mencionar `Atlasmancer.gt.tc` como home futura sin prometer que ya existe.
18. **`CHANGELOG.md`**: registrar el rename como breaking change de la serie 0.x.

Orden recomendado de ejecución: 1 → 2 → 3 → 4 → 5 → 6 (deja el motor renombrado y bilingüe) → 7 → 8 (cierra i18n en exports) → 9 → 10 (cierra audiencia DM/jugador) → 11 → 12 → 13 → 14 (cierra campaign.json) → 15 → 16 → 17 → 18 (cierre y documentación).
