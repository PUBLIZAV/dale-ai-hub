# CLAUDE.md — Guía de Arquitectura y Edición Automática para Claude

Este repositorio contiene **DALE+ AI Command Center**, el sistema multi-agente que administra las **48 cuentas de Facebook e Instagram** de Víctor Hugo Zavala Gallegos (Business Portfolio `764586389025151`) orquestando **5 motores de IA** (`Claude`, `ChatGPT`, `Kimi`, `Manus` y `Gemini`).

## 1. Reglas de Diseño Inquebrantables (Sistema Minimalista 85/15)
Cuando edites plantillas, generes prompts o modifiques agentes en este repositorio, **SIEMPRE** debes respetar estas 3 directrices del director creativo:
1. **Proporción 85% Imagen / 15% Texto:**
   - **85% del lienzo:** Fotografía hiperrealista, producto gigante recortado o escena conceptual con amplio espacio negativo.
   - **15% del lienzo:** Texto en pantalla ultra-sintético (**máximo 8 a 10 palabras en total**: Titular de 1–3 palabras + Precio/Promo numérica + Botón corto tipo `AGENDA POR WHATSAPP >`).
2. **Cero Párrafos en la Imagen:** Todo el texto explicativo, storytelling y hashtags van **exclusivamente en el Copy externo (`copy`)**, jamás dentro del arte gráfico.
3. **Regla Estricta de Logo (`bottom-right-small`):**
   - **El logo de cada cliente NUNCA debe ser protagonista.**
   - Debe ubicarse **siempre pequeño y discreto en la esquina inferior derecha** (escala `5%–7%` del lienzo).

## 2. Estructura del Proyecto
- `server.py`: Servidor HTTP y API REST en Python 3 (sin dependencias externas, corre en `http://localhost:8787`).
  - `GET /api/state`: Devuelve el portafolio Meta, las 5 IAs, los 48 clientes/agentes y la cola de publicaciones.
  - `POST /api/generate`: Genera una publicación individual (Copy + Prompt 85/15 + Notas del Consejo de 5 IAs).
  - `POST /api/generate-week`: Genera automáticamente la parrilla semanal de 5 días para un cliente.
  - `POST /api/agent/update`: Edita en caliente el ADN de cualquiera de los 48 agentes (`brand_voice`, `content_pillars`, `design_kit`, `system_prompt`).
  - `POST /api/publish-meta`: Publica directamente hacia Meta Graph API (`/{asset_id}/feed`) o abre el puente directo a Meta Business Suite.
  - `POST /api/client/logo`: Actualiza el logo PNG transparente del cliente para estamparlo en la esquina inferior derecha.
- `auto_runner.py`: Script CLI para generación y edición automática por lotes (ideal para ser ejecutado por Claude Code, hooks o cronjobs).
- `data/clients_db.json`: Base de datos maestra con las **48 cuentas reales** (`asset_id`, `profile_id`, `ig_id`, `agent`, `design_kit`).
- `data/posts_queue.json`: Cola de publicaciones en estados `draft`, `review`, `approved` y `published`.
- `public/index.html`, `public/app.js`, `public/styles.css`: Dashboard Web interactivo + Estudio Multi-IA + Tablero Kanban.
- `public/examples/`: Los 5 diseños maestros de referencia 85/15.
- `public/logos/`: Logos de clientes para estampado automático inferior derecho.

## 3. Comandos Rápidos para Claude (Edición y Ejecución Automática)
```bash
# Iniciar el servidor del Command Center en el puerto 8787
python3 server.py

# Generar automáticamente parrilla para un cliente desde CLI (para automatización con Claude)
python3 auto_runner.py --client "La Michoacana Plus" --days 5

# Auditar que todos los posts en cola cumplan la regla 85/15 (<10 palabras en imagen y logo inferior derecho)
python3 auto_runner.py --audit-85-15
```
