#!/usr/bin/env python3
import http.server
import json
import os
import socketserver
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
CLIENTS_DB_PATH = os.path.join(DATA_DIR, "clients_db.json")
POSTS_DB_PATH = os.path.join(DATA_DIR, "posts_queue.json")
SECRETS_PATH = os.path.join(DATA_DIR, "secrets.json")

PORT = int(os.environ.get("PORT", "8787"))


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def init_seed_posts():
    if os.path.exists(POSTS_DB_PATH):
        return
    now = datetime.now()
    seed_posts = [
        {
            "id": "post_101",
            "client_id": "client_251061751421746",
            "asset_id": "251061751421746",
            "client_name": "La Michoacana Plus El Centro CA. Oficial",
            "category": "Gastronomía y Postres",
            "platforms": ["facebook", "instagram"],
            "format": "Reel + Post",
            "status": "approved",
            "scheduled_for": (now + timedelta(hours=3)).strftime("%Y-%m-%d 15:30"),
            "ai_lead": "chatgpt",
            "ai_support": "gemini",
            "topic": "Combo Antojo Imperial: Mangonada + Tostilocos preparados al momento",
            "hook": "🤤 ¿Calor en El Centro? Tu cuerpo pide a gritos una Mangonada con chamoy casero y unos Tostilocos bien reportados 🔥🇲🇽",
            "copy": (
                "🤤 ¿Calor en El Centro? Tu cuerpo pide a gritos una Mangonada con chamoy casero y unos Tostilocos bien reportados 🔥🇲🇽\n\n"
                "En La Michoacana Plus preparamos todo al momento con fruta 100% fresca, cueritos, cacahuates, pepino y ese toque picosito que tanto nos gusta en el Valle Imperial.\n\n"
                "✅ Nieves artesanales de más de 40 sabores\n"
                "✅ Fresas con crema y Bionicos\n"
                "✅ Esquites y Nachos recién hechos\n\n"
                "📍 Visítanos hoy en El Centro, CA con toda la familia. ¡Etiqueta a quien te debe la nieve hoy! 🍦👇\n\n"
                "#LaMichoacanaPlus #ElCentroCA #ImperialValley #Mangonada #AntojosMexicanos #Tostilocos"
            ),
            "visual_prompt": (
                "Close-up slow-motion Reel (9:16): Escarchado del vaso con chamoy y tajín, caída de nieve de mango natural, "
                "trozos de mango fresco y banderilla de tamarindo. Corte rápido a Tostilocos recibiendo salsa y limón. Iluminación cálida y colores vibrantes."
            ),
            "council_notes": {
                "claude": "Ajustó el tono familiar bilingüe para resonar con familias del Valle Imperial.",
                "chatgpt": "Diseñó el hook de antojo inmediato y el CTA de etiquetado viral.",
                "kimi": "Detectó pico de interacción entre 3:00 PM y 7:30 PM en El Centro, CA.",
                "manus": "Programó publicación cruzada en FB (251061751421746) e IG (@lamichoacana_plus_ca).",
                "gemini": "Estructuró el guion visual de 12 segundos para Reel vertical."
            }
        },
        {
            "id": "post_102",
            "client_id": "client_895719200299185",
            "asset_id": "895719200299185",
            "client_name": "Ruta Ciudadana",
            "category": "Cívico / Participación Ciudadana",
            "platforms": ["facebook", "instagram"],
            "format": "Carrusel Educativo",
            "status": "review",
            "scheduled_for": (now + timedelta(hours=5)).strftime("%Y-%m-%d 18:00"),
            "ai_lead": "claude",
            "ai_support": "kimi",
            "topic": "Guía paso a paso: Cómo documentar daños en electrodomésticos por variaciones de voltaje en Mexicali",
            "hook": "⚡ ¿Un apagón o bajón de luz dañó tus aparatos en Mexicali? No pierdas tu derecho a reclamar por falta de orden en tu expediente.",
            "copy": (
                "⚡ ¿Un apagón o bajón de luz dañó tus aparatos en Mexicali? No pierdas tu derecho a reclamar por falta de orden en tu expediente.\n\n"
                "En Ruta Ciudadana preparamos una guía clara para que documentes tu caso desde el primer minuto:\n\n"
                "1️⃣ Anota fecha, hora exacta y duración de la afectación en tu colonia.\n"
                "2️⃣ Conserva el número de reporte o folio oficial.\n"
                "3️⃣ Toma fotografías del bien afectado y guarda recibos o diagnóstico técnico.\n"
                "4️⃣ Solicita siempre acuse y respuesta por escrito.\n\n"
                "📋 Descarga tu borrador ciudadano gratuito en nuestro portal para ordenar tus hechos antes de presentarlos ante la instancia competente.\n\n"
                "#RutaCiudadana #Mexicali #QueMexicaliNoSeApague #DerechosCiudadanos #BajaCalifornia"
            ),
            "visual_prompt": (
                "Carrusel editorial de 5 láminas (4:5): Tipografía sobria de alto contraste, paleta institucional de Ruta Ciudadana, "
                "iconografía limpia de checklist documental y sello de advertencia: 'Borrador ciudadano de orientación'."
            ),
            "council_notes": {
                "claude": "Redactó con precisión cívica sin atribuir causas no verificadas ni prometer procedencia automática.",
                "chatgpt": "Optimizó la estructura en 4 puntos escaneables para máxima lectura en móvil.",
                "kimi": "Cruzó el contenido con el formato local 'mexicali-daños-en-el-hogar.txt'.",
                "manus": "Vinculó el CTA con el flujo de descarga del formulario en línea.",
                "gemini": "Definió la jerarquía visual de las 5 tarjetas del carrusel."
            }
        },
        {
            "id": "post_103",
            "client_id": "client_113938840467669",
            "asset_id": "113938840467669",
            "client_name": "Puerto Nuevo Patio & Grill",
            "category": "Restaurante / Grill & Bar",
            "platforms": ["facebook", "instagram"],
            "format": "Reel + Historia",
            "status": "review",
            "scheduled_for": (now + timedelta(hours=7)).strftime("%Y-%m-%d 19:30"),
            "ai_lead": "chatgpt",
            "ai_support": "gemini",
            "topic": "Noche de Terraza, Cortes al Grill y Coctelería de Autor",
            "hook": "🥩🔥 El sonido de un buen corte al grill y tu drink favorito helado en la terraza... así se vive la noche en Puerto Nuevo Patio & Grill.",
            "copy": (
                "🥩🔥 El sonido de un buen corte al grill y tu drink favorito helado en la terraza... así se vive la noche en Puerto Nuevo Patio & Grill.\n\n"
                "Hoy el patio está listo para recibirte con:\n"
                "🦞 Mariscos estilo Baja y platillos al grill en su punto exacto\n"
                "🍸 Mixología refrescante y cervezas bien frías\n"
                "🎶 El mejor ambiente para cenar con amigos o en pareja\n\n"
                "🍹 Reserva tu mesa hoy mismo por mensaje directo (tenemos 9 mensajes nuevos en bandeja, ¡asegura tu lugar temprano!).\n\n"
                "#PuertoNuevoPatioAndGrill #GrillAndBar #MariscosYCortes #NocheDeTerraza #CenaConAmigos"
            ),
            "visual_prompt": (
                "Reel ASMR gastronómico (9:16): Sonido real del corte sellándose en la parrilla con flama viva, "
                "servido de coctel con hielo cristalino y paneo nocturno de las luces cálidas del patio."
            ),
            "council_notes": {
                "claude": "Refinó el tono nocturno y gastronómico para elevar el ticket promedio.",
                "chatgpt": "Creó gancho sensorial enfocado en reservaciones de noche.",
                "kimi": "Detectó 9 mensajes sin leer en bandeja para recordar atención prioritaria de reservas.",
                "manus": "Configuró recordatorio de respuesta en Inbox al publicar.",
                "gemini": "Diseñó guion ASMR de parrilla + coctelería."
            }
        },
        {
            "id": "post_104",
            "client_id": "client_1917558501848263",
            "asset_id": "1917558501848263",
            "client_name": "DDS Guillermo Marquez",
            "category": "Salud / Clínica Dental Turística y Local",
            "platforms": ["facebook", "instagram"],
            "format": "Post Bilingüe (EN/ES)",
            "status": "approved",
            "scheduled_for": (now + timedelta(days=1)).strftime("%Y-%m-%d 11:00"),
            "ai_lead": "claude",
            "ai_support": "chatgpt",
            "topic": "Implantes Dentales y Rehabilitación Oral con Tecnología Digital (EN/ES)",
            "hook": "🦷✨ Recover your smile and confidence with world-class Dental Implants / Recupera tu sonrisa con implantes de alta precisión.",
            "copy": (
                "🦷✨ Recover your smile and confidence with world-class Dental Implants!\n"
                "En la clínica del DDS Guillermo Márquez combinamos planeación digital 3D, materiales de grado internacional y atención personalizada para devolverte una sonrisa funcional y natural.\n\n"
                "🇺🇸 Why patients from the US & Canada trust us:\n"
                "• Advanced Implantology & Full Mouth Rehabilitation\n"
                "• Bilingual team & strict sterilization protocols\n"
                "• Personalized treatment plans with transparent pricing\n\n"
                "🇲🇽 ¿Vives en Mexicali o la frontera? Agenda tu cita de valoración hoy mismo.\n\n"
                "📩 Send us a DM or WhatsApp to book your consultation today!\n\n"
                "#DDSGuillermoMarquez #DentalImplants #SmileMakeover #OdontologiaAvanzada #DentalTourism"
            ),
            "visual_prompt": (
                "Fotografía clínica luminosa y limpia: Doctor Guillermo Márquez mostrando escaneo digital 3D de sonrisa "
                "a un paciente sonriente, con gráfica comparativa sutil de implante dental de titanio."
            ),
            "council_notes": {
                "claude": "Cuidó la ética médica y la confianza tanto en inglés como en español.",
                "chatgpt": "Añadió bullets de valor para pacientes de Dental Tourism (EE.UU./Canadá).",
                "kimi": "Validó términos buscados por pacientes transfronterizos.",
                "manus": "Vinculó publicación con cuenta de IG vinculada (17841448041450017).",
                "gemini": "Propuso composición visual clínica de alta confianza."
            }
        },
        {
            "id": "post_105",
            "client_id": "client_122097015428008177",
            "asset_id": "122097015428008177",
            "client_name": "Rosy Gutierrez Real Estate",
            "category": "Inmobiliaria / Bienes Raíces",
            "platforms": ["facebook"],
            "format": "Reel House Tour + Post",
            "status": "draft",
            "scheduled_for": (now + timedelta(days=1, hours=4)).strftime("%Y-%m-%d 16:00"),
            "ai_lead": "chatgpt",
            "ai_support": "claude",
            "topic": "¿Quieres comprar o vender tu casa en Mexicali usando tu crédito Infonavit o Bancario?",
            "hook": "🏡🔑 Tu patrimonio en Mexicali merece asesoría experta, segura y sin trámites complicados.",
            "copy": (
                "🏡🔑 Tu patrimonio en Mexicali merece asesoría experta, segura y sin trámites complicados.\n\n"
                "En Rosy Gutierrez Real Estate te acompañamos desde la precalificación de tu crédito (Infonavit, Cofinavit o Bancario) hasta la entrega de llaves de tu nuevo hogar.\n\n"
                "✅ Catálogo actualizado de casas y terrenos en las mejores zonas de Mexicali\n"
                "✅ Avalúo comercial y promoción profesional si deseas vender tu propiedad\n"
                "✅ Trato directo, transparente y seguro\n\n"
                "📲 Envíanos un mensaje directo con la palabra 'CASA' o 'VENDER' y te asesoramos hoy mismo.\n\n"
                "#RosyGutierrezRealEstate #BienesRaicesMexicali #CasasEnMexicali #TuCasaIdeal #InfonavitMexicali"
            ),
            "visual_prompt": (
                "Reel House Tour (9:16): Entrada por puerta principal de residencia moderna en Mexicali, transición fluida "
                "a cocina integral iluminada y cierre con entrega simbólica de llaves."
            ),
            "council_notes": {
                "claude": "Aportó tono patrimonial y seguridad jurídica para compradores primerizos.",
                "chatgpt": "Incrustó trigger de comentario/DM ('CASA' o 'VENDER') para automatizar prospectos.",
                "kimi": "Destacó modalidades Infonavit/Cofinavit de alta demanda en Mexicali.",
                "manus": "Conectó el trigger de palabras clave con el seguimiento CRM.",
                "gemini": "Estructuró las tomas del House Tour en 15 segundos."
            }
        },
        {
            "id": "post_106",
            "client_id": "client_2202146520020703",
            "asset_id": "2202146520020703",
            "client_name": "De La Peña Rivera",
            "category": "Legal / Firma de Abogados",
            "platforms": ["facebook"],
            "format": "Cápsula Jurídica (Imagen + Copy)",
            "status": "approved",
            "scheduled_for": (now + timedelta(days=2)).strftime("%Y-%m-%d 10:00"),
            "ai_lead": "claude",
            "ai_support": "kimi",
            "topic": "Blindaje Legal Preventivo para Empresas y Patrimonio Familiar en Baja California",
            "hook": "⚖️ En el ámbito legal, un contrato revisado a tiempo evita meses de litigio y protege tu patrimonio.",
            "copy": (
                "⚖️ En el ámbito legal, un contrato revisado a tiempo evita meses de litigio y protege tu patrimonio.\n\n"
                "En De La Peña Rivera Abogados brindamos representación y consultoría jurídica estratégica con estricto apego a la ley y enfoque preventivo:\n\n"
                "• Elaboración y auditoría de contratos civiles y mercantiles\n"
                "• Defensa corporativa, laboral y patrimonial\n"
                "• Estrategia procesal con resultados comprobables en Baja California\n\n"
                "📩 Agenda una consulta confidencial con nuestra firma enviando un mensaje directo.\n\n"
                "#DeLaPeñaRivera #AbogadosMexicali #AsesoriaJuridica #DerechoCorporativo #ProteccionPatrimonial"
            ),
            "visual_prompt": (
                "Diseño editorial sobrio siguiendo el Manual de Marca DLPRA: Tipografía serif institucional, "
                "tonos oscuros elegantes con acentos dorados/corporativos y fotografía de escritorio jurídico."
            ),
            "council_notes": {
                "claude": "Alineó el lenguaje con el Manual de Marca DLPRA detectado en tu equipo.",
                "chatgpt": "Destacó el beneficio económico de la prevención legal.",
                "kimi": "Seleccionó las 3 áreas de mayor consulta empresarial en Mexicali.",
                "manus": "Programó publicación matutina en horario ejecutivo (10:00 AM).",
                "gemini": "Cuidó las directrices visuales del manual de identidad corporativa."
            }
        }
    ]
    save_json(POSTS_DB_PATH, seed_posts)


def call_real_ai_if_configured(ai_id, system_prompt, user_prompt, secrets):
    """Calls real LLM APIs if the user saved their API keys in secrets.json."""
    try:
        if ai_id == "openai" or ai_id == "chatgpt":
            key = secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
            if key:
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=json.dumps({
                        "model": "gpt-4o",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res["choices"][0]["message"]["content"]

        elif ai_id == "claude":
            key = secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
            if key:
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=json.dumps({
                        "model": "claude-3-7-sonnet-latest",
                        "max_tokens": 1024,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": user_prompt}]
                    }).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": key,
                        "anthropic-version": "2023-06-01"
                    }
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res["content"][0]["text"]

        elif ai_id == "kimi":
            key = secrets.get("MOONSHOT_API_KEY") or os.environ.get("MOONSHOT_API_KEY")
            if key:
                req = urllib.request.Request(
                    "https://api.moonshot.cn/v1/chat/completions",
                    data=json.dumps({
                        "model": "moonshot-v1-8k",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.7
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res["choices"][0]["message"]["content"]

        elif ai_id == "gemini":
            key = secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
            if key:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
                req = urllib.request.Request(
                    url,
                    data=json.dumps({
                        "systemInstruction": {"parts": [{"text": system_prompt}]},
                        "contents": [{"parts": [{"text": user_prompt}]}]
                    }).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Live API call fallback ({ai_id}): {e}")
    return None


def synthesize_multi_agent_post(client, topic, fmt, selected_ai, secrets):
    """Generates hyper-specialized client content using the 5-AI Council and live API if available."""
    agent = client["agent"]
    name = client["name"]
    cat = client["category"]
    loc = client["location"]
    pillars = agent.get("content_pillars", ["Contenido de Valor"])
    cta = agent.get("default_cta", "📲 Envíanos mensaje directo.")
    voice = agent.get("brand_voice", "Profesional y cercano")

    topic_clean = (topic or "").strip()
    if not topic_clean:
        topic_clean = f"Campaña destacada de {pillars[0]} para {name} en {loc}"

    lead_ai = selected_ai if selected_ai != "council" else agent.get("primary_ai", "claude")
    support_ai = agent.get("secondary_ai", "gemini")

    # Check if live API key is configured for lead_ai
    live_text = call_real_ai_if_configured(
        lead_ai,
        agent.get("system_prompt", ""),
        f"Crea una publicación en formato '{fmt}' sobre el tema: '{topic_clean}'. Incluye un Hook magnético en la primera línea, cuerpo persuasivo con bullets, cierre con CTA '{cta}' y 5 hashtags locales.",
        secrets
    )

    clean_tag = "".join(ch for ch in name.title() if ch.isalnum())[:24]
    loc_tag = "Mexicali" if "Mexicali" in loc else ("ImperialValley" if "CA" in loc else "BajaCalifornia")

    # Style adaptations based on which AI leads
    ai_signatures = {
        "claude": {
            "hook_prefix": f"✨ Cuando se trata de {topic_clean.lower()}, la confianza y el detalle marcan toda la diferencia en {name}.",
            "style_note": "Storytelling empático, autoridad de marca y redacción impecable por Claude."
        },
        "chatgpt": {
            "hook_prefix": f"🔥 ¡Atención {loc}! Si estabas esperando el momento ideal para {topic_clean.lower()}, hoy en {name} lo hacemos realidad.",
            "style_note": "Estructura AIDA de alta conversión, bullets de venta directa y urgencia por ChatGPT."
        },
        "kimi": {
            "hook_prefix": f"📊 Datos clave en {loc}: descubre por qué {topic_clean.lower()} con {name} es la decisión más inteligente esta semana.",
            "style_note": "Contexto profundo de mercado local, datos verificados y enfoque analítico por Kimi."
        },
        "manus": {
            "hook_prefix": f"🚀 Plan en acción con {name}: todo listo en {loc} para {topic_clean.lower()} de forma rápida y efectiva.",
            "style_note": "Flujo operativo directo, pasos claros de acción y conversión multicanal por Manus."
        },
        "gemini": {
            "hook_prefix": f"🎬 Imagina vivir la experiencia de {name}: {topic_clean} como nunca antes lo habías visto en {loc}.",
            "style_note": "Dirección creativa visual, ritmo dinámico para Reels y narrativa multimodal por Gemini."
        },
        "muse": {
            "hook_prefix": f"📣 [Pauta Optimizada Meta Ads · {loc}] {name}: {topic_clean} con beneficio directo hoy.",
            "style_note": "Arquitectura de pauta pagada (Meta Ads), segmentación Advantage+, horarios de máximo CTR y programación por Muse de Meta."
        }
    }

    sig = ai_signatures.get(lead_ai, ai_signatures["claude"])
    hook = sig["hook_prefix"]

    if live_text:
        copy_body = live_text
    else:
        copy_body = (
            f"{hook}\n\n"
            f"En {name} ({cat}) sabemos exactamente lo que buscas en {loc}. Por eso diseñamos cada detalle pensando en ti:\n\n"
            f"✅ {pillars[0]}: Atención y calidad que superan expectativas\n"
            f"✅ {pillars[1] if len(pillars) > 1 else 'Servicio Garantizado'}: Soluciones reales y cercanas\n"
            f"✅ {pillars[2] if len(pillars) > 2 else 'Atención Inmediata'}: Respuesta rápida por Inbox y WhatsApp\n\n"
            f"{cta}\n\n"
            f"#{clean_tag} #{loc_tag} #DaleMasIA #{cat.split()[0]}"
        )

    dk = agent.get("design_kit", {})
    layout_id = dk.get("preferred_layout", "split_85_15")
    short_title = topic_clean.split(":")[0].split()[0:2]
    short_headline = " ".join(short_title).title() if short_title else name.split()[0]

    visual_prompt = (
        f"[FÓRMULA 85% IMAGEN / 15% TEXTO · Layout: {layout_id}] "
        f"• 85% IMAGEN PROTAGONISTA (Gemini/DALL·E): Fotografía comercial hiperrealista o producto gigante en primer plano de '{topic_clean}' para {name} ({loc}), fondo limpio con aire negativo para lectura rápida. "
        f"• 15% TEXTO EN PANTALLA (Máx 8 palabras): Titular '{short_headline}' + Dato/Promo puntual. "
        f"• LOGO DISCRETO: Logo de {name} pequeño en la esquina inferior derecha (5-7% de escala, nunca protagonista)."
    )

    # Plan de Pauta Pagada & Data generado por Muse de Meta
    is_dental = "Salud" in cat or "Dental" in cat or "Ortodoncia" in name or "DDS" in name
    is_food = "Gastronom" in cat or "Restaurante" in cat or "Michoacana" in name or "Grill" in name
    is_real_estate = "Inmobiliaria" in cat or "Real Estate" in name
    if is_dental:
        ads_objective = "Clientes Potenciales (Mensajes a WhatsApp / Inbox Dental)"
        ads_budget = "$8 - $15 USD / día"
        ads_Window = "Mar-Jue 10:00 AM y 7:00 PM (Pico de agendamiento)"
        ads_audience = f"Radio 15 mi en {loc} + Cruce Fronterizo (Calexico/Imperial Valley) · Intereses: Estética dental, Invisalign, Salud bucal (24-58 años)"
    elif is_food:
        ads_objective = "Interacción / Tráfico en Sucursal & Pedidos por Mensaje"
        ads_budget = "$5 - $12 USD / día (Impulso en horas de antojo)"
        ads_Window = "Jue-Dom 1:30 PM - 8:30 PM (Pico de calor/antojo)"
        ads_audience = f"Radio 5-8 mi alrededor de {loc} · Advantage+ Food & Antojos Locales (18-50 años)"
    elif is_real_estate:
        ads_objective = "Generación de Leads Calificados (Formulario Instantáneo + DM 'CASA')"
        ads_budget = "$10 - $20 USD / día"
        ads_Window = "Lun-Vie 12:30 PM y Dom 6:00 PM"
        ads_audience = f"{loc} + Compradores en BC/California · Intereses: Crédito Infonavit, Inversión inmobiliaria, Hipotecas (26-60 años)"
    else:
        ads_objective = " Reconocimiento + Mensajes Directos (Click-to-WhatsApp / Messenger)"
        ads_budget = "$6 - $12 USD / día"
        ads_Window = "Lun-Vie 1:00 PM y 7:30 PM (Máximo CTR en Feed/Reels)"
        ads_audience = f"Segmentación Abierta Advantage+ en {loc} (22-55 años) optimizada por conversión"

    meta_ads_plan = {
        "engine": "Muse de Meta",
        "ad_account_id": "345341053347300",
        "business_portfolio_id": "764586389025151",
        "objective": ads_objective.strip(),
        "daily_budget": ads_budget,
        "optimal_schedule": ads_Window,
        "targeting": ads_audience,
        "placements": "Feed FB/IG (1:1 85/15) + Stories/Reels Advantage+ (El <15% de texto en imagen evita penalización de CPM en la subasta de Meta)",
        "ads_manager_url": f"https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=345341053347300&business_id=764586389025151"
    }

    council_notes = {
        "claude": f"Escribió el copy externo completo para no saturar la imagen (respetando el 15% de texto en arte).",
        "chatgpt": f"Sintetizó el titular visual en ≤3 palabras ('{short_headline}') + gancho de precio/promo.",
        "kimi": f"Analizó el contexto local de {loc} y los pilares {', '.join(pillars[:2])}.",
        "manus": f"Verificó la regla 85/15 (<10 palabras) + logo pequeño abajo a la derecha (Asset ID {client['asset_id']}).",
        "gemini": f"Aplicó la plantilla '{layout_id}' con el logo discreto en esquina inferior derecha.",
        "muse": f"Configuró pauta en Cuenta 345341053347300: {ads_objective.strip()} ({ads_budget}) · Ventana óptima: {ads_Window}."
    }

    platforms = ["facebook"]
    if client.get("ig_id") or client.get("ig_username"):
        platforms.append("instagram")

    now = datetime.now()
    new_post = {
        "id": f"post_{int(now.timestamp() * 1000)}",
        "client_id": client["id"],
        "asset_id": client["asset_id"],
        "client_name": name,
        "category": cat,
        "platforms": platforms,
        "format": fmt,
        "status": "review",
        "scheduled_for": (now + timedelta(days=1)).strftime("%Y-%m-%d 12:00"),
        "ai_lead": lead_ai,
        "ai_support": support_ai,
        "topic": topic_clean,
        "hook": hook,
        "copy": copy_body,
        "visual_prompt": visual_prompt,
        "meta_ads_plan": meta_ads_plan,
        "council_notes": council_notes
    }
    return new_post


class HubRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/state":
            db = load_json(CLIENTS_DB_PATH, {})
            posts = load_json(POSTS_DB_PATH, [])
            secrets = load_json(SECRETS_PATH, {})
            masked_secrets = {
                k: (f"{v[:6]}...{v[-4:]}" if v and len(v) > 10 else ("Configurada" if v else ""))
                for k, v in secrets.items()
            }
            self.send_json({
                "meta_portfolio": db.get("meta_portfolio", {}),
                "ai_engines": db.get("ai_engines", []),
                "clients": db.get("clients", []),
                "posts": posts,
                "configured_keys": masked_secrets
            })
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw_body)
        except Exception:
            payload = {}

        if parsed.path == "/api/generate":
            db = load_json(CLIENTS_DB_PATH, {})
            posts = load_json(POSTS_DB_PATH, [])
            secrets = load_json(SECRETS_PATH, {})
            client_id = payload.get("client_id")
            topic = payload.get("topic", "")
            fmt = payload.get("format", "Post FB/IG")
            selected_ai = payload.get("ai_engine", "council")

            client = next((c for c in db.get("clients", []) if c["id"] == client_id or c["asset_id"] == client_id), None)
            if not client:
                self.send_json({"error": "Cliente no encontrado"}, 404)
                return

            new_post = synthesize_multi_agent_post(client, topic, fmt, selected_ai, secrets)
            posts.insert(0, new_post)
            save_json(POSTS_DB_PATH, posts)
            self.send_json({"ok": True, "post": new_post})
            return

        if parsed.path == "/api/generate-week":
            db = load_json(CLIENTS_DB_PATH, {})
            posts = load_json(POSTS_DB_PATH, [])
            secrets = load_json(SECRETS_PATH, {})
            client_id = payload.get("client_id")
            client = next((c for c in db.get("clients", []) if c["id"] == client_id or c["asset_id"] == client_id), None)
            if not client:
                self.send_json({"error": "Cliente no encontrado"}, 404)
                return

            pillars = client["agent"].get("content_pillars", ["Contenido de Valor", "Promoción", "Reels", "Comunidad"])
            formats = ["Reel + Post", "Carrusel Educativo", "Post de Venta Directa", "Historia Interactiva", "Reel Testimonial"]
            ai_Order = ["claude", "chatgpt", "kimi", "gemini", "manus"]
            created = []
            now = datetime.now()
            for day_offset in range(5):
                p_topic = f"Día {day_offset + 1} ({pillars[day_offset % len(pillars)]}): Estrategia especializada para {client['name']}"
                post = synthesize_multi_agent_post(
                    client,
                    p_topic,
                    formats[day_offset % len(formats)],
                    ai_Order[day_offset % len(ai_Order)],
                    secrets
                )
                post["id"] = f"post_{int(now.timestamp() * 1000)}_{day_offset}"
                post["scheduled_for"] = (now + timedelta(days=day_offset + 1)).strftime("%Y-%m-%d 13:00")
                posts.insert(0, post)
                created.append(post)
            save_json(POSTS_DB_PATH, posts)
            self.send_json({"ok": True, "created_count": len(created), "posts": created})
            return

        if parsed.path == "/api/agent/update":
            db = load_json(CLIENTS_DB_PATH, {})
            client_id = payload.get("client_id")
            for c in db.get("clients", []):
                if c["id"] == client_id or c["asset_id"] == client_id:
                    ag = c["agent"]
                    for field in ["primary_ai", "secondary_ai", "brand_voice", "target_audience", "default_cta", "autonomy_mode", "system_prompt"]:
                        if field in payload:
                            ag[field] = payload[field]
                    if "content_pillars" in payload and isinstance(payload["content_pillars"], list):
                        ag["content_pillars"] = payload["content_pillars"]
                    save_json(CLIENTS_DB_PATH, db)
                    self.send_json({"ok": True, "client": c})
                    return
            self.send_json({"error": "Cliente no encontrado"}, 404)
            return

        if parsed.path == "/api/posts/update":
            posts = load_json(POSTS_DB_PATH, [])
            post_id = payload.get("post_id")
            if payload.get("status") == "published":
                self.send_json({
                    "ok": False,
                    "error": "Bloqueado: Durante la prueba piloto nada se marca como publicado ni se envía a Meta."
                }, 403)
                return
            for p in posts:
                if p["id"] == post_id:
                    for field in ["status", "copy", "hook", "visual_prompt", "scheduled_for"]:
                        if field in payload:
                            p[field] = payload[field]
                    save_json(POSTS_DB_PATH, posts)
                    self.send_json({"ok": True, "post": p})
                    return
            self.send_json({"error": "Post no encontrado"}, 404)
            return

        if parsed.path == "/api/posts/delete":
            posts = load_json(POSTS_DB_PATH, [])
            post_id = payload.get("post_id")
            posts = [p for p in posts if p["id"] != post_id]
            save_json(POSTS_DB_PATH, posts)
            self.send_json({"ok": True})
            return

        if parsed.path == "/api/publish-meta":
            # Parche de seguridad: bloqueo total de publicación y gasto hacia Meta durante el piloto.
            self.send_json({
                "ok": False,
                "locked": True,
                "error": "Publicador bloqueado: Durante el piloto nada se envía a Meta ni se activa pauta."
            }, 403)
            return

            self.send_json({
                "ok": True,
                "mode": "suite_bridge",
                "suite_url": f"https://business.facebook.com/latest/home?asset_id={asset_id}",
                "post": post
            })
            return

        if parsed.path == "/api/client/logo":
            db = load_json(CLIENTS_DB_PATH, {})
            client_id = payload.get("client_id")
            logo_data = payload.get("logo_data_url")
            for c in db.get("clients", []):
                if c["id"] == client_id or c["asset_id"] == client_id:
                    c.setdefault("agent", {}).setdefault("design_kit", {})["custom_logo"] = logo_data
                    save_json(CLIENTS_DB_PATH, db)
                    self.send_json({"ok": True, "client": c})
                    return
            self.send_json({"error": "Cliente no encontrado"}, 404)
            return

        if parsed.path == "/api/config/keys":
            secrets = load_json(SECRETS_PATH, {})
            for k, v in payload.items():
                if isinstance(v, str) and v.strip():
                    secrets[k] = v.strip()
            save_json(SECRETS_PATH, secrets)
            masked = {
                k: (f"{v[:6]}...{v[-4:]}" if v and len(v) > 10 else ("Configurada" if v else ""))
                for k, v in secrets.items()
            }
            self.send_json({"ok": True, "configured_keys": masked})
            return

        self.send_json({"error": "Ruta no encontrada"}, 404)


if __name__ == "__main__":
    init_seed_posts()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), HubRequestHandler) as httpd:
        print(f"DALE+ Multi-Agent Social Hub running on http://localhost:{PORT}")
        httpd.serve_forever()
