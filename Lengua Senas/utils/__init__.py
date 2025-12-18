"""
Módulo de utilidades para Signify.

Proporciona funciones auxiliares para manejo de archivos, configuración,
validación del sistema y otras utilidades comunes.

Autor: Signify Team
Versión: 2.0.0
"""

# Importar todas las funciones de utilidades
from .file_utils import (
    ensure_directory_exists,
    get_project_root,
    get_data_directory,
    get_temp_directory,
    get_logs_directory,
    get_cache_directory,
    clean_temp_files,
    clean_cache_files,
    get_csv_file_path,
    find_csv_files,
    backup_file,
    restore_backup,
    get_file_size_mb,
    get_file_info,
    safe_remove_file,
    safe_remove_directory,
    get_directory_size,
    cleanup_all_temp_files
)

from .config_utils import (
    AudioConfig,
    UIConfig,
    DatabaseConfig,
    SystemConfig,
    AppConfig,
    get_default_config,
    load_config_from_file as load_config,
    save_config_to_file as save_config,
    get_runtime_config,
    create_sample_config,
    reset_config_to_defaults as reset_config,
    merge_configs,
    get_global_config,
    reload_global_config,
    update_global_config
)

from .validation_utils import (
    ValidationResult,
    SystemValidationReport,
    validate_python_version,
    validate_required_packages,
    validate_optional_packages,
    validate_project_structure,
    validate_audio_system,
    validate_microphone,
    validate_csv_file,
    run_comprehensive_validation,
    # Funciones de compatibilidad
    validate_csv_file_legacy,
    validate_audio_dependencies,
    check_microphone_availability,
    validate_project_structure_legacy,
    get_validation_report,
    check_all_dependencies
)

# Versión del módulo
__version__ = "2.0.0"

# Funciones principales exportadas
__all__ = [
    # File utilities
    "ensure_directory_exists",
    "get_project_root",
    "get_data_directory",
    "get_temp_directory",
    "get_logs_directory",
    "get_cache_directory",
    "clean_temp_files",
    "clean_cache_files",
    "get_csv_file_path",
    "find_csv_files",
    "backup_file",
    "restore_backup",
    "get_file_size_mb",
    "get_file_info",
    "safe_remove_file",
    "safe_remove_directory",
    "get_directory_size",
    "cleanup_all_temp_files",
    
    # Config utilities
    "AudioConfig",
    "UIConfig",
    "DatabaseConfig",
    "SystemConfig",
    "AppConfig",
    "get_default_config",
    "load_config",
    "save_config",
    "get_runtime_config",
    "create_sample_config",
    "reset_config",
    "merge_configs",
    "get_global_config",
    "reload_global_config",
    "update_global_config",
    
    # Validation utilities
    "ValidationResult",
    "SystemValidationReport",
    "validate_python_version",
    "validate_required_packages",
    "validate_optional_packages",
    "validate_project_structure",
    "validate_audio_system",
    "validate_microphone",
    "validate_csv_file",
    "run_comprehensive_validation",
    "validate_csv_file_legacy",
    "validate_audio_dependencies",
    "check_microphone_availability",
    "validate_project_structure_legacy",
    "get_validation_report",
    "check_all_dependencies"
]


def get_module_info() -> dict:
    """
    Obtiene información sobre el módulo de utilidades.
    
    Returns:
        dict: Información del módulo
    """
    return {
        "name": "Signify Utils",
        "version": __version__,
        "description": "Módulo de utilidades para Signify",
        "modules": {
            "file_utils": "Utilidades de manejo de archivos y directorios",
            "config_utils": "Utilidades de configuración y parámetros",
            "validation_utils": "Utilidades de validación del sistema"
        },
        "functions_count": len(__all__)
    }


def validate_utils_module() -> bool:
    """
    Valida que el módulo de utilidades esté correctamente configurado.
    
    Returns:
        bool: True si el módulo está correctamente configurado
    """
    try:
        # Verificar que las funciones principales estén disponibles
        from . import file_utils, config_utils, validation_utils
        
        # Verificar funciones críticas
        critical_functions = [
            "get_project_root",
            "get_default_config",
            "run_comprehensive_validation"
        ]
        
        for func_name in critical_functions:
            if func_name not in __all__:
                return False
        
        return True
        
    except ImportError:
        return False


# Configuración inicial del módulo
def _initialize_utils():
    """Inicializa el módulo de utilidades."""
    try:
        # Asegurar que los directorios básicos existan
        get_temp_directory()
        get_logs_directory()
        get_cache_directory()
        
        # Limpiar archivos temporales antiguos
        clean_temp_files()
        
    except Exception:
        # Fallar silenciosamente si hay problemas de inicialización
        pass


# Ejecutar inicialización
_initialize_utils()