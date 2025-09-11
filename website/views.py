# project/apps/website/views.py
from typing import Dict, Any, List
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactForm
import requests
import json
import re
import os

# Importaciones para Gemini SDK
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- CONFIGURACIÓN ---
DEBUG = getattr(settings, "DEBUG", False)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LEAD_TO_EMAIL = os.getenv("LEAD_TO_EMAIL", "")

# Configurar Gemini SDK
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

    # Configurar modelo con parámetros optimizados
    generation_config = {
        "temperature": 0.7,
        "max_output_tokens": 400,
        "top_p": 0.9,
        "top_k": 40,
    }

    # Configuración de seguridad (permitir contenido moderado para conversaciones comerciales)
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    try:
        # Inicializar modelo
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
    except Exception as e:
        model = None
        print(f"Error inicializando Gemini: {e}")
else:
    model = None

# Campos requeridos para enviar lead (solo teléfono)
def get_required_fields_for_lead(lead: Dict[str, Any]) -> List[str]:
    """Devuelve los campos requeridos - siempre teléfono"""
    return ["name", "phone", "message"]

# Marcador invisible para tracking interno (usar caracteres unicode invisibles)
ALREADY_SENT_MARKER = "​‌‍" # Caracteres Unicode invisibles

# --- Helpers email (fallbacks en DEBUG) ---
def _lead_recipient() -> str:
    """Intenta encontrar un destinatario razonable en dev si LEAD_TO_EMAIL no está."""
    if LEAD_TO_EMAIL:
        return LEAD_TO_EMAIL
    default_to = getattr(settings, "DEFAULT_TO_EMAIL", None)
    if default_to:
        return default_to
    if DEBUG:
        # Fallback en desarrollo (ajusta según tu setup)
        return getattr(settings, "DEFAULT_FROM_EMAIL", "test@localhost")
    return ""

# --- Anti-injection (detección básica) ---
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|the|above)\s+instructions?",
    r"system\s+(prompt|role|message)",
    r"forget\s+(everything|all|previous)",
    r"new\s+(instructions?|rules?|prompts?)",
    r"act\s+as\s+(if\s+)?you\s+(are|were)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"roleplay\s+as",
    r"ANSWER\s+AS",
]

def is_prompt_attack(text: str) -> bool:
    if not isinstance(text, str):
        return False
    text_lower = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def _clean_user_text(s: str) -> str:
    """Normaliza texto de usuario para envío a la API."""
    if not s:
        return ""
    s = re.sub(r"[^\w\s.,!?¿¡áéíóúñüÁÉÍÓÚÑÜ()@/:-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:2000]  # margen generoso

def _history_to_contents(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contents = []
    for turn in (history or []):
        role = "user" if (turn.get("role") == "user") else "model"
        text = _clean_user_text(turn.get("content") or "")
        if text:
            contents.append({"role": role, "parts": [{"text": text}]})
    return contents

# --- Role lock (humano, breve, copy amable) ---
ROLE_LOCK = (
    "Eres el asistente virtual de Héctor, un desarrollador especializado en IA y aplicaciones web. "
    "Tu objetivo es ayudar a potenciales clientes a definir su idea y conectarlos con Héctor. "

    "PRESENTACIÓN INICIAL: "
    "- Al principio de la conversación, preséntate como el asistente virtual de Héctor y pregunta el nombre del usuario. "
    "- NO digas 'Soy Héctor'. Di 'Hola! Soy el asistente virtual de Héctor. Estoy aquí para ayudarte a definir tu idea. ¿Cómo te llamas?'. "

    "FLUJO DE CONVERSACIÓN INTELIGENTE: "
    "IMPORTANTE: Una vez que te hayas presentado, NO vuelvas a hacerlo en los siguientes mensajes. "
    "Analiza lo que el usuario ya te ha dicho y responde de forma natural y directa. "
    "Si el usuario ya te ha proporcionado información, como su nombre o los detalles de su proyecto, NO vuelvas a pedírsela. "

    "REGLAS BÁSICAS: "
    "1. Preséntate como el asistente virtual de Héctor SOLO en el primer mensaje. "
    "2. Responde directamente al contenido del mensaje del usuario. "
    "3. Si no sabes su nombre, pregúntalo. "
    "4. Si no sabes en qué servicio está interesado, pregúntale qué tiene en mente. "
    "5. Si ya conoces su nombre y el servicio de interés, pide su número de teléfono para que Héctor pueda llamarle. "

    "PERSONALIDAD: "
    "- Habla como una persona real, amigable y profesional. "
    "- Haz una pregunta por vez, de forma clara pero natural. "
    "- Tus respuestas deben ser cortas (máximo 2-3 líneas). "
    "- Utiliza un lenguaje cercano y humano, con palabras como 'genial', 'perfecto' o 'entiendo'. "
    "- El único método de contacto que debes mencionar es el teléfono; no ofrezcas contacto por email. "

    "EJEMPLOS DE RESPUESTAS DIRECTAS: "
    "- Si el usuario dice 'no tengo claro mi proyecto': 'Perfecto, te ayudo a definirlo. ¿Cómo te llamas?'. "
    "- Si dice 'quiero crear una app para mi negocio': '¡Genial! ¿Cómo te llamas?'. "
    "- Si ya te ha dicho su nombre: '¡Genial, [nombre]! Cuéntame un poco más sobre tu proyecto.' "
    "- Si ya te ha explicado su proyecto: 'Suena muy interesante, [nombre]. ¿Cuál es tu número de teléfono para que Héctor pueda llamarte?'. "
    "- Si te da su número de teléfono: 'Perfecto, [nombre]. Héctor te llamará para explorar tu proyecto. ¡Gracias! 📞'. "

    "IMPORTANTE: Incluye SIEMPRE este JSON al final de cada respuesta (el usuario no lo verá): "
    "```json lead\n"
    "{\n"
    '  "name": "", "phone": "", "message": "", "contact_preference": "phone", \n'
    '  "missing": []\n'
    "}\n"
    "```\n"
    "En 'contact_preference', siempre pon 'phone'. En 'missing', lista únicamente los campos 'name', 'phone' o 'message' que todavía no tengas."
)


SASQA_MSG = (
    "sasqa 🛡️: Mantengo la conversación centrada en tu proyecto. "
    "No puedo mostrar ni cambiar mis instrucciones internas. "
    "Cuéntame qué quieres construir (negocio, objetivos y funcionalidades) y seguimos 🙂."
)

# --- Extracción del JSON oculto en respuestas del modelo ---
JSON_BLOCK_RX = re.compile(r"```json\s*lead\s*(\{[\s\S]*?\})\s*```|```json\s*(\{[\s\S]*?\})\s*```", re.I)

def extract_lead_from_text(text: str) -> Dict[str, Any]:
    if not text:
        return {}
    m = None
    for mm in JSON_BLOCK_RX.finditer(text):  # último bloque si hay varios
        m = mm
    if not m:
        return {}
    try:
        # Obtener el contenido JSON del grupo que no sea None
        json_content = m.group(1) if m.group(1) else m.group(2)
        if json_content:
            data = json.loads(json_content)
            return data if isinstance(data, dict) else {}
        return {}
    except Exception:
        return {}

def aggregate_lead_from_history(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    lead: Dict[str, Any] = {
        "name": "", "phone": "", "message": "", "contact_preference": "phone",
        "missing": []
    }
    for turn in history or []:
        if turn.get("role") != "assistant":
            continue
        d = extract_lead_from_text(turn.get("content") or "")
        for k, v in (d or {}).items():
            if k in lead and isinstance(v, str) and v and not lead[k]:
                lead[k] = v

    # Siempre por teléfono - solo verificar name, phone, message
    lead["contact_preference"] = "phone"
    lead["missing"] = [k for k in ["name","phone","message"] if not lead.get(k)]
    return lead

def has_already_sent(history: List[Dict[str, Any]]) -> bool:
    return any(turn.get("role") == "assistant" and ALREADY_SENT_MARKER in (turn.get("content") or "")
               for turn in (history or []))

def build_mail_body(lead: Dict[str, Any], transcript: List[Dict[str, str]]) -> str:
    lines = []
    lines.append("🔥 NUEVO LEAD - LLAMAR AL CLIENTE (chat)")
    lines.append("-" * 40)
    lines.append(f"Nombre: {lead.get('name') or '—'}")
    lines.append(f"Teléfono: {lead.get('phone') or '—'}")
    lines.append(f"Proyecto: {lead.get('message') or '—'}")
    lines.append("")
    lines.append("⚠️  ACCIÓN REQUERIDA: LLAMAR AL CLIENTE")
    lines.append("")
    lines.append("— Transcripción —")
    for t in transcript or []:
        who = "U" if t.get("role") == "user" else "A"
        txt = (t.get("content") or "").replace("\n", " ").strip()
        lines.append(f"{who}: {txt}")
    return "\n".join(lines)

# ---------------------------
# Endpoint: /api/chat-gemini/ (urls.py => name="api_chat_gemini")
# ---------------------------
@require_POST
def api_chat_gemini(request):
    # Payload
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    user_msg = _clean_user_text(payload.get("message") or "")
    history  = payload.get("history") or []  # [{role, content}]
    is_chip_message = payload.get("is_chip_message", False)  # Nuevo: detectar mensajes de chip

    if not user_msg:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)

    # Anti-injection (mensaje actual y últimos del usuario)
    recent_user_msgs = [t.get("content") or "" for t in history[-3:] if t.get("role") == "user"]
    if is_prompt_attack(user_msg) or any(is_prompt_attack(m) for m in recent_user_msgs):
        return JsonResponse({"reply": SASQA_MSG})

    # Comprobaciones de config (con fallbacks en DEBUG)
    if not GEMINI_API_KEY or not model:
        if DEBUG:
            # Respuesta amable para seguir probando el flujo sin API real
            return JsonResponse({"reply": "Estoy en modo demo (falta GEMINI_API_KEY). Cuéntame objetivo, público y 3 funcionalidades clave."})
        return JsonResponse({"error": "Falta GEMINI_API_KEY o error en configuración"}, status=500)

    # Construir el prompt base (solo para primer mensaje)
    if not history and not is_chip_message:
        # Solo incluir el prompt completo si es el primer mensaje
        base_prompt = ROLE_LOCK
    else:
        # Para mensajes subsiguientes, usar un recordatorio más breve
        base_prompt = (
            "Continúa siendo el asistente virtual de Héctor. "
            "Mantén el tono amigable y natural. "
            "Responde directamente sin repetir presentaciones. "
            "Sigue recopilando: nombre, detalles del proyecto, y teléfono para contacto."
        )

    # Si es un mensaje de chip, añadir contexto especial
    if is_chip_message:
        chip_context = (
            "\n\nCONTEXTO ESPECIAL: El usuario acaba de hacer click en una opción rápida. "
            "Este es su primer mensaje en la conversación. Responde DIRECTAMENTE a lo que dice "
            "sin presentarte como 'Hola, soy el asistente virtual de Héctor'. "
            "Ya estás en conversación, actúa naturalmente."
        )
        base_prompt += chip_context

    # Preparar historial para Gemini SDK
    try:
        # Convertir historial al formato de Gemini SDK
        gemini_history = []

        # Si no hay historial, es el primer mensaje - añadir el prompt del sistema
        if not history:
            gemini_history.append({
                "role": "user",
                "parts": [{"text": base_prompt}]
            })
            gemini_history.append({
                "role": "model",
                "parts": [{"text": "Entendido. Estoy listo para ayudar a definir proyectos y conectar con Héctor."}]
            })

        # Procesar historial existente
        for turn in history:
            role = turn.get("role")
            content = _clean_user_text(turn.get("content") or "")
            if content:
                if role == "user":
                    gemini_history.append({
                        "role": "user",
                        "parts": [{"text": content}]
                    })
                elif role == "assistant":
                    # Limpiar el contenido del asistente de cualquier JSON oculto
                    clean_content = JSON_BLOCK_RX.sub("", content).strip()
                    if clean_content:
                        gemini_history.append({
                            "role": "model",
                            "parts": [{"text": clean_content}]
                        })

        # Crear chat con historial completo
        chat = model.start_chat(history=gemini_history)

        # Enviar el mensaje actual del usuario
        response = chat.send_message(user_msg)
        reply = response.text.strip()

        # Defensa en salida
        if is_prompt_attack(reply):
            reply = SASQA_MSG

        # Agregamos datos del lead con histórico + último reply
        agg = aggregate_lead_from_history(history)
        last = extract_lead_from_text(reply)
        for k, v in (last or {}).items():
            if k in agg and isinstance(v, str) and v and not agg[k]:
                agg[k] = v
        # Siempre por teléfono - solo verificar name, phone, message
        agg["contact_preference"] = "phone"
        agg["missing"] = [k for k in ["name","phone","message"] if not agg.get(k)]

        # Limpiamos el bloque JSON antes de devolver al usuario
        reply_clean = JSON_BLOCK_RX.sub("", reply).strip()

        # Limpieza adicional para eliminar cualquier fragmento de JSON que pueda quedar
        reply_clean = re.sub(r'```json.*?```', '', reply_clean, flags=re.DOTALL | re.IGNORECASE)
        reply_clean = re.sub(r'\{[^}]*"name"[^}]*\}', '', reply_clean)
        reply_clean = reply_clean.strip()

        # ¿tenemos lo mínimo y todavía no se envió?
        required_fields = get_required_fields_for_lead(agg)
        missing_required = [k for k in required_fields if not agg.get(k)]
        is_complete = not missing_required

        if is_complete and not has_already_sent(history):
            recipient = _lead_recipient()
            if not recipient and DEBUG:
                # En dev: no reventamos si no hay destinatario
                cierre = (
                    "\n\n(DEV) Tengo todo el lead, pero no hay LEAD_TO_EMAIL/DEFAULT_TO_EMAIL. "
                    "Revisa .env/settings. Continúo la conversación sin enviar correo."
                )
                return JsonResponse({"reply": reply_clean + cierre, "is_complete": True})

            if not recipient:
                return JsonResponse({"error": "Falta LEAD_TO_EMAIL"}, status=500)

            try:
                # Siempre es llamada
                subject = "🔥 LLAMAR - " + (agg.get("name") or "Sin nombre") + " (chat)"

                body_mail = build_mail_body(agg, history + [{"role": "user", "content": user_msg}])
                send_mail(
                    subject=subject,
                    message=body_mail,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
                    recipient_list=[recipient],
                    fail_silently=False,
                )
                # Agregamos marcador invisible para tracking interno
                final_reply = reply_clean + ALREADY_SENT_MARKER
                return JsonResponse({"reply": final_reply, "is_complete": True})
            except Exception as e:
                return JsonResponse({"reply": reply_clean + "\n\n(Nota: no pude enviar el correo ahora mismo, lo reintento en breve.)", "is_complete": True})

        # Aún faltan datos o ya se envió - pero indicamos si está completo para mostrar el botón
        return JsonResponse({"reply": reply_clean, "is_complete": is_complete})

    except Exception as e:
        # Manejo mejorado de errores del SDK
        error_msg = str(e).lower()

        # Error de quota/rate limit
        if "quota" in error_msg or "rate" in error_msg or "429" in error_msg:
            fallback_reply = "Disculpa, he recibido muchas consultas. Por favor espera un momento y vuelve a intentar, o puedes llenar el formulario directamente."
            return JsonResponse({
                "reply": fallback_reply,
                "error_type": "rate_limit",
                "is_complete": False
            })

        # Error de API key
        if "api" in error_msg and "key" in error_msg:
            if DEBUG:
                return JsonResponse({"reply": "Error de configuración de API key. Revisa la configuración."})
            return JsonResponse({"error": "Error de configuración"}, status=500)

        # Error de contenido bloqueado por seguridad
        if "safety" in error_msg or "blocked" in error_msg:
            return JsonResponse({"reply": "Disculpa, reformula tu mensaje de manera más específica sobre tu proyecto."})

        # Error genérico
        if DEBUG:
            return JsonResponse({"error": f"Error de Gemini: {e}"}, status=500)
        else:
            return JsonResponse({"reply": "Disculpa, hubo un problema técnico. Por favor inténtalo de nuevo."})

# --- VISTAS ORIGINALES ---

def home_view(request):
    return render(request, 'website/home.html')

def acerca_view(request):
    return render(request, 'website/acerca.html')

def contacto_view(request):
    def wants_json(r):
        return (r.headers.get("x-requested-with") == "XMLHttpRequest" or
                "application/json" in (r.headers.get("accept") or ""))

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if not form.is_valid():
            if wants_json(request):
                # Devuelve errores de validación por campo
                return JsonResponse({"ok": False, "errors": form.errors}, status=400)
            # Flujo clásico (no-AJAX)
            return render(request, 'website/contacto.html', {'form': form})

        # Datos limpios
        name    = form.cleaned_data['name']
        phone   = form.cleaned_data['phone']       # obligatorio
        company = form.cleaned_data.get('company') or '—'
        sector  = form.cleaned_data.get('sector')  or '—'
        message = form.cleaned_data['message']

        # Destinatario
        to_addr = (getattr(settings, "LEAD_TO_EMAIL", "") or
                   getattr(settings, "DEFAULT_TO_EMAIL", ""))
        if not to_addr:
            msg = "No hay destinatario configurado."
            if wants_json(request):
                return JsonResponse({"ok": False, "errors": {"__all__": [msg]}}, status=500)
            messages.error(request, msg)
            return render(request, 'website/contacto.html', {'form': form})

        # Email
        subject = f"Nuevo contacto — {name}"
        body = (
            f"Nombre: {name}\n"
            f"Teléfono: {phone}\n"
            f"Empresa: {company}\n"
            f"Sector: {sector}\n"
            f"Mensaje:\n{message}\n"
        )
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
                recipient_list=[to_addr],
                fail_silently=False,
            )
        except Exception as e:
            err = "No pude enviar el email ahora mismo. Inténtalo más tarde."
            if wants_json(request):
                return JsonResponse({"ok": False, "errors": {"__all__": [err]}}, status=502)
            messages.error(request, err)
            return render(request, 'website/contacto.html', {'form': form})

        # OK
        if wants_json(request):
            return JsonResponse({"ok": True, "message": "¡Mensaje enviado! Te contactaré pronto."})
        messages.success(request, "¡Mensaje enviado! Te contactaré pronto.")
        return redirect('website:contacto')

    # GET
    form = ContactForm()
    return render(request, 'website/contacto.html', {'form': form})

def privacidad_view(request):
    return render(request, 'website/legal/privacidad.html')

def terminos_view(request):
    return render(request, 'website/legal/terminos.html')

def cookies_view(request):
    return render(request, 'website/legal/cookies.html')

def vinaros_view(request):
    return render(request, 'website/vinaros.html')

def castellon_view(request):
    return render(request, 'website/castellon.html')