# DALE+ AI Command Center (MVP)

Plataforma centralizada de generación, diseño **85% Imagen / 15% Texto** y publicación automatizada para las **48 cuentas de Facebook e Instagram** gestionadas por **DALE+ (Victor Hugo Zavala Gallegos)**.

## Reglas de Diseño Inquebrantables

1. **Fórmula Minimalista 85% Imagen / 15% Texto:**
   - **85% Imagen protagonista:** Producto, platillo, paciente o inmueble ocupando el lienzo principal.
   - **15% Texto en el arte (máx. 8–10 palabras en total):**
     - `visual_headline`: 1 a 3 palabras de alto impacto.
     - `visual_subtext`: Precio o beneficio ultra corto (`1 x $400 | 3 x $900`).
     - `visual_cta`: Pastilla de llamado a la acción (`AGENDA POR WHATSAPP >`).
   - Todo el texto persuasivo, dirección y hashtags viven **únicamente en el copy externo** (`copy`), nunca dentro del arte.
2. **Logo Discreto (`bottom-right-small`):**
   - El logotipo del cliente **nunca es protagonista**. Se ubica siempre pequeño (`5%–7%` del lienzo) en la **esquina inferior derecha**.

---

## Estructura del Proyecto

- `server.py` — Servidor HTTP y API REST local (`http://localhost:8787`) sin dependencias externas.
- `auto_runner.py` — CLI de generación en lote y auditoría automática `85/15` diseñado para **Claude Code / edición automática**.
- `CLAUDE.md` — Manual técnico de arquitectura y reglas para que **Claude** edite y genere contenido sin romper el estándar visual.
- `data/clients_db.json` — Base de datos real con las **48 cuentas** de Facebook/Instagram, IDs de activos de Meta y kits de diseño `85/15`.
- `data/posts_queue.json` — Cola de publicaciones y parrillas semanales activas.
- `public/index.html`, `public/app.js`, `public/styles.css` — Dashboard interactivo + motor HTML5 `<canvas>` (`1080×1080` PNG).
- `public/examples/` — Las 5 imágenes de referencia del estándar visual `85/15`.
- `public/logos/` — Logotipos oficiales de clientes listos para marca de agua en esquina inferior derecha.

---

## Inicio Rápido

```bash
python3 server.py
```
Abre `http://localhost:8787` en tu navegador.

## Comandos para Edición Automática con Claude (`auto_runner.py`)

```bash
# Auditar que toda la cola cumpla la regla 85/15 (<=10 palabras en imagen y logo bottom-right-small)
python3 auto_runner.py --audit-85-15

# Generar parrilla de 5 días para un cliente específico
python3 auto_runner.py --client "Dr. Mariano García" --days 5 --ai claude

# Generar un post puntual por tema
python3 auto_runner.py --client "La Michoacana Plus" --days 1 --topic "Promo 2x1 Mangonadas" --ai gemini
```
