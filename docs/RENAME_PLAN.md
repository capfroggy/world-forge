# Rename Plan: world-forge to Atlasmancer

Estado: en ejecucion

Este plan existe para que el rename tecnico se haga una vez, con cuidado, y sin romper el prototipo actual mientras se implementa v0.2.

## Objetivo

Cambiar el proyecto de `world-forge` a Atlasmancer en producto, repo, paquete, CLI y documentacion.

## Estrategia

Hacer el rename en dos pasos:

1. Preparacion documental.
2. Rename tecnico con compatibilidad temporal.

El paso 1 ya esta completo. v0.2 Bloque A ejecuta el paso 2 sin shim de compatibilidad, siguiendo `docs/ATLASMANCER_V0.2_SPEC.md`.

## Paso 1: Preparacion documental

- [x] Decidir nombre oficial: Atlasmancer.
- [x] Registrar dominio objetivo: `Atlasmancer.gt.tc`.
- [x] Crear decisiones del proyecto.
- [x] Crear base de marca.
- [x] Crear checklist de rename.
- [x] Actualizar roadmap y deployment docs.
- [x] Documentar `world-forge` como nombre anterior hasta ejecutar rename tecnico.

## Paso 2: Rename tecnico

Pendiente.

Cambios esperados:

- [x] Renombrar paquete Python `world_forge` a `atlasmancer`.
- [x] Cambiar paquete instalable `world-forge` a `atlasmancer`.
- [x] Cambiar comando principal `world-forge` a `atlasmancer`.
- [x] No mantener alias temporal `world-forge` durante alpha.
- [x] Actualizar imports internos.
- [x] Actualizar tests.
- [x] Actualizar README.
- [x] Actualizar docs.
- [ ] Actualizar URLs de GitHub cuando el repo sea renombrado.
- [x] Actualizar ejemplos de README.
- [x] Validar `python -m unittest`.
- [x] Validar `atlasmancer --help`.
- [x] Validar que `world-forge` ya no sea instalado por este paquete.

## Compatibilidad recomendada

Durante v0.2:

- `atlasmancer` es el comando nuevo.
- `world-forge` no se mantiene como alias porque el proyecto sigue en alpha.
- `python -m atlasmancer` es la entrada por modulo.

## Riesgos

- Usuarios con instalaciones editables antiguas deben desinstalar `world-forge` si lo tenian instalado.
- Romper imports de tests.
- Confundir usuarios si el repo remoto conserva temporalmente `world-forge` como nombre.
- Dejar URLs antiguas en docs.

## Criterios de aceptacion del rename tecnico

- `python -m unittest` pasa.
- `atlasmancer --help` funciona.
- `world-forge` ya no es instalado por este paquete.
- `python -m atlasmancer` funciona.
- README usa Atlasmancer como nombre principal.
- Docs no presentan World Forge como nombre actual.
- GitHub queda limpio sin archivos generados accidentales.
