# Deployment Strategy

Estado: decision inicial
Fecha: 2026-06-19

## Decision corta

World Forge debe ser:

1. Open source en GitHub.
2. Web app gratuita como experiencia principal.
3. Local-first y sin login en el MVP.
4. Deploy inicial en hosting estatico, no en InfinityFree.

La recomendacion es:

> Mantener GitHub como fuente de verdad y lanzar una app web estatica/PWA desde el repo. No usar InfinityFree como plataforma principal en esta etapa.

## Por que no elegir solo "software en GitHub"

Ventajas:

- Perfecto para comunidad open source.
- Facil de contribuir.
- Transparente.
- Gratis.
- Bueno para CLI, libreria y releases.

Problemas:

- Muchos DMs no quieren instalar Python.
- La audiencia de D&D espera abrir una web y crear un mapa.
- Las herramientas populares suelen ser visuales.
- GitHub solo como producto limita adopcion no tecnica.

Conclusion:

GitHub es obligatorio, pero no suficiente para el usuario final.

## Por que no elegir InfinityFree como base principal

InfinityFree ofrece cosas utiles:

- Hosting gratis.
- PHP.
- MySQL/MariaDB.
- SSL.
- Dominio propio o subdominio.
- 5 GB de espacio segun su pagina de features.

Pero para World Forge MVP no necesitamos PHP/MySQL.

Riesgos:

- App moderna con mapas grandes se beneficia mas de build/deploy desde GitHub.
- Las campanas deben ser archivos portables/locales al inicio, no bases MySQL compartidas.
- Para datos de usuario, cuentas y privacidad, no conviene improvisar backend gratis.
- Si el proyecto crece, migrar desde PHP/MySQL gratuito puede doler.
- El hosting gratuito se debe tratar como "best effort", no como infraestructura critica.

Conclusion:

InfinityFree puede servir para una landing simple o prueba PHP, pero no como base del producto.

## Opcion recomendada para MVP

### Fase A: GitHub only

Ahora mismo:

- Repo publico.
- CLI.
- Docs.
- Roadmap.
- Issues.
- Releases.

Objetivo:

Construir comunidad tecnica y mantener transparencia.

### Fase B: GitHub Pages o Cloudflare Pages

Cuando exista app web:

- App estatica.
- PWA.
- IndexedDB.
- Export/import `.wforge`.
- Sin login.
- Sin backend.

Ventajas:

- Gratis.
- Integrado con GitHub.
- Deploy automatico.
- Mas adecuado para frontend moderno.
- Menos mantenimiento.

### Fase C: Backend opcional

Solo cuando haga falta:

- Cuentas.
- Sincronizacion cloud.
- Compartir mundos por link.
- Galeria publica.
- Colaboracion multiusuario.

Opciones futuras:

- Supabase.
- Cloudflare Workers + D1/R2.
- Neon/Postgres.
- Railway/Fly.io.
- Servidor propio.

No construir backend antes de validar la app local-first.

## Matriz de decision

| Opcion | Mejor para | Problema |
|---|---|---|
| GitHub repo | Open source, comunidad tecnica, CLI | No es amigable para DMs no tecnicos |
| GitHub Pages | Web estatica desde repo | Sin backend dinamico |
| Cloudflare Pages | Web estatica/PWA con buen free tier | Requiere configurar cuenta/proyecto |
| InfinityFree | PHP/MySQL, WordPress, sitios clasicos | No ideal para app moderna local-first |
| Backend propio | Cuentas, cloud sync, galeria | Mas coste y mantenimiento |

## Decision para los proximos 90 dias

No elegir entre GitHub y web. Hacer ambos, en orden:

1. GitHub open source como base.
2. App web local-first.
3. Deploy estatico.
4. Backend solo despues.

## Plan de lanzamiento

### Semana 1-2

- Roadmap publico.
- README con vision.
- Issues iniciales.
- i18n base.
- Campaign JSON.

### Semana 3-6

- Prototipo web local.
- Render canvas.
- Crear mundo.
- Guardar local.
- Exportar/importar.

### Semana 7-10

- Deploy publico.
- Dominio.
- Demo world.
- Feedback en Reddit/Discord/GitHub.

### Semana 11-12

- Pulir UX.
- Player/GM export.
- Priorizacion basada en feedback.

## Reglas de producto para hosting

- No requerir cuenta para crear un mundo.
- No almacenar mundos del usuario en servidor sin consentimiento.
- Export/import siempre disponible.
- Todo mundo debe poder sobrevivir fuera de la app.
- El core debe seguir siendo open source.
- Si se agrega cloud sync, debe ser opcional.

## Recomendacion final

World Forge debe nacer como:

> Open-source local-first web app.

No como:

- Solo CLI.
- Solo PHP/MySQL.
- Solo SaaS cerrado.
- Solo generador de imagenes.

Esto encaja mejor con la vision: una herramienta gratuita que ayude a mucha gente y que la comunidad pueda mejorar.

## Fuentes revisadas

- InfinityFree features: https://www.infinityfree.com/
- InfinityFree terms: https://www.infinityfree.com/terms/
- GitHub Pages docs: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- Cloudflare Pages limits: https://developers.cloudflare.com/pages/platform/limits/
- D&D SRD: https://www.dndbeyond.com/srd
