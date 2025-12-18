"""
Utilidades de validación para Signify.

Proporciona funciones para validar dependencias del sistema, estructura del proyecto,
configuración de audio y integridad de datos.

Autor: Signify Team
Versión: 2.0.0
"""

import csv
import importlib
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

from .file_utils import get_project_root, get_csv_file_path

# Constantes de validación
REQUIRED_PYTHON_VERSION = (3, 8)
REQUIRED_PACKAGES = [
    "streamlit",
    "pandas",
    "pygame",
    "openai-whisper",
    "pyaudio",
    "pyttsx3",
    "speech_recognition",
    "difflib"
]

OPTIONAL_PACKAGES = [
    "torch",
    "torchaudio",
    "numpy",
    "scipy"
]

REQUIRED_FILES = [
    "app.py",
    "signs_database.py",
    "speech_engine.py",
    "sign_processor.py",
    "requirements.txt"
]

REQUIRED_DIRECTORIES = [
    "utils"
]

CSV_REQUIRED_COLUMNS = [
    "palabra",
    "instrucciones",
    "categoria"
]


@dataclass
class ValidationResult:
    """
    Resultado de una validación individual.
    
    Attributes:
        name: Nombre de la validación
        passed: Si la validación pasó
        message: Mensaje descriptivo del resultado
        details: Detalles adicionales (opcional)
        severity: Nivel de severidad (info, warning, error, critical)
    """
    name: str
    passed: bool
    message: str
    details: Optional[str] = None
    severity: str = "info"
    
    def __post_init__(self) -> None:
        """Valida los valores después de la inicialización."""
        valid_severities = ["info", "warning", "error", "critical"]
        if self.severity not in valid_severities:
            self.severity = "error" if not self.passed else "info"


@dataclass
class SystemValidationReport:
    """
    Reporte completo de validación del sistema.
    
    Attributes:
        results: Lista de resultados de validación
        overall_status: Estado general (passed/failed)
        summary: Resumen de resultados
        recommendations: Recomendaciones para resolver problemas
        timestamp: Timestamp del reporte
    """
    results: List[ValidationResult] = field(default_factory=list)
    overall_status: str = "unknown"
    summary: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Calcula el estado general y resumen."""
        self._calculate_summary()
        self._determine_overall_status()
        if self.timestamp is None:
            import datetime
            self.timestamp = datetime.datetime.now().isoformat()
    
    def _calculate_summary(self) -> None:
        """Calcula el resumen de resultados."""
        self.summary = {
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "critical": sum(1 for r in self.results if r.severity == "critical"),
            "errors": sum(1 for r in self.results if r.severity == "error"),
            "warnings": sum(1 for r in self.results if r.severity == "warning"),
            "info": sum(1 for r in self.results if r.severity == "info")
        }
    
    def _determine_overall_status(self) -> None:
        """Determina el estado general basado en los resultados."""
        if self.summary.get("critical", 0) > 0:
            self.overall_status = "critical"
        elif self.summary.get("errors", 0) > 0:
            self.overall_status = "failed"
        elif self.summary.get("warnings", 0) > 0:
            self.overall_status = "warning"
        elif self.summary.get("failed", 0) > 0:
            self.overall_status = "failed"
        else:
            self.overall_status = "passed"
    
    def add_result(self, result: ValidationResult) -> None:
        """
        Añade un resultado de validación.
        
        Args:
            result: Resultado a añadir
        """
        self.results.append(result)
        self._calculate_summary()
        self._determine_overall_status()
    
    def get_failed_results(self) -> List[ValidationResult]:
        """
        Obtiene solo los resultados fallidos.
        
        Returns:
            List[ValidationResult]: Resultados fallidos
        """
        return [r for r in self.results if not r.passed]
    
    def get_critical_results(self) -> List[ValidationResult]:
        """
        Obtiene solo los resultados críticos.
        
        Returns:
            List[ValidationResult]: Resultados críticos
        """
        return [r for r in self.results if r.severity == "critical"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el reporte a diccionario.
        
        Returns:
            Dict[str, Any]: Reporte como diccionario
        """
        return {
            "overall_status": self.overall_status,
            "summary": self.summary,
            "timestamp": self.timestamp,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "severity": r.severity
                }
                for r in self.results
            ],
            "recommendations": self.recommendations
        }


def validate_python_version() -> ValidationResult:
    """
    Valida que la versión de Python sea compatible.
    
    Returns:
        ValidationResult: Resultado de la validación
    """
    current_version = sys.version_info[:2]
    required_version = REQUIRED_PYTHON_VERSION
    
    if current_version >= required_version:
        return ValidationResult(
            name="Python Version",
            passed=True,
            message=f"Python {current_version[0]}.{current_version[1]} es compatible",
            severity="info"
        )
    else:
        return ValidationResult(
            name="Python Version",
            passed=False,
            message=f"Python {current_version[0]}.{current_version[1]} no es compatible. Se requiere Python {required_version[0]}.{required_version[1]}+",
            severity="critical"
        )


def validate_required_packages() -> List[ValidationResult]:
    """
    Valida que los paquetes requeridos estén instalados.
    
    Returns:
        List[ValidationResult]: Lista de resultados de validación
    """
    results = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package.replace("-", "_"))
            results.append(ValidationResult(
                name=f"Package: {package}",
                passed=True,
                message=f"Paquete {package} está instalado",
                severity="info"
            ))
        except ImportError:
            results.append(ValidationResult(
                name=f"Package: {package}",
                passed=False,
                message=f"Paquete requerido {package} no está instalado",
                details=f"Instalar con: pip install {package}",
                severity="error"
            ))
    
    return results


def validate_optional_packages() -> List[ValidationResult]:
    """
    Valida que los paquetes opcionales estén instalados.
    
    Returns:
        List[ValidationResult]: Lista de resultados de validación
    """
    results = []
    
    for package in OPTIONAL_PACKAGES:
        try:
            importlib.import_module(package.replace("-", "_"))
            results.append(ValidationResult(
                name=f"Optional Package: {package}",
                passed=True,
                message=f"Paquete opcional {package} está instalado",
                severity="info"
            ))
        except ImportError:
            results.append(ValidationResult(
                name=f"Optional Package: {package}",
                passed=False,
                message=f"Paquete opcional {package} no está instalado",
                details=f"Instalar con: pip install {package}",
                severity="warning"
            ))
    
    return results


def validate_project_structure() -> List[ValidationResult]:
    """
    Valida la estructura del proyecto.
    
    Returns:
        List[ValidationResult]: Lista de resultados de validación
    """
    results = []
    project_root = get_project_root()
    
    # Validar archivos requeridos
    for file_name in REQUIRED_FILES:
        file_path = project_root / file_name
        if file_path.exists() and file_path.is_file():
            results.append(ValidationResult(
                name=f"File: {file_name}",
                passed=True,
                message=f"Archivo {file_name} existe",
                severity="info"
            ))
        else:
            results.append(ValidationResult(
                name=f"File: {file_name}",
                passed=False,
                message=f"Archivo requerido {file_name} no encontrado",
                details=f"Ruta esperada: {file_path}",
                severity="error"
            ))
    
    # Validar directorios requeridos
    for dir_name in REQUIRED_DIRECTORIES:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            results.append(ValidationResult(
                name=f"Directory: {dir_name}",
                passed=True,
                message=f"Directorio {dir_name} existe",
                severity="info"
            ))
        else:
            results.append(ValidationResult(
                name=f"Directory: {dir_name}",
                passed=False,
                message=f"Directorio requerido {dir_name} no encontrado",
                details=f"Ruta esperada: {dir_path}",
                severity="error"
            ))
    
    return results


def validate_audio_system() -> List[ValidationResult]:
    """
    Valida el sistema de audio.
    
    Returns:
        List[ValidationResult]: Lista de resultados de validación
    """
    results = []
    
    # Validar pygame
    try:
        import pygame
        pygame.mixer.init()
        results.append(ValidationResult(
            name="Audio: Pygame",
            passed=True,
            message="Pygame mixer inicializado correctamente",
            severity="info"
        ))
        pygame.mixer.quit()
    except Exception as e:
        results.append(ValidationResult(
            name="Audio: Pygame",
            passed=False,
            message="Error al inicializar pygame mixer",
            details=str(e),
            severity="error"
        ))
    
    # Validar pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.stop()
        results.append(ValidationResult(
            name="Audio: TTS Engine",
            passed=True,
            message="Motor de síntesis de voz disponible",
            severity="info"
        ))
    except Exception as e:
        results.append(ValidationResult(
            name="Audio: TTS Engine",
            passed=False,
            message="Error al inicializar motor de síntesis de voz",
            details=str(e),
            severity="warning"
        ))
    
    # Validar micrófono
    microphone_result = validate_microphone()
    results.append(microphone_result)
    
    return results


def validate_microphone() -> ValidationResult:
    """
    Valida la disponibilidad del micrófono.
    
    Returns:
        ValidationResult: Resultado de la validación del micrófono
    """
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        microphones = sr.Microphone.list_microphone_names()
        
        if not microphones:
            return ValidationResult(
                name="Audio: Microphone",
                passed=False,
                message="No se encontraron micrófonos disponibles",
                severity="warning"
            )
        
        # Intentar usar el micrófono por defecto
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        return ValidationResult(
            name="Audio: Microphone",
            passed=True,
            message=f"Micrófono disponible. Encontrados {len(microphones)} dispositivos",
            details=f"Dispositivos: {', '.join(microphones[:3])}{'...' if len(microphones) > 3 else ''}",
            severity="info"
        )
        
    except ImportError:
        return ValidationResult(
            name="Audio: Microphone",
            passed=False,
            message="speech_recognition no está disponible",
            details="Instalar con: pip install SpeechRecognition",
            severity="error"
        )
    except Exception as e:
        return ValidationResult(
            name="Audio: Microphone",
            passed=False,
            message="Error al acceder al micrófono",
            details=str(e),
            severity="warning"
        )


def validate_csv_file() -> ValidationResult:
    """
    Valida el archivo CSV de señas.
    
    Returns:
        ValidationResult: Resultado de la validación del CSV
    """
    csv_path = get_csv_file_path()
    
    if csv_path is None:
        return ValidationResult(
            name="Data: CSV File",
            passed=False,
            message="Archivo CSV de señas no encontrado",
            details="Buscar archivo 'señas_ecuatorianas.csv' en el directorio del proyecto",
            severity="critical"
        )
    
    try:
        # Validar que el archivo se puede leer
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Validar columnas requeridas
            if not reader.fieldnames:
                return ValidationResult(
                    name="Data: CSV File",
                    passed=False,
                    message="Archivo CSV no tiene encabezados",
                    severity="error"
                )
            
            missing_columns = []
            for required_col in CSV_REQUIRED_COLUMNS:
                if required_col not in reader.fieldnames:
                    missing_columns.append(required_col)
            
            if missing_columns:
                return ValidationResult(
                    name="Data: CSV File",
                    passed=False,
                    message=f"Columnas requeridas faltantes: {', '.join(missing_columns)}",
                    details=f"Columnas encontradas: {', '.join(reader.fieldnames)}",
                    severity="error"
                )
            
            # Contar filas
            row_count = sum(1 for _ in reader)
            
            if row_count == 0:
                return ValidationResult(
                    name="Data: CSV File",
                    passed=False,
                    message="Archivo CSV está vacío",
                    severity="error"
                )
            
            return ValidationResult(
                name="Data: CSV File",
                passed=True,
                message=f"Archivo CSV válido con {row_count} registros",
                details=f"Ruta: {csv_path}",
                severity="info"
            )
            
    except UnicodeDecodeError:
        return ValidationResult(
            name="Data: CSV File",
            passed=False,
            message="Error de codificación en archivo CSV",
            details="Verificar que el archivo esté codificado en UTF-8",
            severity="error"
        )
    except Exception as e:
        return ValidationResult(
            name="Data: CSV File",
            passed=False,
            message="Error al leer archivo CSV",
            details=str(e),
            severity="error"
        )


def run_comprehensive_validation() -> SystemValidationReport:
    """
    Ejecuta una validación completa del sistema.
    
    Returns:
        SystemValidationReport: Reporte completo de validación
    """
    report = SystemValidationReport()
    
    # Validaciones básicas
    report.add_result(validate_python_version())
    
    # Validaciones de paquetes
    for result in validate_required_packages():
        report.add_result(result)
    
    for result in validate_optional_packages():
        report.add_result(result)
    
    # Validaciones de estructura
    for result in validate_project_structure():
        report.add_result(result)
    
    # Validaciones de datos
    report.add_result(validate_csv_file())
    
    # Validaciones de audio
    for result in validate_audio_system():
        report.add_result(result)
    
    # Generar recomendaciones
    report.recommendations = _generate_recommendations(report)
    
    return report


def _generate_recommendations(report: SystemValidationReport) -> List[str]:
    """
    Genera recomendaciones basadas en los resultados de validación.
    
    Args:
        report: Reporte de validación
        
    Returns:
        List[str]: Lista de recomendaciones
    """
    recommendations = []
    
    failed_results = report.get_failed_results()
    critical_results = report.get_critical_results()
    
    if critical_results:
        recommendations.append("🚨 Problemas críticos encontrados que impiden el funcionamiento:")
        for result in critical_results:
            recommendations.append(f"   • {result.message}")
            if result.details:
                recommendations.append(f"     → {result.details}")
    
    if failed_results:
        error_results = [r for r in failed_results if r.severity == "error"]
        warning_results = [r for r in failed_results if r.severity == "warning"]
        
        if error_results:
            recommendations.append("\n⚠️ Errores que deben corregirse:")
            for result in error_results:
                recommendations.append(f"   • {result.message}")
                if result.details:
                    recommendations.append(f"     → {result.details}")
        
        if warning_results:
            recommendations.append("\n💡 Advertencias (funcionalidad limitada):")
            for result in warning_results:
                recommendations.append(f"   • {result.message}")
                if result.details:
                    recommendations.append(f"     → {result.details}")
    
    if report.overall_status == "passed":
        recommendations.append("✅ Todas las validaciones pasaron correctamente.")
        recommendations.append("El sistema está listo para ejecutar Signify.")
    
    # Recomendaciones generales
    recommendations.append("\n📋 Recomendaciones generales:")
    recommendations.append("   • Ejecutar 'pip install -r requirements.txt' para instalar dependencias")
    recommendations.append("   • Verificar que el archivo CSV esté en la ubicación correcta")
    recommendations.append("   • Probar el micrófono antes de usar reconocimiento de voz")
    recommendations.append("   • Mantener conexión a internet para descargar modelos de Whisper")
    
    return recommendations


# Funciones de compatibilidad con la versión anterior
def validate_csv_file_legacy(csv_path: Path) -> Tuple[bool, str]:
    """
    Función de compatibilidad para validar CSV (versión anterior).
    
    Args:
        csv_path: Ruta del archivo CSV
        
    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)
    """
    result = validate_csv_file()
    return result.passed, result.message


def validate_audio_dependencies() -> Dict[str, bool]:
    """
    Función de compatibilidad para validar dependencias de audio.
    
    Returns:
        Dict[str, bool]: Estado de cada dependencia
    """
    dependencies = {
        'pygame': False,
        'pyttsx3': False,
        'speech_recognition': False,
        'whisper': False
    }
    
    for dep in dependencies:
        try:
            if dep == 'whisper':
                import whisper
            else:
                importlib.import_module(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies


def check_microphone_availability() -> bool:
    """
    Función de compatibilidad para verificar micrófono.
    
    Returns:
        bool: True si hay micrófono disponible
    """
    result = validate_microphone()
    return result.passed


def validate_project_structure_legacy() -> Dict[str, bool]:
    """
    Función de compatibilidad para validar estructura del proyecto.
    
    Returns:
        Dict[str, bool]: Estado de cada directorio/archivo requerido
    """
    results = validate_project_structure()
    return {result.name.split(": ")[1]: result.passed for result in results}


def get_validation_report() -> Dict[str, Any]:
    """
    Función de compatibilidad para generar reporte de validación.
    
    Returns:
        Dict[str, Any]: Reporte completo de validación
    """
    report = run_comprehensive_validation()
    return report.to_dict()


def check_all_dependencies() -> List[str]:
    """
    Función de compatibilidad para verificar todas las dependencias.
    
    Returns:
        List[str]: Lista de problemas encontrados
    """
    report = run_comprehensive_validation()
    failed_results = report.get_failed_results()
    return [f"{result.name}: {result.message}" for result in failed_results]