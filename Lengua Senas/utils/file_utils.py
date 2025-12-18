"""
Utilidades para manejo de archivos y directorios.

Proporciona funciones para gestión de archivos, directorios temporales,
limpieza de archivos y operaciones de respaldo.

Autor: Signify Team
Versión: 2.0.0
"""

import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Union

# Constantes del módulo
DEFAULT_BACKUP_SUFFIX = ".backup"
DEFAULT_TEMP_CLEANUP_HOURS = 24
TEMP_DIR_NAME = "signbridge_ai"
CSV_FILENAME = "señas_ecuatorianas.csv"


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Asegura que un directorio exista, creándolo si es necesario.
    
    Args:
        directory_path: Ruta del directorio a crear
        
    Returns:
        Path: Objeto Path del directorio creado
        
    Raises:
        OSError: Si no se puede crear el directorio
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise OSError(f"No se pudo crear el directorio {directory_path}: {e}") from e


def get_project_root() -> Path:
    """
    Obtiene la ruta raíz del proyecto.
    
    Busca desde la ubicación actual hacia arriba hasta encontrar
    archivos característicos del proyecto.
    
    Returns:
        Path: Ruta raíz del proyecto
    """
    current_file = Path(__file__)
    # Subir dos niveles desde utils/file_utils.py hasta la raíz
    project_root = current_file.parent.parent
    
    # Verificar que estamos en la raíz correcta
    if (project_root / "app.py").exists() or (project_root / "setup.py").exists():
        return project_root
    
    # Buscar hacia arriba si no encontramos los archivos característicos
    for parent in current_file.parents:
        if (parent / "app.py").exists() or (parent / "setup.py").exists():
            return parent
    
    # Si no encontramos nada, devolver la ubicación calculada
    return project_root


def get_data_directory() -> Path:
    """
    Obtiene el directorio de datos del proyecto.
    
    Returns:
        Path: Directorio de datos, creado si no existe
    """
    data_dir = get_project_root() / "data"
    return ensure_directory_exists(data_dir)


def get_temp_directory() -> Path:
    """
    Obtiene un directorio temporal específico para Signify.
    
    Returns:
        Path: Directorio temporal, creado si no existe
    """
    temp_dir = Path(tempfile.gettempdir()) / TEMP_DIR_NAME
    return ensure_directory_exists(temp_dir)


def get_logs_directory() -> Path:
    """
    Obtiene el directorio de logs del proyecto.
    
    Returns:
        Path: Directorio de logs, creado si no existe
    """
    logs_dir = get_project_root() / "logs"
    return ensure_directory_exists(logs_dir)


def get_cache_directory() -> Path:
    """
    Obtiene el directorio de caché del proyecto.
    
    Returns:
        Path: Directorio de caché, creado si no existe
    """
    cache_dir = get_project_root() / ".cache"
    return ensure_directory_exists(cache_dir)


def clean_temp_files(max_age_hours: int = DEFAULT_TEMP_CLEANUP_HOURS) -> int:
    """
    Limpia archivos temporales antiguos.
    
    Args:
        max_age_hours: Edad máxima en horas para conservar archivos
        
    Returns:
        int: Número de archivos eliminados
    """
    temp_dir = get_temp_directory()
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    files_deleted = 0
    
    try:
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                try:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        files_deleted += 1
                except (OSError, FileNotFoundError):
                    # Ignorar errores de eliminación individual
                    continue
    except (OSError, FileNotFoundError):
        # Directorio temporal no existe o no es accesible
        pass
    
    return files_deleted


def clean_cache_files(max_age_hours: int = DEFAULT_TEMP_CLEANUP_HOURS * 7) -> int:
    """
    Limpia archivos de caché antiguos.
    
    Args:
        max_age_hours: Edad máxima en horas para conservar archivos de caché
        
    Returns:
        int: Número de archivos eliminados
    """
    cache_dir = get_cache_directory()
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    files_deleted = 0
    
    try:
        for file_path in cache_dir.rglob("*"):
            if file_path.is_file():
                try:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        files_deleted += 1
                except (OSError, FileNotFoundError):
                    continue
    except (OSError, FileNotFoundError):
        pass
    
    return files_deleted


def get_csv_file_path() -> Optional[Path]:
    """
    Busca el archivo CSV de señas ecuatorianas en ubicaciones conocidas.
    
    Returns:
        Optional[Path]: Ruta del archivo CSV si existe, None en caso contrario
    """
    possible_paths = [
        get_project_root() / CSV_FILENAME,
        get_data_directory() / CSV_FILENAME,
        Path("C:/Users/migue/OneDrive/Documents/Señas_Samsung") / CSV_FILENAME,
        Path.cwd() / CSV_FILENAME,
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_file():
            return path
    
    return None


def find_csv_files(directory: Optional[Union[str, Path]] = None) -> List[Path]:
    """
    Busca todos los archivos CSV en un directorio.
    
    Args:
        directory: Directorio donde buscar (por defecto: raíz del proyecto)
        
    Returns:
        List[Path]: Lista de archivos CSV encontrados
    """
    if directory is None:
        directory = get_project_root()
    
    search_dir = Path(directory)
    csv_files = []
    
    try:
        if search_dir.exists() and search_dir.is_dir():
            csv_files = list(search_dir.glob("*.csv"))
            # También buscar en subdirectorios
            csv_files.extend(search_dir.glob("**/*.csv"))
    except (OSError, PermissionError):
        pass
    
    return csv_files


def backup_file(file_path: Union[str, Path], 
                backup_suffix: str = DEFAULT_BACKUP_SUFFIX) -> Optional[Path]:
    """
    Crea una copia de seguridad de un archivo.
    
    Args:
        file_path: Ruta del archivo original
        backup_suffix: Sufijo para el archivo de respaldo
        
    Returns:
        Optional[Path]: Ruta del archivo de respaldo si se creó exitosamente
        
    Raises:
        FileNotFoundError: Si el archivo original no existe
        OSError: Si no se puede crear el respaldo
    """
    try:
        original_path = Path(file_path)
        if not original_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        backup_path = original_path.with_suffix(original_path.suffix + backup_suffix)
        
        # Si ya existe un backup, crear uno con timestamp
        if backup_path.exists():
            timestamp = int(time.time())
            backup_path = original_path.with_suffix(
                f"{original_path.suffix}{backup_suffix}.{timestamp}"
            )
        
        shutil.copy2(original_path, backup_path)
        return backup_path
        
    except (OSError, shutil.Error) as e:
        raise OSError(f"No se pudo crear respaldo de {file_path}: {e}") from e


def restore_backup(backup_path: Union[str, Path], 
                  original_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Restaura un archivo desde su respaldo.
    
    Args:
        backup_path: Ruta del archivo de respaldo
        original_path: Ruta donde restaurar (por defecto: inferida del backup)
        
    Returns:
        Path: Ruta del archivo restaurado
        
    Raises:
        FileNotFoundError: Si el archivo de respaldo no existe
        OSError: Si no se puede restaurar el archivo
    """
    backup_file_path = Path(backup_path)
    
    if not backup_file_path.exists():
        raise FileNotFoundError(f"Archivo de respaldo no encontrado: {backup_path}")
    
    if original_path is None:
        # Inferir la ruta original removiendo el sufijo de backup
        original_path = backup_file_path.with_suffix(
            backup_file_path.suffix.replace(DEFAULT_BACKUP_SUFFIX, "")
        )
    
    original_file_path = Path(original_path)
    
    try:
        shutil.copy2(backup_file_path, original_file_path)
        return original_file_path
    except (OSError, shutil.Error) as e:
        raise OSError(f"No se pudo restaurar {backup_path}: {e}") from e


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Obtiene el tamaño de un archivo en megabytes.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        float: Tamaño en MB (0.0 si el archivo no existe o hay error)
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0


def get_file_info(file_path: Union[str, Path]) -> dict:
    """
    Obtiene información detallada de un archivo.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        dict: Información del archivo (tamaño, fechas, permisos, etc.)
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"exists": False}
        
        stat = path.stat()
        
        return {
            "exists": True,
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
            "is_file": path.is_file(),
            "is_directory": path.is_dir(),
            "is_symlink": path.is_symlink(),
            "suffix": path.suffix,
            "name": path.name,
            "parent": str(path.parent),
        }
    except (OSError, FileNotFoundError):
        return {"exists": False, "error": "No se pudo acceder al archivo"}


def safe_remove_file(file_path: Union[str, Path]) -> bool:
    """
    Elimina un archivo de forma segura.
    
    Args:
        file_path: Ruta del archivo a eliminar
        
    Returns:
        bool: True si se eliminó exitosamente, False en caso contrario
    """
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
            return True
        return False
    except (OSError, FileNotFoundError):
        return False


def safe_remove_directory(directory_path: Union[str, Path], 
                         recursive: bool = False) -> bool:
    """
    Elimina un directorio de forma segura.
    
    Args:
        directory_path: Ruta del directorio a eliminar
        recursive: Si eliminar recursivamente el contenido
        
    Returns:
        bool: True si se eliminó exitosamente, False en caso contrario
    """
    try:
        path = Path(directory_path)
        if path.exists() and path.is_dir():
            if recursive:
                shutil.rmtree(path)
            else:
                path.rmdir()  # Solo funciona si está vacío
            return True
        return False
    except (OSError, FileNotFoundError):
        return False


def get_directory_size(directory_path: Union[str, Path]) -> float:
    """
    Calcula el tamaño total de un directorio en MB.
    
    Args:
        directory_path: Ruta del directorio
        
    Returns:
        float: Tamaño total en MB
    """
    try:
        total_size = 0
        path = Path(directory_path)
        
        if path.exists() and path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
        
        return total_size / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0.0


def cleanup_all_temp_files() -> dict:
    """
    Limpia todos los archivos temporales y de caché.
    
    Returns:
        dict: Estadísticas de limpieza
    """
    stats = {
        "temp_files_deleted": 0,
        "cache_files_deleted": 0,
        "total_space_freed_mb": 0.0,
        "errors": []
    }
    
    try:
        # Obtener tamaño antes de la limpieza
        temp_size_before = get_directory_size(get_temp_directory())
        cache_size_before = get_directory_size(get_cache_directory())
        
        # Limpiar archivos
        stats["temp_files_deleted"] = clean_temp_files()
        stats["cache_files_deleted"] = clean_cache_files()
        
        # Calcular espacio liberado
        temp_size_after = get_directory_size(get_temp_directory())
        cache_size_after = get_directory_size(get_cache_directory())
        
        stats["total_space_freed_mb"] = (
            (temp_size_before - temp_size_after) + 
            (cache_size_before - cache_size_after)
        )
        
    except Exception as e:
        stats["errors"].append(f"Error durante limpieza: {e}")
    
    return stats