# backend/controladores/analisisController.py

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from config.conexion import get_supabase, get_supabase_admin
from PIL import Image
import io
import uuid
from datetime import datetime
import numpy as np
from tensorflow import keras
import tensorflow as tf
from trayendo_modelo import model as modelo

router = APIRouter(prefix="/analisis", tags=["Análisis"])



# FUNCIÓN: OBTENER INFORMACIÓN DE VULNERABILIDAD

async def obtener_informacion_vulnerabilidad(persona_id: str, supabase):
    """
    Obtiene la información de vulnerabilidad del perfil de salud.
    Esta información es INDEPENDIENTE del diagnóstico de la radiografía.
    """
    try:
        response = (
            supabase.table("perfil_salud")
            .select("*")
            .eq("persona_id", persona_id)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            perfil = response.data[0]
            
            return {
                "nivel_vulnerabilidad": perfil.get("nivel_vulnerabilidad", "DESCONOCIDA"),
                "prioridad_atencion": perfil.get("prioridad_atencion", "MEDIA"),
                "explicacion": f"Paciente con vulnerabilidad {perfil.get('nivel_vulnerabilidad', 'desconocida').lower()} según perfil de salud registrado.",
                "tiene_perfil": True
            }
        else:
            return {
                "nivel_vulnerabilidad": "NO_REGISTRADA",
                "prioridad_atencion": "MEDIA",
                "explicacion": "No se encontró perfil de salud registrado para este paciente.",
                "tiene_perfil": False
            }
    except Exception as e:
        print(f"Error obteniendo vulnerabilidad: {e}")
        return {
            "nivel_vulnerabilidad": "ERROR",
            "prioridad_atencion": "MEDIA",
            "explicacion": "Error al obtener información de vulnerabilidad.",
            "tiene_perfil": False
        }



# FUNCIÓN: GENERAR EXPLICACIÓN DEL ANÁLISIS

def generar_explicacion_analisis(diagnostico: str, confianza: float, vulnerabilidad_info: dict) -> dict:
    """
    Genera una explicación que COMBINA pero NO MEZCLA:
    1. El diagnóstico médico de la radiografía (NORMAL/PNEUMONIA)
    2. La información de vulnerabilidad del paciente (del perfil de salud)
    
    IMPORTANTE: El diagnóstico y la vulnerabilidad son INDEPENDIENTES.
    """
    
    
    # PARTE 1: EXPLICACIÓN DEL DIAGNÓSTICO (RADIOGRAFÍA)
    
    if diagnostico == "NORMAL":
        diagnostico_explicacion = f"""
DIAGNÓSTICO DE LA RADIOGRAFÍA: NORMAL
- Confianza del modelo: {confianza}%
- El modelo de IA no detectó patrones asociados con neumonía en esta radiografía.
- Las estructuras pulmonares aparecen dentro de parámetros normales según el análisis automatizado.
"""
    else:  # PNEUMONIA
        diagnostico_explicacion = f"""
DIAGNÓSTICO DE LA RADIOGRAFÍA: NEUMONÍA DETECTADA
- Confianza del modelo: {confianza}%
- El modelo de IA identificó patrones consistentes con neumonía en esta radiografía.
- Se detectaron opacidades o consolidaciones que sugieren proceso infeccioso pulmonar.
- IMPORTANTE: Este es un análisis preliminar, se requiere confirmación médica profesional.
"""
    
    
    # PARTE 2: INFORMACIÓN DE VULNERABILIDAD (PERFIL DE SALUD)
    
    if vulnerabilidad_info["tiene_perfil"]:
        nivel = vulnerabilidad_info["nivel_vulnerabilidad"]
        prioridad = vulnerabilidad_info["prioridad_atencion"]
        
        vulnerabilidad_explicacion = f"""
PERFIL DE VULNERABILIDAD DEL PACIENTE: {nivel}
- Nivel de vulnerabilidad: {nivel}
- Prioridad de atención sugerida: {prioridad}
- {vulnerabilidad_info["explicacion"]}

Esta evaluación se basa en:
  • Edad y condición demográfica
  • Situación socioeconómica
  • Acceso a servicios de salud
  • Historial de COVID-19 y secuelas
"""
    else:
        vulnerabilidad_explicacion = """
PERFIL DE VULNERABILIDAD: NO DISPONIBLE
- No se cuenta con información de perfil de salud registrado.
- Se recomienda completar el perfil para una evaluación más personalizada.
"""
    
    
    # PARTE 3: RECOMENDACIÓN COMBINADA (CONTEXTO)
    
    if diagnostico == "NORMAL":
        if vulnerabilidad_info.get("nivel_vulnerabilidad") == "ALTA":
            recomendacion = """
RECOMENDACIÓN:
✅ La radiografía muestra patrones normales.
⚠️ Sin embargo, dado su perfil de ALTA vulnerabilidad, se recomienda:
  - Mantener chequeos médicos periódicos
  - Estar atento a cualquier síntoma respiratorio
  - Priorizar acceso a atención médica ante síntomas
  - Seguir medidas preventivas de salud respiratoria
"""
        else:
            recomendacion = """
RECOMENDACIÓN:
✅ La radiografía muestra patrones normales.
✅ Continuar con chequeos médicos de rutina según indicación profesional.
"""
    else:  # PNEUMONIA
        if vulnerabilidad_info.get("nivel_vulnerabilidad") == "ALTA":
            recomendacion = """
RECOMENDACIÓN URGENTE:
🚨 NEUMONÍA DETECTADA + VULNERABILIDAD ALTA
⚠️ Esta combinación requiere ATENCIÓN MÉDICA INMEDIATA:
  - Acudir a urgencias o centro de salud LO ANTES POSIBLE
  - El perfil de alta vulnerabilidad aumenta el riesgo de complicaciones
  - NO esperar a que los síntomas empeoren
  - Llevar esta información al médico tratante
  
PRIORIDAD: ALTA - ATENCIÓN URGENTE REQUERIDA
"""
        elif vulnerabilidad_info.get("nivel_vulnerabilidad") == "MEDIA":
            recomendacion = """
RECOMENDACIÓN PRIORITARIA:
⚠️ NEUMONÍA DETECTADA + VULNERABILIDAD MEDIA
⚠️ Se requiere ATENCIÓN MÉDICA PRONTA:
  - Consultar con médico en las próximas 24-48 horas
  - El perfil de vulnerabilidad media requiere seguimiento cercano
  - Monitorear síntomas (fiebre, dificultad respiratoria, dolor)
  - Llevar esta información al médico tratante
  
PRIORIDAD: MEDIA-ALTA - CONSULTA MÉDICA PRONTO
"""
        else:
            recomendacion = """
RECOMENDACIÓN:
⚠️ NEUMONÍA DETECTADA
⚠️ Se requiere EVALUACIÓN MÉDICA:
  - Consultar con médico profesional
  - Confirmar diagnóstico con estudios adicionales
  - Iniciar tratamiento apropiado según indicación médica
  - Llevar esta información al médico tratante
  
PRIORIDAD: CONSULTA MÉDICA NECESARIA
"""
        # EXPLICACIÓN DEL NIVEL DE CONFIANZA
    explicacion_confianza = f"""
    ¿QUÉ SIGNIFICA EL NIVEL DE CONFIANZA?
    - La confianza representa el grado de seguridad del modelo al comparar las posibles clases (NORMAL vs NEUMONÍA).
    - Un valor inferior al 80% NO significa que el diagnóstico sea incorrecto.
    - Indica que existen características compartidas entre ambas clases o que la imagen presenta patrones sutiles.
    - El modelo selecciona la clase con mayor probabilidad relativa, aunque la diferencia no sea extrema.
    - En pruebas clínicas y de IA médica, es común obtener diagnósticos correctos con niveles de confianza moderados (60–75%).

    El diagnóstico mostrado corresponde a la opción más probable según el análisis automatizado,
    pero SIEMPRE debe ser interpretado como apoyo a la decisión médica, no como veredicto final.
    """

    
    # EXPLICACIÓN COMPLETA
    
    explicacion_detallada = f"""
{diagnostico_explicacion}


{vulnerabilidad_explicacion}

{explicacion_confianza}

{recomendacion}


NOTA IMPORTANTE:
Este análisis combina:
1. Diagnóstico automatizado de la radiografía (modelo de IA)
2. Evaluación de vulnerabilidad según perfil de salud del paciente

Ambos son factores INDEPENDIENTES que se consideran juntos para dar
una recomendación contextualizada. El diagnóstico de la radiografía
NO cambia según la vulnerabilidad, pero la urgencia de atención SÍ
se ajusta considerando el perfil del paciente.

⚕️ SIEMPRE consulte con un profesional médico calificado.
"""
    
    
    # MENSAJE CORTO PARA LA INTERFAZ
    
    if diagnostico == "NORMAL":
        mensaje_corto = "Radiografía normal. Continuar con chequeos de rutina."
    else:
        if vulnerabilidad_info.get("nivel_vulnerabilidad") == "ALTA":
            mensaje_corto = "🚨 Neumonía detectada en paciente de ALTA vulnerabilidad. Atención URGENTE requerida."
        elif vulnerabilidad_info.get("nivel_vulnerabilidad") == "MEDIA":
            mensaje_corto = "⚠️ Neumonía detectada en paciente con vulnerabilidad media. Consulta médica PRONTA."
        else:
            mensaje_corto = "⚠️ Neumonía detectada. Consulta médica necesaria."
    
    return {
        "explicacion_detallada": explicacion_detallada.strip(),
        "mensaje_corto": mensaje_corto
    }



# ENDPOINT: SUBIR ANÁLISIS (USUARIOS AUTENTICADOS)

@router.post("/subir")
async def subir_analisis(
    imagen: UploadFile = File(...),
    request: Request = None
):
    """
    Endpoint para subir análisis para usuarios autenticados.
    Incluye diagnóstico + información de vulnerabilidad del perfil.
    """
    if modelo is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")

    if not hasattr(request.state, 'persona') or not request.state.persona:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")

    try:
        persona_id = request.state.persona["id"]
        contenido = await imagen.read()
        
        # Procesar imagen
        img = Image.open(io.BytesIO(contenido)).convert("RGB").resize((224, 224))
        arr = keras.preprocessing.image.img_to_array(img)
        arr = np.expand_dims(arr, axis=0)

        # Predicción
        pred = modelo.predict(arr, verbose=0)[0]
        prob = tf.nn.softmax(pred).numpy()
        
        clases = ["NORMAL", "PNEUMONIA"]
        idx = int(np.argmax(prob))

        diagnostico = clases[idx]
        confianza = round(float(prob[idx] * 100), 2)
        probabilidades = {
            "normal": float(prob[0]),
            "neumonia": float(prob[1]),
        }

        # Subir a storage
        supabase_admin = get_supabase_admin()
        nombre_archivo = f"{persona_id}/{uuid.uuid4()}.jpg"
        
        supabase_admin.storage.from_("radiografias").upload(
            nombre_archivo,
            contenido,
            {"content-type": imagen.content_type},
        )
        
        url = supabase_admin.storage.from_("radiografias").get_public_url(nombre_archivo)

        # Obtener vulnerabilidad
        vulnerabilidad_info = await obtener_informacion_vulnerabilidad(persona_id, supabase_admin)
        
        # Generar explicación
        explicacion_info = generar_explicacion_analisis(
            diagnostico,
            confianza,
            vulnerabilidad_info
        )

        # Guardar en BD
        analisis_data = {
            "id": str(uuid.uuid4()),
            "persona_id": persona_id,
            "imagen_url": url,
            "diagnostico": diagnostico,
            "confianza": confianza,
            "probabilidades": probabilidades,
            "fecha": datetime.now().isoformat(),
            "nivel_vulnerabilidad_paciente": vulnerabilidad_info["nivel_vulnerabilidad"],
            "prioridad_atencion_sugerida": vulnerabilidad_info["prioridad_atencion"],
            "explicacion_vulnerabilidad": vulnerabilidad_info["explicacion"],
            "detalles_analisis": explicacion_info["explicacion_detallada"]
        }

        supabase_admin.table("analisis_radiografias").insert(analisis_data).execute()

        return {
            "success": True,
            "data": {
                "diagnostico": diagnostico,
                "confianza": confianza,
                "probabilidades": probabilidades,
                "vulnerabilidad": {
                    "nivel": vulnerabilidad_info["nivel_vulnerabilidad"],
                    "prioridad": vulnerabilidad_info["prioridad_atencion"],
                    "explicacion": vulnerabilidad_info["explicacion"]
                },
                "detalles_analisis": explicacion_info["explicacion_detallada"],
                "nivel_vulnerabilidad_paciente": vulnerabilidad_info["nivel_vulnerabilidad"],
                "prioridad_atencion_sugerida": vulnerabilidad_info["prioridad_atencion"],
                "explicacion_vulnerabilidad": vulnerabilidad_info["explicacion"]
            },
            "message": "Análisis completado y guardado exitosamente"
        }

    except Exception as e:
        print(f"Error en subir_analisis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# ENDPOINT: OBTENER HISTORIAL

@router.get("/historial")
async def obtener_historial(request: Request):
    """Obtener historial de análisis del usuario autenticado"""
    if not hasattr(request.state, 'persona') or not request.state.persona:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")

    try:
        persona_id = request.state.persona["id"]
        supabase = get_supabase()
        
        response = (
            supabase.table("analisis_radiografias")
            .select("*")
            .eq("persona_id", persona_id)
            .order("fecha", desc=True)
            .execute()
        )

        return {
            "success": True,
            "data": response.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ENDPOINT: OBTENER PERFIL DE SALUD

@router.get("/perfil-salud")
async def obtener_perfil_salud(request: Request):
    """Obtener perfil de salud del usuario autenticado"""
    if not hasattr(request.state, 'persona') or not request.state.persona:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")

    try:
        persona_id = request.state.persona["id"]
        supabase = get_supabase()
        
        response = (
            supabase.table("perfil_salud")
            .select("*")
            .eq("persona_id", persona_id)
            .execute()
        )

        if not response.data:
            return {
                "success": False,
                "message": "No se encontró perfil de salud",
                "datos": None
            }

        return {
            "success": True,
            "exito": True,
            "datos": response.data[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))