"""
Utilidades para manejo de configuración del sistema.

Proporciona clases de configuración y funciones para cargar, guardar
y gestionar la configuración de la aplicación Signify.

Autor: Signify Team
Versión: 2.0.0
"""

import json
import os
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Any, Optional, Union

from .file_utils import get_project_root, ensure_directory_exists

# Constantes de configuración
DEFAULT_CONFIG_FILENAME = "config.json"
DEFAULT_SAMPLE_CONFIG_FILENAME = "config_sample.json"
DEFAULT_AUDIO_RATE = 22050
DEFAULT_AUDIO_CHANNELS = 1
DEFAULT_AUDIO_CHUNK_SIZE = 1024
DEFAULT_VOICE_TIMEOUT = 5.0
DEFAULT_VOICE_PHRASE_TIMEOUT = 1.0
DEFAULT_TTS_RATE = 150
DEFAULT_TTS_VOLUME = 0.9


@dataclass
class AudioConfig:
    """
    Configuración de audio para síntesis de voz y reconocimiento.
    
    Attributes:
        tts_enabled: Si la síntesis de voz está habilitada
        voice_recognition_enabled: Si el reconocimiento de voz está habilitado
        sample_rate: Frecuencia de muestreo de audio
        channels: Número de canales de audio
        chunk_size: Tamaño del buffer de audio
        voice_timeout: Tiempo límite para reconocimiento de voz
        phrase_timeout: Tiempo límite para frases
        tts_rate: Velocidad de síntesis de voz
        tts_volume: Volumen de síntesis de voz
        whisper_model: Modelo de Whisper a usar
        audio_device_index: Índice del dispositivo de audio
    """
    tts_enabled: bool = True
    voice_recognition_enabled: bool = True
    sample_rate: int = DEFAULT_AUDIO_RATE
    channels: int = DEFAULT_AUDIO_CHANNELS
    chunk_size: int = DEFAULT_AUDIO_CHUNK_SIZE
    voice_timeout: float = DEFAULT_VOICE_TIMEOUT
    phrase_timeout: float = DEFAULT_VOICE_PHRASE_TIMEOUT
    tts_rate: int = DEFAULT_TTS_RATE
    tts_volume: float = DEFAULT_TTS_VOLUME
    whisper_model: str = "base"
    audio_device_index: Optional[int] = None
    
    def __post_init__(self) -> None:
        """Valida la configuración después de la inicialización."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Valida los valores de configuración."""
        if not 8000 <= self.sample_rate <= 48000:
            raise ValueError(f"sample_rate debe estar entre 8000 y 48000, recibido: {self.sample_rate}")
        
        if self.channels not in [1, 2]:
            raise ValueError(f"channels debe ser 1 o 2, recibido: {self.channels}")
        
        if not 512 <= self.chunk_size <= 8192:
            raise ValueError(f"chunk_size debe estar entre 512 y 8192, recibido: {self.chunk_size}")
        
        if not 0.1 <= self.voice_timeout <= 30.0:
            raise ValueError(f"voice_timeout debe estar entre 0.1 y 30.0, recibido: {self.voice_timeout}")
        
        if not 0.1 <= self.phrase_timeout <= 10.0:
            raise ValueError(f"phrase_timeout debe estar entre 0.1 y 10.0, recibido: {self.phrase_timeout}")
        
        if not 50 <= self.tts_rate <= 400:
            raise ValueError(f"tts_rate debe estar entre 50 y 400, recibido: {self.tts_rate}")
        
        if not 0.0 <= self.tts_volume <= 1.0:
            raise ValueError(f"tts_volume debe estar entre 0.0 y 1.0, recibido: {self.tts_volume}")
        
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if self.whisper_model not in valid_models:
            raise ValueError(f"whisper_model debe ser uno de {valid_models}, recibido: {self.whisper_model}")


@dataclass
class UIConfig:
    """
    Configuración de la interfaz de usuario.
    
    Attributes:
        theme: Tema de la interfaz (light/dark)
        language: Idioma de la interfaz
        show_advanced_options: Si mostrar opciones avanzadas
        auto_play_audio: Si reproducir audio automáticamente
        results_per_page: Número de resultados por página
        show_confidence_scores: Si mostrar puntuaciones de confianza
        enable_animations: Si habilitar animaciones
        sidebar_collapsed: Si la barra lateral está colapsada por defecto
    """
    theme: str = "light"
    language: str = "es"
    show_advanced_options: bool = False
    auto_play_audio: bool = True
    results_per_page: int = 10
    show_confidence_scores: bool = True
    enable_animations: bool = True
    sidebar_collapsed: bool = False
    
    def __post_init__(self) -> None:
        """Valida la configuración después de la inicialización."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Valida los valores de configuración."""
        valid_themes = ["light", "dark", "auto"]
        if self.theme not in valid_themes:
            raise ValueError(f"theme debe ser uno de {valid_themes}, recibido: {self.theme}")
        
        valid_languages = ["es", "en"]
        if self.language not in valid_languages:
            raise ValueError(f"language debe ser uno de {valid_languages}, recibido: {self.language}")
        
        if not 1 <= self.results_per_page <= 100:
            raise ValueError(f"results_per_page debe estar entre 1 y 100, recibido: {self.results_per_page}")


@dataclass
class DatabaseConfig:
    """
    Configuración de la base de datos de señas.
    
    Attributes:
        csv_file_path: Ruta del archivo CSV
        auto_reload: Si recargar automáticamente la base de datos
        cache_enabled: Si habilitar caché de búsquedas
        fuzzy_search_threshold: Umbral para búsqueda difusa
        max_search_results: Número máximo de resultados de búsqueda
        enable_partial_search: Si habilitar búsqueda parcial
        search_timeout: Tiempo límite para búsquedas
    """
    csv_file_path: Optional[str] = None
    auto_reload: bool = True
    cache_enabled: bool = True
    fuzzy_search_threshold: float = 0.6
    max_search_results: int = 50
    enable_partial_search: bool = True
    search_timeout: float = 5.0
    
    def __post_init__(self) -> None:
        """Valida la configuración después de la inicialización."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Valida los valores de configuración."""
        if not 0.0 <= self.fuzzy_search_threshold <= 1.0:
            raise ValueError(f"fuzzy_search_threshold debe estar entre 0.0 y 1.0, recibido: {self.fuzzy_search_threshold}")
        
        if not 1 <= self.max_search_results <= 1000:
            raise ValueError(f"max_search_results debe estar entre 1 y 1000, recibido: {self.max_search_results}")
        
        if not 0.1 <= self.search_timeout <= 60.0:
            raise ValueError(f"search_timeout debe estar entre 0.1 y 60.0, recibido: {self.search_timeout}")


@dataclass
class SystemConfig:
    """
    Configuración general del sistema.
    
    Attributes:
        debug_mode: Si el modo debug está habilitado
        log_level: Nivel de logging
        temp_cleanup_hours: Horas para limpiar archivos temporales
        max_memory_usage_mb: Uso máximo de memoria en MB
        enable_telemetry: Si habilitar telemetría
        auto_update_check: Si verificar actualizaciones automáticamente
        performance_monitoring: Si habilitar monitoreo de rendimiento
    """
    debug_mode: bool = False
    log_level: str = "INFO"
    temp_cleanup_hours: int = 24
    max_memory_usage_mb: int = 512
    enable_telemetry: bool = False
    auto_update_check: bool = True
    performance_monitoring: bool = False
    
    def __post_init__(self) -> None:
        """Valida la configuración después de la inicialización."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Valida los valores de configuración."""
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level debe ser uno de {valid_log_levels}, recibido: {self.log_level}")
        
        if not 1 <= self.temp_cleanup_hours <= 168:  # 1 hora a 1 semana
            raise ValueError(f"temp_cleanup_hours debe estar entre 1 y 168, recibido: {self.temp_cleanup_hours}")
        
        if not 64 <= self.max_memory_usage_mb <= 4096:
            raise ValueError(f"max_memory_usage_mb debe estar entre 64 y 4096, recibido: {self.max_memory_usage_mb}")


@dataclass
class AppConfig:
    """
    Configuración completa de la aplicación.
    
    Attributes:
        audio: Configuración de audio
        ui: Configuración de interfaz de usuario
        database: Configuración de base de datos
        system: Configuración del sistema
        version: Versión de configuración
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
    """
    audio: AudioConfig = field(default_factory=AudioConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    version: str = "2.0.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la configuración a diccionario.
        
        Returns:
            Dict[str, Any]: Configuración como diccionario
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """
        Crea una configuración desde un diccionario.
        
        Args:
            data: Diccionario con datos de configuración
            
        Returns:
            AppConfig: Instancia de configuración
        """
        # Extraer configuraciones anidadas
        audio_data = data.get('audio', {})
        ui_data = data.get('ui', {})
        database_data = data.get('database', {})
        system_data = data.get('system', {})
        
        return cls(
            audio=AudioConfig(**audio_data),
            ui=UIConfig(**ui_data),
            database=DatabaseConfig(**database_data),
            system=SystemConfig(**system_data),
            version=data.get('version', '2.0.0'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def validate(self) -> bool:
        """
        Valida toda la configuración.
        
        Returns:
            bool: True si la configuración es válida
            
        Raises:
            ValueError: Si alguna configuración es inválida
        """
        try:
            # Las validaciones se ejecutan automáticamente en __post_init__
            # de cada dataclass, pero las llamamos explícitamente por seguridad
            self.audio._validate_config()
            self.ui._validate_config()
            self.database._validate_config()
            self.system._validate_config()
            return True
        except ValueError:
            raise


def get_default_config() -> AppConfig:
    """
    Obtiene la configuración por defecto.
    
    Returns:
        AppConfig: Configuración por defecto
    """
    import datetime
    
    config = AppConfig()
    config.created_at = datetime.datetime.now().isoformat()
    config.updated_at = config.created_at
    
    return config


def get_config_file_path() -> Path:
    """
    Obtiene la ruta del archivo de configuración.
    
    Returns:
        Path: Ruta del archivo de configuración
    """
    return get_project_root() / DEFAULT_CONFIG_FILENAME


def load_config_from_file(config_path: Optional[Union[str, Path]] = None) -> AppConfig:
    """
    Carga la configuración desde un archivo JSON.
    
    Args:
        config_path: Ruta del archivo de configuración (opcional)
        
    Returns:
        AppConfig: Configuración cargada o por defecto si no existe
        
    Raises:
        ValueError: Si el archivo de configuración es inválido
        OSError: Si hay problemas de acceso al archivo
    """
    if config_path is None:
        config_path = get_config_file_path()
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Crear configuración por defecto si no existe
        default_config = get_default_config()
        save_config_to_file(default_config, config_path)
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config = AppConfig.from_dict(data)
        config.validate()
        
        # Actualizar timestamp de última carga
        import datetime
        config.updated_at = datetime.datetime.now().isoformat()
        
        return config
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Archivo de configuración JSON inválido: {e}") from e
    except (OSError, IOError) as e:
        raise OSError(f"Error al leer archivo de configuración: {e}") from e


def save_config_to_file(config: AppConfig, 
                       config_path: Optional[Union[str, Path]] = None) -> None:
    """
    Guarda la configuración en un archivo JSON.
    
    Args:
        config: Configuración a guardar
        config_path: Ruta del archivo de configuración (opcional)
        
    Raises:
        OSError: Si hay problemas de acceso al archivo
        ValueError: Si la configuración es inválida
    """
    if config_path is None:
        config_path = get_config_file_path()
    
    config_file = Path(config_path)
    
    # Validar configuración antes de guardar
    config.validate()
    
    # Actualizar timestamp
    import datetime
    config.updated_at = datetime.datetime.now().isoformat()
    
    # Asegurar que el directorio existe
    ensure_directory_exists(config_file.parent)
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
    except (OSError, IOError) as e:
        raise OSError(f"Error al guardar archivo de configuración: {e}") from e


def get_runtime_config() -> AppConfig:
    """
    Obtiene la configuración de tiempo de ejecución.
    
    Carga la configuración desde archivo o variables de entorno.
    
    Returns:
        AppConfig: Configuración de tiempo de ejecución
    """
    # Cargar configuración base desde archivo
    config = load_config_from_file()
    
    # Sobrescribir con variables de entorno si existen
    _apply_environment_overrides(config)
    
    return config


def _apply_environment_overrides(config: AppConfig) -> None:
    """
    Aplica sobrescrituras desde variables de entorno.
    
    Args:
        config: Configuración a modificar
    """
    # Audio overrides
    if os.getenv('SIGNBRIDGE_TTS_ENABLED'):
        config.audio.tts_enabled = os.getenv('SIGNBRIDGE_TTS_ENABLED').lower() == 'true'
    
    if os.getenv('SIGNBRIDGE_VOICE_RECOGNITION_ENABLED'):
        config.audio.voice_recognition_enabled = os.getenv('SIGNBRIDGE_VOICE_RECOGNITION_ENABLED').lower() == 'true'
    
    if os.getenv('SIGNBRIDGE_WHISPER_MODEL'):
        config.audio.whisper_model = os.getenv('SIGNBRIDGE_WHISPER_MODEL')
    
    # UI overrides
    if os.getenv('SIGNBRIDGE_THEME'):
        config.ui.theme = os.getenv('SIGNBRIDGE_THEME')
    
    if os.getenv('SIGNBRIDGE_LANGUAGE'):
        config.ui.language = os.getenv('SIGNBRIDGE_LANGUAGE')
    
    # Database overrides
    if os.getenv('SIGNBRIDGE_CSV_PATH'):
        config.database.csv_file_path = os.getenv('SIGNBRIDGE_CSV_PATH')
    
    # System overrides
    if os.getenv('SIGNBRIDGE_DEBUG'):
        config.system.debug_mode = os.getenv('SIGNBRIDGE_DEBUG').lower() == 'true'
    
    if os.getenv('SIGNBRIDGE_LOG_LEVEL'):
        config.system.log_level = os.getenv('SIGNBRIDGE_LOG_LEVEL').upper()


def create_sample_config(output_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Crea un archivo de configuración de ejemplo.
    
    Args:
        output_path: Ruta donde crear el archivo (opcional)
        
    Returns:
        Path: Ruta del archivo creado
        
    Raises:
        OSError: Si hay problemas de acceso al archivo
    """
    if output_path is None:
        output_path = get_project_root() / DEFAULT_SAMPLE_CONFIG_FILENAME
    
    sample_config = get_default_config()
    
    # Añadir comentarios explicativos al diccionario
    config_dict = sample_config.to_dict()
    config_dict['_comments'] = {
        'audio': {
            'whisper_model': 'Opciones: tiny, base, small, medium, large',
            'sample_rate': 'Frecuencia de muestreo en Hz (8000-48000)',
            'tts_rate': 'Velocidad de síntesis de voz (50-400 palabras por minuto)'
        },
        'ui': {
            'theme': 'Opciones: light, dark, auto',
            'language': 'Opciones: es, en',
            'results_per_page': 'Número de resultados por página (1-100)'
        },
        'database': {
            'fuzzy_search_threshold': 'Umbral de similitud para búsqueda difusa (0.0-1.0)',
            'max_search_results': 'Máximo número de resultados (1-1000)'
        },
        'system': {
            'log_level': 'Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL',
            'max_memory_usage_mb': 'Uso máximo de memoria en MB (64-4096)'
        }
    }
    
    output_file = Path(output_path)
    ensure_directory_exists(output_file.parent)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        return output_file
    except (OSError, IOError) as e:
        raise OSError(f"Error al crear archivo de configuración de ejemplo: {e}") from e


def reset_config_to_defaults(config_path: Optional[Union[str, Path]] = None) -> AppConfig:
    """
    Resetea la configuración a valores por defecto.
    
    Args:
        config_path: Ruta del archivo de configuración (opcional)
        
    Returns:
        AppConfig: Nueva configuración por defecto
        
    Raises:
        OSError: Si hay problemas de acceso al archivo
    """
    default_config = get_default_config()
    save_config_to_file(default_config, config_path)
    return default_config


def merge_configs(base_config: AppConfig, override_config: AppConfig) -> AppConfig:
    """
    Combina dos configuraciones, dando prioridad a la segunda.
    
    Args:
        base_config: Configuración base
        override_config: Configuración que sobrescribe
        
    Returns:
        AppConfig: Configuración combinada
    """
    base_dict = base_config.to_dict()
    override_dict = override_config.to_dict()
    
    # Combinar diccionarios recursivamente
    merged_dict = _deep_merge_dicts(base_dict, override_dict)
    
    return AppConfig.from_dict(merged_dict)


def _deep_merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combina diccionarios de forma recursiva.
    
    Args:
        base: Diccionario base
        override: Diccionario que sobrescribe
        
    Returns:
        Dict[str, Any]: Diccionario combinado
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


# Instancia global de configuración (singleton)
_global_config: Optional[AppConfig] = None


def get_global_config() -> AppConfig:
    """
    Obtiene la instancia global de configuración.
    
    Returns:
        AppConfig: Configuración global
    """
    global _global_config
    
    if _global_config is None:
        _global_config = get_runtime_config()
    
    return _global_config


def reload_global_config() -> AppConfig:
    """
    Recarga la configuración global desde archivo.
    
    Returns:
        AppConfig: Nueva configuración global
    """
    global _global_config
    _global_config = get_runtime_config()
    return _global_config


def update_global_config(**kwargs) -> AppConfig:
    """
    Actualiza la configuración global con nuevos valores.
    
    Args:
        **kwargs: Valores a actualizar
        
    Returns:
        AppConfig: Configuración actualizada
    """
    global _global_config
    
    if _global_config is None:
        _global_config = get_runtime_config()
    
    # Actualizar valores específicos
    config_dict = _global_config.to_dict()
    
    for key, value in kwargs.items():
        if '.' in key:
            # Manejar claves anidadas como 'audio.tts_enabled'
            keys = key.split('.')
            current = config_dict
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        else:
            config_dict[key] = value
    
    _global_config = AppConfig.from_dict(config_dict)
    return _global_config