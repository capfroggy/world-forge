# Project Decisions

Estado: vivo
Ultima actualizacion: 2026-06-19

Este documento guarda las decisiones que no queremos volver a discutir desde cero cada semana.

## 1. Nombre del producto

Decision:

- Nombre oficial: Atlasmancer.
- Nombre anterior/prototipo: world-forge.
- Dominio objetivo: `Atlasmancer.gt.tc`.

Razon:

- "Atlasmancer" comunica atlas, mapas, magia y creacion.
- Funciona razonablemente bien en ingles y espanol.
- Evita usar marcas como D&D en el nombre.
- Tiene personalidad propia para una herramienta de worldbuilding.

Estado:

- Decidido.
- Rename tecnico del paquete y CLI ejecutado en v0.2 Bloque A.
- Pendiente renombrar el repo remoto de GitHub si se decide hacerlo desde la configuracion de GitHub.

## 2. Modelo de producto

Decision:

- Atlasmancer sera open source.
- Atlasmancer sera web-first.
- Atlasmancer sera local-first.
- Atlasmancer no requerira login en el MVP.

Razon:

- GitHub ayuda a construir comunidad y confianza.
- Una web app reduce la friccion para DMs no tecnicos.
- Local-first protege mundos/campanas del usuario y evita backend prematuro.
- Export/import evita lock-in.

## 3. Hosting inicial

Decision:

- Mantener GitHub como fuente de verdad.
- Preparar deploy estatico para la app web futura.
- No usar InfinityFree como base tecnica principal del MVP.

Razon:

- El MVP no necesita PHP/MySQL.
- Una PWA estatica con IndexedDB encaja mejor con local-first.
- El backend debe llegar solo cuando haya necesidad real de cuentas, sincronizacion o galeria.

## 4. Idiomas

Decision:

- Idiomas iniciales: ingles (`en`) y espanol (`es`).
- Todo texto visible debe pasar por i18n en cuanto exista el sistema de locales.
- El fallback sera ingles.

Razon:

- La mayoria del ecosistema TTRPG esta en ingles.
- El soporte en espanol es menor y es una oportunidad importante para diferenciar Atlasmancer.
- Agregar i18n tarde es caro y doloroso.

## 5. Roles de colaboracion

Decision:

- Claude: planificador, product designer, narrativa, templates, UX writing, traducciones.
- Codex: arquitectura tecnica, implementacion, tests, refactors, CI, validacion.
- Humano: vision, gusto, prioridades, pruebas como DM/jugador, decisiones finales.

Razon:

- Separar planificacion y ejecucion evita mezclar ideas con codigo sin control.
- La implementacion necesita pruebas y cambios pequenos.
- La validacion humana decide si la herramienta se siente divertida y util.

## 6. Propiedad intelectual

Decision:

- No copiar contenido protegido de libros oficiales.
- Usar contenido original por defecto.
- Si se usa SRD/Creative Commons, documentar atribucion y limites.
- No nombrar el producto como herramienta "D&D" oficial.

Razon:

- Queremos una herramienta compatible con campanas TTRPG, no dependiente de una marca.
- El proyecto debe ser seguro para open source y uso publico.

## 7. Proxima fase

Decision:

- La siguiente fase es Atlasmancer v0.2 Foundation.

Alcance esperado:

- Rename tecnico controlado.
- Branding base.
- i18n EN/ES.
- Primer `campaign.json`.
- Ejemplos.
- Documentacion para contributors.
- Preparacion para app web local-first.
