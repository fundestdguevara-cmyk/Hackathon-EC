"""Signify - Sistema de Consulta de Lengua de Señas Ecuatoriano

Un sistema profesional y modular para la consulta, búsqueda y aprendizaje
del lengua de señas ecuatoriano con funcionalidades de síntesis de voz
y reconocimiento por voz.

Módulos principales:
- database: Gestión de la base de datos de señas
- audio: Síntesis de voz y reconocimiento de audio
- core: Lógica de procesamiento principal
- utils: Utilidades y herramientas auxiliares

Autor: Signify Team
Versión: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Signify Team"
__description__ = "Sistema de Consulta de Lengua de Señas Ecuatoriano"

# Importaciones principales para facilitar el uso del paquete
from .database.signs_database import SignsDatabase, SignEntry
from .core.sign_processor import SignProcessor, get_processor
from .audio.speech_engine import get_speech_engine, get_voice_recognition
from .utils.config_utils import get_runtime_config, SystemConfig

__all__ = [
    'SignsDatabase',
    'SignEntry', 
    'SignProcessor',
    'get_processor',
    'get_speech_engine',
    'get_voice_recognition',
    'get_runtime_config',
    'SystemConfig'
]