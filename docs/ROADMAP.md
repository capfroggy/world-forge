# World Forge Roadmap

Estado: borrador maestro
Idioma base del documento: espanol
Objetivo: convertir `world-forge` en una herramienta gratuita, abierta y multilenguaje para crear mundos completos de D&D/TTRPG.

## 1. Vision

World Forge debe evolucionar de un generador CLI de mapas a una aplicacion completa de worldbuilding para directores de juego y jugadores.

La promesa central:

> Crear, explorar, guardar, editar, imprimir y compartir un mundo de fantasia jugable en un solo lugar.

El usuario deberia poder crear:

- Continentes.
- Regiones.
- Paises/reinos/imperios.
- Fronteras politicas.
- Biomas y clima.
- Montanas, rios, costas, lagos, islas y rutas.
- Ciudades, pueblos, aldeas, fortalezas y ruinas.
- Mazmorras, cuevas, torres, templos y lugares raros.
- Facciones, religiones, gremios y casas nobles.
- NPCs, monstruos, tesoros, rumores y secretos.
- Misiones principales y secundarias.
- Eventos de campana y relojes de amenaza.
- Mapas imprimibles para mesa.
- Mapas "player-safe" sin secretos.
- Mapas "GM-only" con secretos, facciones y ganchos.

El objetivo no es competir solo con generadores de mapas. El objetivo es juntar tres cosas:

1. Generacion procedural.
2. Edicion manual.
3. Preparacion real de partidas.

## 2. Principios de producto

### Gratis y abierto

El core debe ser open source. La comunidad debe poder usarlo, forkearlo, traducirlo y contribuir generadores.

### Local-first

El usuario debe poder crear mundos sin cuenta y sin servidor. El mundo debe guardarse localmente y exportarse como archivo.

### Web-first, pero no web-only

La experiencia principal deberia ser una app web/PWA, porque es la forma mas facil de llegar a DMs. Pero el motor debe poder existir como libreria y CLI.

### Multilenguaje desde el inicio

No hacer textos hardcoded en el motor. Todo contenido visible debe pasar por i18n:

- `en`: ingles.
- `es`: espanol.
- Preparado para agregar `fr`, `pt`, `de`, etc.

### Compatible con mesa real

Cada feature debe responder a una pregunta practica:

- "Puedo usar esto en una sesion esta semana?"
- "Puedo imprimirlo?"
- "Puedo ocultar secretos a los jugadores?"
- "Puedo editar lo generado?"
- "Puedo exportarlo si algun dia la app desaparece?"

### Inspirado, no copiado

Mirar herramientas existentes, pero crear una identidad propia:

- Azgaar: world map + politica + simulacion.
- Inkarnate: mapas bonitos.
- Watabou: ciudades rapidas.
- Donjon: tablas y generadores utiles.
- DungeonScrawl/DungeonFog/Mipui: mapas tacticos.

World Forge debe diferenciarse por ser gratuito, abierto, multilenguaje, local-first y orientado a campanas completas.

## 3. Usuarios objetivo

### DM casual

Quiere un mundo jugable rapido. No quiere configurar cien parametros.

Necesita:

- Boton "Create world".
- Export a PDF/PNG/HTML.
- Hooks, NPCs y misiones.
- Modo jugador/DM.

### DM worldbuilder

Quiere controlar fronteras, historia, idiomas, religiones, rutas comerciales, guerras y secretos.

Necesita:

- Edicion manual.
- Capas de mapa.
- Timeline.
- Relaciones entre entidades.
- Import/export.

### Jugador

Quiere explorar el mapa permitido por el DM y leer notas publicas.

Necesita:

- Player map.
- Lugares descubiertos.
- Diario de viaje.
- Notas compartidas.

### Creador open source

Quiere contribuir generadores, traducciones, temas o exportadores.

Necesita:

- Arquitectura modular.
- Tests.
- Documentacion tecnica.
- Datos en formatos abiertos.

## 4. Alcance por capas

### Capa 1: Motor procedural

Responsable de generar datos coherentes.

Debe producir:

- Terreno.
- Elevacion.
- Humedad.
- Temperatura.
- Biomas.
- Rios.
- Costas.
- Montanas.
- Regiones naturales.
- Sitios candidatos para civilizacion.

### Capa 2: Simulacion de mundo

Responsable de dar logica social y politica.

Debe producir:

- Paises/reinos.
- Capitales.
- Ciudades.
- Pueblos.
- Rutas.
- Recursos.
- Facciones.
- Conflictos.
- Historia breve.
- Relaciones diplomaticas.

### Capa 3: Contenido jugable

Responsable de convertir el mundo en material de mesa.

Debe producir:

- NPCs.
- Misiones.
- Rumores.
- Secretos.
- Dungeons.
- Encuentros.
- Tesoros.
- Complicaciones de viaje.
- Tablas rollables.

### Capa 4: Editor

Responsable de permitir que el usuario cambie lo generado.

Debe permitir:

- Renombrar lugares.
- Mover marcadores.
- Pintar terreno.
- Crear/eliminar ciudades.
- Editar fronteras.
- Editar NPCs/misiones.
- Bloquear elementos para que no cambien al regenerar.

### Capa 5: Presentacion

Responsable de mostrar, imprimir y exportar.

Debe incluir:

- App web.
- CLI.
- PNG.
- HTML imprimible.
- PDF.
- JSON.
- Markdown.
- Player map.
- GM map.
- Export futuro a Foundry/VTT.

## 5. Arquitectura objetivo

### Monorepo recomendado

Estructura futura:

```text
world-forge/
  packages/
    engine-python/
    app-web/
    shared-schema/
    content-packs/
  docs/
  examples/
  tests/
```

Sin embargo, no hay que migrar a monorepo todavia. La primera etapa puede vivir en el repo actual y evolucionar cuando exista la app web.

### Motor

El motor actual esta en Python. Se puede mantener para:

- Prototipado rapido.
- Generacion offline.
- CLI.
- Tests de algoritmos.
- Export batch.

Pero la app web necesita una estrategia:

1. Reescribir parte del motor en TypeScript.
2. Compilar Python a WebAssembly, opcion mas compleja.
3. Mantener motor Python como servidor/API, opcion menos local-first.

Decision recomendada:

- Corto plazo: mantener Python para prototipos y export.
- Mediano plazo: definir schema estable y crear motor TypeScript para web.
- Largo plazo: compartir reglas/datos entre Python y TypeScript mediante schemas y fixtures.

### Datos

Todo mundo debe ser un archivo portable:

```text
my-world.wforge
```

Internamente puede ser:

- ZIP.
- `manifest.json`.
- `world.json`.
- `chunks/*.json` o binario comprimido.
- `assets/`.
- `notes/`.
- `exports/`.

Para MVP web:

- Guardar en IndexedDB.
- Exportar/importar `.wforge`.
- Permitir backup manual.

Para CLI:

- Guardar como JSON o SQLite.

### Identidad estable

Cada entidad debe tener ID:

- `world_id`.
- `continent_id`.
- `region_id`.
- `country_id`.
- `place_id`.
- `npc_id`.
- `quest_id`.
- `faction_id`.

Nunca depender solo de coordenadas o nombres.

### Versionado

Cada mundo debe guardar:

- Version de World Forge.
- Version del schema.
- Version del algoritmo.
- Seed.
- Parametros.
- Idioma base.
- Fecha de creacion.

Esto permite abrir mundos antiguos aunque el generador mejore.

## 6. Modelo de datos inicial

### World

Campos:

- `id`
- `name`
- `seed`
- `schema_version`
- `generator_version`
- `locale`
- `size`
- `created_at`
- `updated_at`
- `settings`

### Continent

Campos:

- `id`
- `world_id`
- `name`
- `bounds`
- `climate_summary`
- `dominant_biomes`
- `regions`

### Region

Campos:

- `id`
- `continent_id`
- `name`
- `kind`
- `biomes`
- `danger_level`
- `travel_tags`
- `description`
- `secrets`

Tipos:

- bosque.
- desierto.
- cordillera.
- costa.
- pantano.
- tundra.
- llanura.
- jungla.
- archipielago.
- tierras malditas.

### Country

Campos:

- `id`
- `name`
- `government`
- `capital_id`
- `regions`
- `culture`
- `laws`
- `resources`
- `allies`
- `rivals`
- `current_crisis`

### Place

Campos:

- `id`
- `name`
- `kind`
- `x`
- `y`
- `region_id`
- `country_id`
- `population`
- `services`
- `tags`
- `public_description`
- `gm_secret`

Tipos:

- capital.
- ciudad.
- pueblo.
- aldea.
- fuerte.
- puerto.
- ruina.
- templo.
- torre.
- mazmorra.
- punto raro.

### NPC

Campos:

- `id`
- `name`
- `role`
- `ancestry`
- `pronouns`
- `personality`
- `desire`
- `fear`
- `secret`
- `relationship_ids`
- `location_id`
- `quest_ids`

### Faction

Campos:

- `id`
- `name`
- `type`
- `goal`
- `method`
- `leader_npc_id`
- `home_place_id`
- `influence_region_ids`
- `allies`
- `rivals`
- `clock`

Tipos:

- gremio.
- culto.
- casa noble.
- compania mercenaria.
- circulo druida.
- iglesia.
- sindicato criminal.
- orden arcana.

### Quest

Campos:

- `id`
- `title`
- `level_range`
- `type`
- `hook`
- `objective`
- `complication`
- `involved_place_ids`
- `involved_npc_ids`
- `involved_faction_ids`
- `reward`
- `failure_consequence`
- `gm_notes`

Tipos:

- investigacion.
- exploracion.
- rescate.
- escolta.
- diplomacia.
- caza de monstruo.
- dungeon crawl.
- misterio.
- guerra.
- intriga.

### Dungeon

Campos:

- `id`
- `name`
- `parent_place_id`
- `theme`
- `entrance`
- `rooms`
- `boss`
- `hazards`
- `treasure`
- `secret`
- `map`

## 7. Roadmap por fases

## Fase 0: Fundacion del repo actual

Objetivo:

Convertir el prototipo CLI en una base mantenible.

Entregables:

- README actualizado con vision grande.
- `docs/ROADMAP.md`.
- `docs/DEPLOYMENT_STRATEGY.md`.
- Carpeta `examples/`.
- Tests mas completos.
- Separar generacion, modelo y render.
- Mantener CLI actual funcionando.

Criterios de aceptacion:

- `python -m unittest` verde.
- El CLI actual sigue funcionando.
- Roadmap y estrategia estan versionados en GitHub.

## Fase 1: Campaign Pack local

Objetivo:

Crear un archivo de mundo guardable y reabrible.

Features:

- Comando `world-forge create`.
- Comando `world-forge open`.
- Comando `world-forge export`.
- Formato `.wforge` inicial o JSON canonical.
- Manifest con seed, version, idioma y parametros.
- Lugares enriquecidos.
- Player/GM data separados.

CLI ideal:

```bash
world-forge create --seed "salt-crown" --locale es --output salt-crown.wforge
world-forge export salt-crown.wforge --format html --output atlas.html
world-forge export salt-crown.wforge --format png --output map.png
```

Criterios:

- Un mundo generado se puede guardar, cerrar, abrir y exportar sin perder datos.
- El export JSON es determinista.
- Existe migracion basica de schema.

## Fase 2: Sistema multilenguaje

Objetivo:

Soporte real para ingles y espanol, preparado para mas idiomas.

Features:

- Archivos `locales/en.json`.
- Archivos `locales/es.json`.
- Catalogos para:
  - UI.
  - terrenos.
  - biomas.
  - tipos de lugar.
  - templates de misiones.
  - nombres de campos.
  - errores.
- Fallback a ingles.
- Tests de claves faltantes.

Regla:

No se aceptan textos nuevos visibles al usuario sin pasar por i18n.

Criterios:

- `--locale en` y `--locale es` generan salidas coherentes.
- El mismo mundo puede renderizarse en ingles o espanol sin cambiar sus IDs.
- Documentacion explica como agregar un idioma.

## Fase 3: Mundo geografico coherente

Objetivo:

Generar continentes, regiones y terreno con logica.

Features:

- Elevacion.
- Temperatura.
- Humedad.
- Placas/cordilleras simplificadas.
- Biomas.
- Costas.
- Rios.
- Lagos.
- Islas.
- Regiones naturales.

Requerimientos tecnicos:

- Coordenadas globales.
- Chunks.
- Ruido deterministico por coordenada global.
- Render por ventana.
- No generar todo el mundo en memoria.

Criterios:

- Mapas de 10,000 x 10,000 tiles son posibles por chunks.
- No hay costuras visibles entre chunks.
- Rios no nacen ni mueren absurdamente en bordes de chunks.
- Cada region tiene nombre, bioma dominante y descripcion.

## Fase 4: Civilizacion

Objetivo:

Convertir geografia en mundo politico y social.

Features:

- Paises/reinos.
- Capitales.
- Ciudades.
- Pueblos.
- Puertos.
- Fronteras.
- Caminos.
- Rutas maritimas.
- Recursos.
- Culturas.
- Conflictos.

Logica:

- Ciudades grandes cerca de agua, rutas o recursos.
- Capitales separadas por distancia.
- Fronteras siguen rios, montanas o regiones.
- Rutas evitan montanas cuando sea posible.
- Puertos aparecen en costas utiles.

Criterios:

- Cada pais tiene capital, gobierno, recurso principal y crisis.
- Cada ciudad tiene servicios y al menos un NPC.
- Cada frontera tiene razon geografica o politica.

## Fase 5: Contenido jugable

Objetivo:

Generar material que un DM pueda usar en sesion.

Features:

- NPCs.
- Facciones.
- Misiones.
- Rumores.
- Secretos.
- Tablas de encuentros.
- Tablas de viaje.
- Recompensas.
- Amenazas.
- Relojes de faccion.

Criterios:

- Cada region tiene al menos:
  - 3 rumores.
  - 2 amenazas.
  - 2 NPCs.
  - 1 faccion.
  - 1 gancho de aventura.
- Cada pais tiene:
  - gobierno.
  - conflicto interno.
  - rival externo.
  - recurso deseado.
- Cada lugar importante tiene:
  - descripcion publica.
  - secreto de DM.
  - NPC.
  - hook.
  - recompensa.

## Fase 6: App web MVP

Objetivo:

Crear una app web usable sin cuenta.

Stack recomendado:

- TypeScript.
- React o Svelte.
- Canvas para mapa.
- IndexedDB para guardado local.
- i18n desde el principio.
- Export/import `.wforge`.

Pantallas:

- Home/Create World.
- World Map.
- Place Inspector.
- Region Inspector.
- Quest Board.
- NPC/Faction Browser.
- Export Center.
- Settings/Language.

Flujo MVP:

1. Usuario entra.
2. Elige idioma.
3. Crea mundo con seed o aleatorio.
4. Ve mapa mundial.
5. Click en ciudad/region.
6. Edita nombres/descripciones.
7. Exporta player map y GM packet.

Criterios:

- Funciona offline despues de cargar.
- No requiere login.
- Guarda en navegador.
- Exporta/importa archivo.
- Soporta ingles y espanol.

## Fase 7: Editor visual

Objetivo:

Permitir que el DM modifique el mundo.

Features:

- Pintar terreno.
- Crear/mover/eliminar lugares.
- Editar paises/regiones.
- Editar rutas.
- Editar fronteras.
- Bloquear entidades.
- Regenerar solo partes no bloqueadas.
- Undo/redo.

Criterios:

- El usuario puede corregir cualquier cosa importante.
- Lo editado no se pierde al exportar/importar.
- Existe historial de cambios basico.

## Fase 8: Mazmorras y mapas tacticos

Objetivo:

Cubrir dungeons y mapas de batalla.

Features:

- Generador de dungeon por lugar.
- Rooms conectadas.
- Trampas.
- Enemigos.
- Tesoro.
- Boss.
- Mapa imprimible.
- Export PNG/PDF.
- Escala de cuadricula.

MVP:

- Dungeons simples de 5 a 12 rooms.
- Tema conectado al lugar.
- Tabla de encuentros.
- Version player y GM.

Criterios:

- Una ruina puede generar una dungeon coherente.
- La dungeon exporta mapa + key de habitaciones.

## Fase 9: Campanas vivas

Objetivo:

Ayudar a mantener una campana con cambios en el tiempo.

Features:

- Timeline.
- Calendario.
- Eventos programados.
- Faction clocks.
- Consecuencias si los jugadores ignoran misiones.
- Diario de sesion.
- Lugares descubiertos.

Criterios:

- Un DM puede registrar una sesion.
- Las facciones avanzan sus objetivos.
- El mundo puede cambiar sin regenerarse entero.

## Fase 10: Comunidad y ecosistema

Objetivo:

Abrir el proyecto a colaboraciones.

Features:

- Plugin/content pack system.
- Packs de nombres.
- Packs de biomas.
- Packs de culturas.
- Packs de misiones.
- Packs de estilos visuales.
- Galeria de mundos exportables.
- Templates comunitarios.

Criterios:

- Un usuario puede instalar un pack sin tocar el core.
- Un traductor puede contribuir idioma sin entender generacion procedural.
- Un artista puede contribuir tema visual.

## 8. Roadmap por releases

### v0.1 actual

- CLI.
- Mapas ASCII.
- Export JSON/Markdown/HTML/PNG.
- Lugares con hooks basicos.

### v0.2 Foundation

- Roadmap formal.
- Reorganizacion modular.
- Tests de CLI/renderers.
- Examples.
- README orientado a producto.
- Primer sistema i18n.

### v0.3 Campaign Pack

- Guardado/carga.
- `.wforge` o JSON canonical.
- Export/import.
- Player/GM split inicial.

### v0.4 Geography Engine

- Chunks.
- Biomas reales.
- Continentes/regiones.
- Rios y costas mejores.

### v0.5 Civilizations

- Paises.
- Ciudades.
- Rutas.
- Fronteras.
- Recursos.

### v0.6 Playable Content

- NPCs.
- Facciones.
- Misiones.
- Rumores.
- Dungeons basicos.

### v0.7 Web MVP

- App web local-first.
- Crear mundo.
- Ver mapa.
- Editar lugares.
- Export/import.
- EN/ES.

### v0.8 Visual Editor

- Pintar.
- Mover lugares.
- Editar fronteras.
- Undo/redo.
- Bloqueo de entidades.

### v0.9 Campaign Mode

- Diario.
- Timeline.
- Faction clocks.
- Estado de mundo.

### v1.0 Public Launch

- Web app estable.
- Documentacion completa.
- Licencia clara.
- Guia de contribucion.
- Deploy publico.
- Demo worlds.
- Soporte EN/ES completo.

## 9. Backlog detallado

### Generacion geografica

- [ ] Heightmap mejorado.
- [ ] Biome map.
- [ ] Moisture map.
- [ ] Temperature map.
- [ ] River network.
- [ ] Lake placement.
- [ ] Coast smoothing.
- [ ] Mountain chains.
- [ ] Region segmentation.
- [ ] Named continents.
- [ ] Named seas.

### Politica/civilizacion

- [ ] Settlement suitability score.
- [ ] Country generation.
- [ ] Border generation.
- [ ] Capital placement.
- [ ] Trade routes.
- [ ] Roads.
- [ ] Ports.
- [ ] Resources.
- [ ] Conflicts.
- [ ] Diplomatic relations.

### D&D/TTRPG content

- [ ] NPC generator.
- [ ] Quest generator.
- [ ] Faction generator.
- [ ] Dungeon generator.
- [ ] Encounter table generator.
- [ ] Treasure generator.
- [ ] Travel complication generator.
- [ ] Rumor truth states.
- [ ] Secrets.
- [ ] Session prep export.

### App web

- [ ] Project setup.
- [ ] i18n setup.
- [ ] Canvas map renderer.
- [ ] Map zoom/pan.
- [ ] Place panel.
- [ ] Region panel.
- [ ] Search.
- [ ] Save to IndexedDB.
- [ ] Export/import `.wforge`.
- [ ] Print/export center.
- [ ] Settings.

### Multilenguaje

- [ ] Locale schema.
- [ ] English catalog.
- [ ] Spanish catalog.
- [ ] Missing key tests.
- [ ] Locale fallback.
- [ ] Translation contribution guide.
- [ ] Content templates by locale.
- [ ] Name generation by locale/culture.

### Open source

- [ ] `CONTRIBUTING.md`.
- [ ] `CODE_OF_CONDUCT.md`.
- [ ] Issue templates.
- [ ] PR template.
- [ ] Good first issues.
- [ ] Architecture docs.
- [ ] Public roadmap.
- [ ] Demo screenshots.

## 10. Legal/IP guardrails

Este proyecto debe tener cuidado con D&D IP.

Reglas:

- No copiar texto de libros oficiales que no este en SRD/Creative Commons.
- No usar nombres protegidos de settings oficiales.
- No usar monstruos o terminos excluidos por Wizards.
- Crear contenido original por defecto.
- Si se usa SRD, incluir atribucion correcta.
- Mantener una capa `ruleset` para permitir otros sistemas en el futuro.

Fuentes utiles:

- SRD 5.2.1: https://www.dndbeyond.com/srd
- Creative Commons BY 4.0: https://creativecommons.org/licenses/by/4.0/

## 11. Colaboracion con Claude y otras IAs

Claude puede ayudar mucho, pero con roles claros.

### Claude

Usarlo para:

- Bancos de nombres.
- Plantillas narrativas.
- Hooks.
- Rumores.
- Facciones.
- NPCs.
- Revision de tono en ingles/espanol.
- UX writing.
- Traducciones iniciales.

No usarlo como unica fuente para:

- Arquitectura.
- Seguridad.
- Licencias.
- Persistencia.
- Algoritmos criticos.

### Codex

Usarlo para:

- Arquitectura.
- Implementacion.
- Tests.
- Refactors.
- Tooling.
- CI.
- Integracion.
- Validacion.

### Humano

Tu rol principal:

- Vision.
- Gusto.
- Priorizacion.
- Probar como DM/jugador.
- Decidir que se siente divertido.
- Decidir que se corta.

## 12. Primera meta concreta

La siguiente meta no debe ser "crear la app completa".

La siguiente meta debe ser:

> World Forge v0.2: un generador local-first, bilingue, exportable y con una vision clara.

Alcance v0.2 recomendado:

- Roadmap.
- Estrategia de despliegue.
- README actualizado.
- `locales/en.json`.
- `locales/es.json`.
- i18n basico en CLI/exports.
- `examples/`.
- Mejoras de mapas imprimibles.
- Primer formato `campaign.json`.

Cuando eso exista, empezamos la app web.
