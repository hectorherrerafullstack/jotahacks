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

# --- CONFIGURACIÓN ---
DEBUG = getattr(settings, "DEBUG", False)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
LEAD_TO_EMAIL = os.getenv("LEAD_TO_EMAIL", "")

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
    "Eres el asistente virtual de Héctor, desarrollador especializado en IA y aplicaciones web. "
    "Ayudas a potenciales clientes a definir su idea y conectarlos con Héctor. "
    
    "PRESENTACIÓN: "
    "- NO digas 'Soy Héctor' "
    "- Di 'Hola! Estoy aquí para ayudarte a definir tu idea. Soy el asistente virtual de Héctor' "
    
    "FLUJO CONVERSACIONAL INTELIGENTE: "
    "IMPORTANTE: Eres el asistente virtual de Héctor. NO te presentes en cada mensaje. "
    "Analiza lo que el usuario ya te ha dicho y responde de forma natural y directa. "
    "Si el usuario ya te explicó su situación o proyecto, NO pidas información que ya dio. "
    
    "REGLAS BÁSICAS: "
    "1. NO digas 'Hola, soy el asistente virtual de Héctor' si ya estás en conversación "
    "2. Responde directamente al contenido del mensaje del usuario "
    "3. Si no sabes su nombre: pregúntalo "
    "4. Si no sabes su proyecto: pregunta qué tiene en mente "
    "5. Si ya sabes nombre y proyecto: pide teléfono para que Héctor le llame "
    
    "PERSONALIDAD: "
    "- Habla como una persona real, amigable y profesional "
    "- Una pregunta por vez, clara pero natural "
    "- Respuestas cortas (máximo 2-3 líneas) "
    "- Usa palabras como 'suena', 'me parece', 'genial' para ser más humano "
    "- SOLO contacto por teléfono, no menciones email "
    
    "EJEMPLOS DE RESPUESTAS DIRECTAS: "
    "- Si dice 'no tengo claro mi proyecto': 'Perfecto, te ayudo a definirlo. ¿Cómo te llamas?' "
    "- Si dice 'quiero crear una app/aplicación para mi negocio': '¡Genial! ¿Cómo te llamas?' "
    "- Si dice 'necesito desarrollar un sistema específico': '¡Perfecto! ¿Cómo te llamas?' "
    "- Si ya dijo su nombre: 'Genial, [nombre]! Cuéntame más detalles sobre tu proyecto.' "
    "- Si ya explicó proyecto: 'Suena muy bien, [nombre]! ¿Cuál es tu teléfono para que Héctor te llame?' "
    "- 'Listo, Luis! Héctor te llamará mañana para explorar tu proyecto 📞' "
    
    "IMPORTANTE: Incluye SIEMPRE este JSON al final (el usuario no lo ve): "
    "```json lead\n"
    "{\n"
    '  "name": "", "phone": "", "message": "", "contact_preference": "phone", \n'
    '  "missing": []\n'
    "}\n"
    "```\n"
    "En contact_preference siempre pon 'phone'. En missing lista solo name, phone, message si faltan."
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
    if not GEMINI_API_KEY:
        if DEBUG:
            # Respuesta amable para seguir probando el flujo sin API real
            return JsonResponse({"reply": "Estoy en modo demo (falta GEMINI_API_KEY). Cuéntame objetivo, público y 3 funcionalidades clave."})
        return JsonResponse({"error": "Falta GEMINI_API_KEY"}, status=500)

    # A Gemini
    contents = _history_to_contents(history)
    
    # Construir el prompt base
    base_prompt = ROLE_LOCK
    
    # Si es un mensaje de chip, añadir contexto especial
    if is_chip_message:
        chip_context = (
            "\n\nCONTEXTO ESPECIAL: El usuario acaba de hacer click en una opción rápida. "
            "Este es su primer mensaje en la conversación. Responde DIRECTAMENTE a lo que dice "
            "sin presentarte como 'Hola, soy el asistente virtual de Héctor'. "
            "Ya estás en conversación, actúa naturalmente."
        )
        base_prompt += chip_context
    
    contents.append({"role": "user", "parts": [{"text": user_msg}]})
    body = {
        "contents": [
            {"role": "user", "parts": [{"text": base_prompt}]},
            *contents,
        ],
        "generationConfig": {
            "temperature": 0.65,
            "maxOutputTokens": 380
        }
    }

    try:
        r = requests.post(GEMINI_API_URL, json=body, timeout=20)
        # Si la clave en URL está vacía, Google responderá 400; capturamos abajo
        data = {}
        try:
            data = r.json()
        except Exception:
            pass

        if not r.ok:
            # Manejo específico para error 429 (Too Many Requests)
            if r.status_code == 429:
                fallback_reply = "Disculpa, he recibido muchas consultas. Por favor espera un momento y vuelve a intentar, o puedes llenar el formulario directamente."
                return JsonResponse({
                    "reply": fallback_reply,
                    "error_type": "rate_limit",
                    "is_complete": False
                })
            
            # Otros errores
            msg = (data.get("error", {}) or {}).get("message") or f"HTTP {r.status_code}"
            return JsonResponse({"error": f"Gemini devolvió un error: {msg}"}, status=r.status_code)

        reply = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        ).strip()

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

    except requests.RequestException as e:
        return JsonResponse({"error": f"Fallo de red: {e}"}, status=502)

# --- VISTAS ORIGINALES ---

def home_view(request):
    return render(request, 'website/home.html')

def acerca_view(request):
    return render(request, 'website/acerca.html')

def contacto_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Enviar email
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                message = form.cleaned_data['message']
                
                subject = f"Nuevo mensaje de contacto - {name}"
                body = f"""
Nuevo mensaje de contacto desde el formulario web:

Nombre: {name}
Email: {email}
Mensaje:
{message}
                """
                
                recipient = _lead_recipient()
                if recipient:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
                        recipient_list=[recipient],
                        fail_silently=False,
                    )
                    messages.success(request, '¡Mensaje enviado correctamente! Te contactaré pronto.')
                else:
                    messages.error(request, 'Error en la configuración del email. Inténtalo más tarde.')
                
                return redirect('contacto')
            except Exception as e:
                messages.error(request, 'Error al enviar el mensaje. Inténtalo más tarde.')
                return redirect('contacto')
    else:
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
