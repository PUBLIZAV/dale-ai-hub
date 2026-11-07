# ReelStudio IA V2 — módulo experimental 2 Creativos Digital

La V1 no se modifica. V2 se ejecuta en `http://127.0.0.1:8766` para evitar conflicto con la V1. La API en `/docs` sigue la propuesta de Claude salvo una diferencia **intencional**: `POST /jobs` recibe **multipart/form-data** con archivos cargados desde el navegador (no rutas absolutas arbitrarias). No aceptar rutas externas evita acceso accidental a otros archivos del Mac. El panel podrá cargar archivos por multipart o habilitar un importador desde un directorio autorizado en una siguiente fase.

## Mac M5

1. Descomprimir `ReelStudio_IA_V2.zip` en Descargas.
2. Confirmar FFmpeg: `ffmpeg -version` y Python: `python3 --version`.
3. En Terminal:

```bash
cd ~/Downloads/ReelStudio_IA_V2
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8766
```
4. Abrir `http://127.0.0.1:8766` y documentación API `http://127.0.0.1:8766/docs`.

Se requiere internet *solo para instalar paquetes Python la primera vez*. El render posterior es local. Los trabajos persisten en `~/ReelStudio/jobs/{job_id}`. Solo se procesa uno a la vez. La cola de trabajos en espera en esta versión está en memoria, por lo que un reinicio puede dejar trabajos en estado `queued` sin reanudarlos automáticamente.

## Funciones reales y límites

- Une videos e imágenes por orden de selección con transiciones `xfade` (disolvencia y duración según estilo); entrega 9:16, 4:5, 1:1 a 1080 px de ancho; silencioso, 30 fps, H264.
- No usa IA para seleccionar escenas ni interpretar libremente el brief. El audio del material original y los archivos de música **no se incorporan todavía**. Los títulos, subtítulos, presets de marca y corrección de silencios quedan pendientes.
- `POST /jobs/{job_id}/revisions` puede variar estilo y vuelve a renderizar; no interpreta correcciones generales.
- No publica en redes ni cambia archivos originales.
- Requiere espacio libre; renderiza 3 versiones, en serie, con archivos de trabajo intermedios.

## API

`GET /health`; `GET /presets`; `POST /jobs` (multipart con `files`, `brief`, `duration_seconds`, `style`, `outputs`, `client_id`, `campaign_id`); `GET /jobs/{job_id}`; `GET /jobs/{job_id}/outputs`; `GET /jobs/{job_id}/files/{filename}`; `POST /jobs/{job_id}/revisions` (JSON `{ "style": "dinamico", "notes": "..." }`); `POST /jobs/{job_id}/cancel`.

## Nota de seguridad

El servicio escucha solamente en localhost. No exponerlo en la red. Para un despliegue multiusuario será necesario autenticación, aislamiento, cuotas globales, validación fuerte de archivos y una cola persistente robusta.
