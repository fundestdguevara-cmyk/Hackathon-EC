"""
Motor de Síntesis de Voz para Señas Ecuatorianas

Integra funcionalidades de texto a voz y reconocimiento de voz usando
gTTS para síntesis y Whisper para reconocimiento de voz.

Autor: Signify Team
Versión: 2.0.0
"""

import os
import shutil
import tempfile
import threading
from typing import Optional

import numpy as np
import pygame
import sounddevice as sd
import whisper
from gtts import gTTS


class SpeechEngine:
    """
    Motor de síntesis de voz usando gTTS y pygame.
    
    Proporciona funcionalidades para convertir texto a voz y reproducir
    audio de forma síncrona o asíncrona.
    """
    
    def __init__(self, language: str = "es") -> None:
        """
        Inicializa el motor de voz.
        
        Args:
            language: Código de idioma para TTS (por defecto español)
        """
        self.language = language
        self.temp_dir = self._create_temp_directory()
        self._init_pygame()
        self._is_initialized = True
    
    def _create_temp_directory(self) -> str:
        """
        Crea directorio temporal para archivos de audio.
        
        Returns:
            Ruta del directorio temporal creado
        """
        temp_dir = os.path.join(tempfile.gettempdir(), "signs_audio")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def _init_pygame(self) -> None:
        """
        Inicializa pygame mixer para reproducción de audio.
        
        Raises:
            RuntimeError: Si no se puede inicializar pygame
        """
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("✅ Motor de audio inicializado correctamente")
        except pygame.error as e:
            error_msg = f"⚠️ Advertencia: No se pudo inicializar pygame mixer: {e}"
            print(error_msg)
            raise RuntimeError(error_msg) from e
    
    def speak_text(self, text: str, async_mode: bool = True) -> None:
        """
        Convierte texto a voz y lo reproduce.
        
        Args:
            text: Texto a convertir a voz
            async_mode: Si True, reproduce en segundo plano
        """
        if not text or not text.strip():
            return
        
        if not self._is_initialized:
            print("❌ Motor de voz no inicializado")
            return
        
        if async_mode:
            thread = threading.Thread(
                target=self._speak_sync, 
                args=(text,),
                daemon=True
            )
            thread.start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str) -> None:
        """
        Función interna para síntesis de voz síncrona.
        
        Args:
            text: Texto a sintetizar y reproducir
        """
        temp_file = None
        try:
            # Crear archivo temporal único
            temp_file = os.path.join(
                self.temp_dir, 
                f"audio_{os.getpid()}_{threading.get_ident()}.mp3"
            )
            
            # Generar audio con gTTS
            tts = gTTS(text=text, lang=self.language, slow=False)
            tts.save(temp_file)
            
            # Verificar que el archivo se creó correctamente
            if not os.path.exists(temp_file):
                print(f"❌ Error: No se pudo crear el archivo de audio temporal")
                return
            
            # Reproducir con pygame
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Esperar a que termine la reproducción con timeout
            timeout_counter = 0
            max_timeout = 300  # 30 segundos máximo
            while pygame.mixer.music.get_busy() and timeout_counter < max_timeout:
                pygame.time.wait(100)
                timeout_counter += 1
            
            # Si se alcanzó el timeout, detener la reproducción
            if timeout_counter >= max_timeout:
                pygame.mixer.music.stop()
                print("⚠️ Reproducción de audio detenida por timeout")
            
        except Exception as e:
            print(f"❌ Error en síntesis de voz: {e}")
            # Intentar detener cualquier reproducción en curso
            try:
                pygame.mixer.music.stop()
            except:
                pass
        finally:
            # Limpiar archivo temporal
            if temp_file:
                self._cleanup_temp_file(temp_file)
    
    def _cleanup_temp_file(self, file_path: str) -> None:
        """
        Limpia archivos temporales de audio.
        
        Args:
            file_path: Ruta del archivo temporal a eliminar
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            print(f"⚠️ No se pudo eliminar archivo temporal: {e}")
    
    def speak_sign_instruction(self, word: str, instructions: str, language: str = "ecuatoriano") -> None:
        """
        Reproduce instrucciones de señas de forma estructurada con anuncio del idioma.
        
        Args:
            word: Palabra de la seña
            instructions: Instrucciones de cómo hacer la seña
            language: Idioma de la seña (ecuatoriano, chileno, mexicano)
        """
        if not word or not instructions:
            return
        
        # Mapeo de idiomas a países
        language_country_map = {
            "ecuatoriano": "Ecuador",
            "chileno": "Chile", 
            "mexicano": "México"
        }
        
        country = language_country_map.get(language, "Ecuador")
        
        instruction_text = (
            f"La palabra '{word}' en lengua de señas de {country} se hace así: {instructions}"
        )
        self.speak_text(instruction_text)
    
    def speak_search_result(self, word: str, found: bool, 
                           instructions: Optional[str] = None, language: str = "ecuatoriano") -> None:
        """
        Reproduce resultados de búsqueda con información del idioma.
        
        Args:
            word: Palabra buscada
            found: Si se encontró la seña
            instructions: Instrucciones de la seña (si se encontró)
            language: Idioma de la búsqueda
        """
        if not word:
            return
        
        # Mapeo de idiomas a países
        language_country_map = {
            "ecuatoriano": "Ecuador",
            "chileno": "Chile", 
            "mexicano": "México"
        }
        
        country = language_country_map.get(language, "Ecuador")
        
        if found and instructions:
            result_text = f"Encontré la seña para '{word}' en lengua de señas de {country}: {instructions}"
        else:
            result_text = f"No encontré la seña para '{word}' en lengua de señas de {country}. Intenta con otra palabra."
        
        self.speak_text(result_text)
    
    def speak_welcome_message(self) -> None:
        """Reproduce mensaje de bienvenida."""
        welcome_text = (
            "Bienvenido al Sistema de Señas Ecuatorianas. "
            "Puedes buscar cualquier palabra para aprender su seña correspondiente."
        )
        self.speak_text(welcome_text)
    
    def speak_help_message(self) -> None:
        """Reproduce mensaje de ayuda."""
        help_text = (
            "Escribe una palabra en el campo de búsqueda para encontrar su seña. "
            "También puedes usar el reconocimiento de voz para buscar palabras habladas."
        )
        self.speak_text(help_text)
    
    def speak_category_info(self, category: str, count: int) -> None:
        """
        Reproduce información sobre una categoría.
        
        Args:
            category: Nombre de la categoría
            count: Número de señas en la categoría
        """
        if not category:
            return
        
        info_text = f"La categoría '{category}' contiene {count} señas disponibles."
        self.speak_text(info_text)
    
    def speak_random_sign(self, word: str, instructions: str) -> None:
        """
        Reproduce información de una seña aleatoria.
        
        Args:
            word: Palabra de la seña
            instructions: Instrucciones de la seña
        """
        if not word or not instructions:
            return
        
        random_text = f"Seña aleatoria: '{word}'. {instructions}"
        self.speak_text(random_text)
    
    def stop_speech(self) -> None:
        """Detiene la reproducción de voz actual."""
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"⚠️ Error al detener reproducción: {e}")
    
    def is_playing(self) -> bool:
        """
        Verifica si hay audio reproduciéndose.
        
        Returns:
            True si hay audio reproduciéndose, False en caso contrario
        """
        try:
            return pygame.mixer.music.get_busy()
        except pygame.error:
            return False
    
    def set_volume(self, volume: float) -> None:
        """
        Establece el volumen de reproducción.
        
        Args:
            volume: Volumen entre 0.0 y 1.0
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError("El volumen debe estar entre 0.0 y 1.0")
        
        try:
            pygame.mixer.music.set_volume(volume)
        except pygame.error as e:
            print(f"⚠️ Error al establecer volumen: {e}")
    
    def cleanup(self) -> None:
        """Limpia recursos del motor de voz."""
        self.stop_speech()
        
        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
        
        # Limpiar directorio temporal
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"⚠️ Error al limpiar directorio temporal: {e}")
        
        self._is_initialized = False


class VoiceRecognitionEngine:
    """
    Motor de reconocimiento de voz usando Whisper de OpenAI.
    
    Proporciona funcionalidades para grabar audio del micrófono
    y transcribirlo a texto usando modelos de Whisper.
    """
    
    # Configuraciones de modelo disponibles
    MODEL_SIZES = ["tiny", "base", "small", "medium", "large"]
    DEFAULT_SAMPLE_RATE = 16000
    DEFAULT_DURATION = 5
    
    def __init__(self, model_size: str = "tiny") -> None:
        """
        Inicializa el motor de reconocimiento de voz.
        
        Args:
            model_size: Tamaño del modelo Whisper (tiny, base, small, medium, large)
            
        Raises:
            ValueError: Si el tamaño del modelo no es válido
        """
        if model_size not in self.MODEL_SIZES:
            raise ValueError(f"Tamaño de modelo inválido. Use uno de: {self.MODEL_SIZES}")
        
        self.model_size = model_size
        self.model = None
        self._is_initialized = False
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Carga el modelo Whisper.
        
        Raises:
            ImportError: Si whisper no está instalado
            Exception: Si hay errores al cargar el modelo
        """
        try:
            self.model = whisper.load_model(self.model_size)
            self._is_initialized = True
            print(f"✅ Modelo Whisper '{self.model_size}' cargado correctamente")
        except ImportError as e:
            error_msg = "❌ Error: whisper no está instalado. Instala con: pip install openai-whisper"
            print(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            error_msg = f"❌ Error al cargar modelo Whisper: {e}"
            print(error_msg)
            raise Exception(error_msg) from e
    
    def is_available(self) -> bool:
        """
        Verifica si el motor de reconocimiento está disponible.
        
        Returns:
            True si el motor está inicializado y disponible
        """
        return self._is_initialized and self.model is not None
    
    def record_and_transcribe(self, duration: int = DEFAULT_DURATION, 
                             sample_rate: int = DEFAULT_SAMPLE_RATE) -> Optional[str]:
        """
        Graba audio del micrófono y lo transcribe.
        
        Args:
            duration: Duración de la grabación en segundos
            sample_rate: Frecuencia de muestreo
            
        Returns:
            Texto transcrito o None si hay error
            
        Raises:
            RuntimeError: Si el motor no está inicializado
        """
        if not self.is_available():
            raise RuntimeError("❌ Modelo Whisper no disponible")
        
        if duration <= 0:
            raise ValueError("La duración debe ser mayor a 0")
        
        if sample_rate <= 0:
            raise ValueError("La frecuencia de muestreo debe ser mayor a 0")
        
        try:
            print(f"🎤 Grabando por {duration} segundos...")
            
            # Grabar audio
            recording = sd.rec(
                int(duration * sample_rate), 
                samplerate=sample_rate, 
                channels=1, 
                dtype=np.float32
            )
            sd.wait()
            
            # Convertir a array 1D
            audio = np.squeeze(recording)
            
            # Verificar que hay audio
            if np.max(np.abs(audio)) < 0.01:
                print("⚠️ Advertencia: Audio muy bajo o silencio detectado")
                return None
            
            print("🔄 Transcribiendo audio...")
            
            # Transcribir con Whisper
            result = self.model.transcribe(audio, language="es")
            transcribed_text = result["text"].strip()
            
            # Limpiar el texto reconocido para eliminar transformaciones no deseadas
            if transcribed_text:
                # Remover puntos finales innecesarios
                if transcribed_text.endswith('.'):
                    transcribed_text = transcribed_text[:-1]
                
                # Remover otros signos de puntuación innecesarios al final
                transcribed_text = transcribed_text.rstrip('.,!?;:')
                
                # Mantener la capitalización original si es una sola palabra
                words = transcribed_text.split()
                if len(words) == 1:
                    # Para una sola palabra, mantener la primera letra en mayúscula si es apropiado
                    transcribed_text = words[0].capitalize()
                else:
                    # Para múltiples palabras, mantener el formato original pero limpiar
                    transcribed_text = transcribed_text.strip()
                
                print(f"📝 Texto transcrito: '{transcribed_text}'")
                return transcribed_text
            else:
                print("⚠️ No se detectó texto en el audio")
                return None
            
        except ImportError as e:
            error_msg = "❌ Error: sounddevice no está instalado. Instala con: pip install sounddevice"
            print(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            error_msg = f"❌ Error en reconocimiento de voz: {e}"
            print(error_msg)
            return None
    
    def test_microphone(self) -> bool:
        """
        Prueba si el micrófono está disponible.
        
        Returns:
            True si el micrófono funciona correctamente
        """
        try:
            # Grabar 1 segundo de prueba
            test_recording = sd.rec(
                int(1 * self.DEFAULT_SAMPLE_RATE), 
                samplerate=self.DEFAULT_SAMPLE_RATE, 
                channels=1, 
                dtype=np.float32
            )
            sd.wait()
            
            # Verificar que se grabó algo
            return len(test_recording) > 0
            
        except Exception as e:
            print(f"❌ Error al probar micrófono: {e}")
            return False
    
    def get_available_devices(self) -> list:
        """
        Obtiene lista de dispositivos de audio disponibles.
        
        Returns:
            Lista de dispositivos de audio
        """
        try:
            return sd.query_devices()
        except Exception as e:
            print(f"❌ Error al consultar dispositivos: {e}")
            return []
    
    def cleanup(self) -> None:
        """Limpia recursos del motor de reconocimiento."""
        self.model = None
        self._is_initialized = False


# Instancias globales singleton
_speech_engine: Optional[SpeechEngine] = None
_voice_recognition: Optional[VoiceRecognitionEngine] = None


def get_speech_engine(language: str = "es") -> SpeechEngine:
    """
    Obtiene la instancia singleton del motor de voz.
    
    Args:
        language: Código de idioma para TTS
        
    Returns:
        Instancia de SpeechEngine
    """
    global _speech_engine
    if _speech_engine is None:
        _speech_engine = SpeechEngine(language)
    return _speech_engine


def get_voice_recognition(model_size: str = "tiny") -> VoiceRecognitionEngine:
    """
    Obtiene la instancia singleton del reconocimiento de voz.
    
    Args:
        model_size: Tamaño del modelo Whisper
        
    Returns:
        Instancia de VoiceRecognitionEngine
    """
    global _voice_recognition
    if _voice_recognition is None:
        _voice_recognition = VoiceRecognitionEngine(model_size)
    return _voice_recognition


def speak(text: str, async_mode: bool = True) -> None:
    """
    Función de conveniencia para síntesis de voz.
    
    Args:
        text: Texto a sintetizar
        async_mode: Si True, reproduce en segundo plano
    """
    engine = get_speech_engine()
    engine.speak_text(text, async_mode)


def listen_and_transcribe(duration: int = 5) -> Optional[str]:
    """
    Función de conveniencia para reconocimiento de voz.
    
    Args:
        duration: Duración de la grabación en segundos
        
    Returns:
        Texto transcrito o None si hay error
    """
    recognition = get_voice_recognition()
    return recognition.record_and_transcribe(duration)


def cleanup_audio_engines() -> None:
    """Limpia todos los motores de audio."""
    global _speech_engine, _voice_recognition
    
    if _speech_engine:
        _speech_engine.cleanup()
        _speech_engine = None
    
    if _voice_recognition:
        _voice_recognition.cleanup()
        _voice_recognition = None
    
    print("✅ Motores de audio limpiados correctamente")