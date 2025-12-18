"""
Módulo de Base de Datos para Señas Ecuatorianas.

Maneja la carga, búsqueda y gestión de señas desde el archivo CSV.
Proporciona funcionalidades de búsqueda exacta, difusa y por categorías.

Autor: Signify Team
Versión: 2.0.0
"""

import csv
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import difflib


@dataclass
class SignEntry:
    """
    Representa una entrada de seña en la base de datos.
    
    Attributes:
        word: Palabra o término de la seña
        instructions: Instrucciones detalladas para realizar la seña
        category: Categoría temática de la seña
        description: Descripción adicional (mantenido por compatibilidad)
        language: Idioma de la seña (ecuatoriano, chileno, mexicano)
    """
    word: str
    instructions: str
    category: str = "General"
    description: str = ""
    language: str = "ecuatoriano"
    
    def __post_init__(self) -> None:
        """Inicialización posterior para mantener compatibilidad."""
        if not self.description:
            self.description = self.instructions
    
    def __str__(self) -> str:
        """Representación en cadena de la entrada de seña."""
        return f"{self.word}: {self.instructions}"


class SignsDatabase:
    """
    Clase principal para manejar la base de datos de señas multiidioma.
    
    Proporciona funcionalidades para cargar, buscar y gestionar señas
    desde múltiples archivos CSV con soporte para búsquedas exactas, difusas
    y por categorías en diferentes idiomas de señas.
    """
    
    def __init__(self, csv_files: Optional[Dict[str, str]] = None) -> None:
        """
        Inicializa la base de datos de señas multiidioma.
        
        Args:
            csv_files: Diccionario con idioma como clave y ruta del CSV como valor.
                      Si es None, usa las rutas por defecto.
        """
        self.signs: Dict[str, Dict[str, SignEntry]] = {}  # {idioma: {palabra: SignEntry}}
        self.csv_files = csv_files or self._get_default_csv_files()
        self._load_all_signs()
    
    def _get_default_csv_files(self) -> Dict[str, str]:
        """
        Obtiene las rutas por defecto de los archivos CSV para cada idioma.
        
        Returns:
            Diccionario con idioma como clave y ruta del CSV como valor
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return {
            "ecuatoriano": os.path.join(project_root, "señas_ecuatorianas.csv"),
            "chileno": os.path.join(project_root, "señas_chilenas.csv"),
            "mexicano": os.path.join(project_root, "señas_mexicanas.csv")
        }
    
    def _get_default_csv_path(self) -> str:
        """
        Obtiene la ruta por defecto del archivo CSV ecuatoriano (compatibilidad).
        
        Returns:
            Ruta del archivo CSV ecuatoriano
        """
        return self._get_default_csv_files()["ecuatoriano"]
    
    def _load_all_signs(self) -> None:
        """
        Carga las señas desde todos los archivos CSV configurados.
        
        Raises:
            FileNotFoundError: Si algún archivo CSV no existe
            Exception: Si hay errores durante la carga
        """
        total_loaded = 0
        
        for language, csv_path in self.csv_files.items():
            try:
                self.signs[language] = {}
                loaded_count = self._load_signs_from_file(csv_path, language)
                total_loaded += loaded_count
                print(f"✅ {language.capitalize()}: {loaded_count} señas cargadas")
            except Exception as e:
                print(f"❌ Error cargando {language}: {e}")
                self.signs[language] = {}
        
        print(f"✅ Total: {total_loaded} señas cargadas de {len(self.csv_files)} idiomas")
    
    def _load_signs_from_file(self, csv_path: str, language: str) -> int:
        """
        Carga las señas desde un archivo CSV específico.
        
        Args:
            csv_path: Ruta del archivo CSV
            language: Idioma de las señas
            
        Returns:
            Número de señas cargadas
            
        Raises:
            FileNotFoundError: Si el archivo CSV no existe
            Exception: Si hay errores durante la carga
        """
        if not os.path.exists(csv_path):
            print(f"⚠️ Archivo no encontrado: {csv_path}")
            return 0
            
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as file:
                csv_reader = csv.DictReader(file, quotechar='"', skipinitialspace=True)
                
                loaded_count = 0
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # Obtener y limpiar los datos
                        palabra_key = next((k for k in row.keys() if 'Palabra' in k), 'Palabra')
                        descripcion_key = next((k for k in row.keys() if 'Descripción' in k), 'Descripción')
                        categoria_key = next((k for k in row.keys() if 'Categoría' in k), 'Categoría')
                        
                        raw_word = row.get(palabra_key, '').strip()
                        instructions = row.get(descripcion_key, '').strip()
                        category = row.get(categoria_key, 'General').strip()
                        
                        # Remover comillas adicionales si existen
                        if raw_word.startswith('"') and raw_word.endswith('"'):
                            raw_word = raw_word[1:-1]
                        
                        # Normalizar la palabra
                        word_normalized = self._normalize_word(raw_word)
                        word_key = raw_word.lower().strip()
                        
                        if word_key and instructions:
                            self.signs[language][word_key] = SignEntry(
                                word=word_normalized,
                                instructions=instructions,
                                category=category,
                                language=language
                            )
                            loaded_count += 1
                        else:
                            print(f"⚠️ {language} - Fila {row_num}: Datos incompletos")
                            
                    except Exception as row_error:
                        print(f"⚠️ {language} - Error en fila {row_num}: {row_error}")
                        continue
                
                return loaded_count
                
        except Exception as e:
            error_msg = f"Error al cargar {csv_path}: {e}"
            print(error_msg)
            raise Exception(error_msg) from e
    
    def _normalize_word(self, word: str) -> str:
        """
        Normaliza una palabra para mostrar con formato consistente.
        
        Args:
            word: Palabra a normalizar
            
        Returns:
            Palabra normalizada (primera letra mayúscula, resto minúsculas)
        """
        if not word or not word.strip():
            return ""
        
        # Limpiar espacios y caracteres especiales
        cleaned = word.strip()
        
        # Manejar casos especiales con comas o múltiples palabras
        if ',' in cleaned:
            # Para casos como "Ambos, as" -> "Ambos, As"
            parts = [part.strip() for part in cleaned.split(',')]
            normalized_parts = []
            for part in parts:
                if part:
                    normalized_parts.append(part.capitalize())
            return ', '.join(normalized_parts)
        else:
            # Caso normal: primera letra mayúscula, resto minúsculas
            return cleaned.capitalize()

    def reload_database(self) -> None:
        """Recarga la base de datos desde todos los archivos CSV."""
        self.signs.clear()
        self._load_all_signs()
    
    def search_exact(self, word: str, language: str = "ecuatoriano") -> Optional[SignEntry]:
        """
        Busca una seña exacta en la base de datos.
        
        Args:
            word: Palabra a buscar (insensible a mayúsculas)
            language: Idioma en el que buscar
            
        Returns:
            SignEntry si se encuentra, None si no existe
        """
        if not word or not word.strip():
            return None
        
        if language not in self.signs:
            return None
        
        # Normalizar la búsqueda a minúsculas para la clave
        search_key = word.lower().strip()
        return self.signs[language].get(search_key)
    
    def search_exact_all_languages(self, word: str) -> Dict[str, Optional[SignEntry]]:
        """
        Busca una seña exacta en todos los idiomas disponibles.
        
        Args:
            word: Palabra a buscar
            
        Returns:
            Diccionario con idioma como clave y SignEntry como valor (None si no se encuentra)
        """
        results = {}
        for language in self.signs.keys():
            results[language] = self.search_exact(word, language)
        return results
    
    def search_fuzzy(self, word: str, max_results: int = 5, 
                    min_similarity: float = 0.3, language: str = "ecuatoriano") -> List[Tuple[SignEntry, float]]:
        """
        Busca señas similares usando coincidencia difusa.
        
        Args:
            word: Palabra a buscar
            max_results: Número máximo de resultados
            min_similarity: Umbral mínimo de similitud (0.0 - 1.0)
            language: Idioma en el que buscar
            
        Returns:
            Lista de tuplas (SignEntry, similarity_score) ordenada por similitud
        """
        if not word or not word.strip():
            return []
        
        if language not in self.signs:
            return []
        
        word = word.lower().strip()
        matches = []
        
        for sign_word, sign_entry in self.signs[language].items():
            similarity = difflib.SequenceMatcher(None, word, sign_word).ratio()
            if similarity >= min_similarity:
                matches.append((sign_entry, similarity))
        
        # Ordenar por similitud descendente
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:max_results]
    
    def search_partial(self, partial_word: str, max_results: int = 10) -> List[SignEntry]:
        """
        Busca señas que contengan la palabra parcial.
        
        Args:
            partial_word: Parte de la palabra a buscar
            max_results: Número máximo de resultados
            
        Returns:
            Lista de SignEntry que contienen la palabra parcial
        """
        if not partial_word or not partial_word.strip():
            return []
        
        partial_word = partial_word.lower().strip()
        matches = []
        
        for sign_word, sign_entry in self.signs.items():
            if partial_word in sign_word:
                matches.append(sign_entry)
                if len(matches) >= max_results:
                    break
        
        return matches
    
    def search_by_category(self, category: str, language: str = "ecuatoriano", max_results: int = 20) -> List[SignEntry]:
        """
        Busca señas por categoría específica.
        
        Args:
            category: Categoría a buscar
            language: Idioma en el que buscar
            max_results: Número máximo de resultados
            
        Returns:
            Lista de SignEntry de la categoría especificada
        """
        if not category or not category.strip():
            return []
        
        if language not in self.signs:
            return []
        
        category = category.lower().strip()
        matches = []
        
        for sign_entry in self.signs[language].values():
            if category in sign_entry.category.lower():
                matches.append(sign_entry)
                if len(matches) >= max_results:
                    break
        
        return matches
    
    def get_all_words(self) -> List[str]:
        """
        Retorna todas las palabras disponibles en la base de datos.
        
        Returns:
            Lista ordenada de todas las palabras
        """
        return sorted(list(self.signs.keys()))
    
    def get_all_categories(self, language: str = "ecuatoriano") -> List[str]:
        """
        Obtiene todas las categorías disponibles.
        
        Args:
            language: Idioma del que obtener las categorías
            
        Returns:
            Lista de categorías únicas ordenadas alfabéticamente
        """
        if language not in self.signs:
            return []
        
        categories = set()
        for sign_entry in self.signs[language].values():
            if sign_entry.category:
                categories.add(sign_entry.category)
        
        return sorted(list(categories))
    
    def get_all_categories_all_languages(self) -> Dict[str, List[str]]:
        """
        Obtiene todas las categorías de todos los idiomas.
        
        Returns:
            Diccionario con idioma como clave y lista de categorías como valor
        """
        result = {}
        for language in self.signs.keys():
            result[language] = self.get_all_categories(language)
        return result
    
    def get_random_signs(self, count: int = 5, language: str = "ecuatoriano") -> List[SignEntry]:
        """
        Obtiene señas aleatorias de la base de datos.
        
        Args:
            count: Número de señas aleatorias a obtener
            language: Idioma del que obtener las señas
            
        Returns:
            Lista de SignEntry aleatorias
        """
        if language not in self.signs or not self.signs[language]:
            return []
        
        available_signs = list(self.signs[language].values())
        actual_count = min(count, len(available_signs))
        
        return random.sample(available_signs, actual_count)
    
    def get_signs_by_keywords(self, keywords: List[str], 
                             language: str = "ecuatoriano", max_results: int = 15) -> List[SignEntry]:
        """
        Obtiene señas que contengan palabras clave específicas.
        
        Args:
            keywords: Lista de palabras clave para filtrar
            language: Idioma en el que buscar
            max_results: Número máximo de resultados
            
        Returns:
            Lista de SignEntry que contienen las palabras clave
        """
        if not keywords or language not in self.signs:
            return []
        
        keywords = [kw.lower().strip() for kw in keywords if kw.strip()]
        if not keywords:
            return []
        
        matches = []
        
        for sign_entry in self.signs[language].values():
            # Buscar en palabra, instrucciones y categoría
            search_text = f"{sign_entry.word} {sign_entry.instructions} {sign_entry.category}".lower()
            
            if any(keyword in search_text for keyword in keywords):
                matches.append(sign_entry)
                if len(matches) >= max_results:
                    break
        
        return matches
    
    def get_database_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Obtiene estadísticas de la base de datos por idioma.
        
        Returns:
            Diccionario con estadísticas por idioma
        """
        stats = {}
        
        for language, signs in self.signs.items():
            categories = set()
            for sign_entry in signs.values():
                if sign_entry.category:
                    categories.add(sign_entry.category)
            
            stats[language] = {
                "total_signs": len(signs),
                "total_categories": len(categories)
            }
        
        return stats
    
    def get_common_words(self) -> List[str]:
        """
        Obtiene las palabras que están presentes en todos los idiomas.
        
        Returns:
            Lista de palabras comunes a todos los idiomas
        """
        if not self.signs:
            return []
        
        # Obtener las palabras de cada idioma
        language_words = {}
        for language, signs in self.signs.items():
            language_words[language] = set(signs.keys())
        
        # Encontrar la intersección de todas las palabras
        if language_words:
            common_words = set.intersection(*language_words.values())
            return sorted(list(common_words))
        
        return []
    
    def _calculate_average_instruction_length(self, language: str = "ecuatoriano") -> float:
        """
        Calcula la longitud promedio de las instrucciones.
        
        Args:
            language: Idioma para calcular el promedio
            
        Returns:
            Longitud promedio de las instrucciones
        """
        if language not in self.signs or not self.signs[language]:
            return 0.0
        
        total_length = sum(len(sign.instructions) for sign in self.signs[language].values())
        return total_length / len(self.signs[language]) if self.signs[language] else 0.0
    
    def export_to_dict(self, language: str = "ecuatoriano") -> Dict[str, Dict[str, str]]:
        """
        Exporta la base de datos a un diccionario.
        
        Args:
            language: Idioma a exportar
            
        Returns:
            Diccionario con la estructura de la base de datos
        """
        if language not in self.signs:
            return {}
        
        result = {}
        for word_key, sign_entry in self.signs[language].items():
            result[word_key] = {
                "word": sign_entry.word,
                "instructions": sign_entry.instructions,
                "category": sign_entry.category,
                "language": sign_entry.language
            }
        
        return result
    
    def export_all_to_dict(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Exporta toda la base de datos multiidioma a un diccionario.
        
        Returns:
            Diccionario con todos los idiomas y sus señas
        """
        result = {}
        for language in self.signs.keys():
            result[language] = self.export_to_dict(language)
        return result
    
    def __len__(self) -> int:
        """
        Retorna el número total de señas en todos los idiomas.
        
        Returns:
            Número total de señas
        """
        return sum(len(signs) for signs in self.signs.values())
    
    def __contains__(self, word: str) -> bool:
        """
        Verifica si una palabra existe en algún idioma.
        
        Args:
            word: Palabra a verificar
            
        Returns:
            True si la palabra existe en algún idioma
        """
        word_key = word.lower().strip()
        for signs in self.signs.values():
            if word_key in signs:
                return True
        return False
    
    def __getitem__(self, word: str) -> Optional[SignEntry]:
        """
        Obtiene una seña por palabra (busca en ecuatoriano por defecto).
        
        Args:
            word: Palabra a buscar
            
        Returns:
            SignEntry si se encuentra, None si no existe
        """
        return self.search_exact(word, "ecuatoriano")


# Funciones de utilidad para compatibilidad
def load_signs_database(csv_files: Optional[Dict[str, str]] = None) -> SignsDatabase:
    """
    Función de utilidad para cargar la base de datos de señas multiidioma.
    
    Args:
        csv_files: Diccionario con idioma como clave y ruta del CSV como valor
        
    Returns:
        Instancia de SignsDatabase cargada
    """
    return SignsDatabase(csv_files)


def get_default_database() -> SignsDatabase:
    """
    Obtiene una instancia por defecto de la base de datos.
    
    Returns:
        Instancia de SignsDatabase con configuración por defecto
    """
    return SignsDatabase()


# Instancia global para uso singleton (opcional)
_default_database: Optional[SignsDatabase] = None


def get_database_instance() -> SignsDatabase:
    """
    Obtiene la instancia singleton de la base de datos.
    
    Returns:
        Instancia singleton de SignsDatabase
    """
    global _default_database
    if _default_database is None:
        _default_database = SignsDatabase()
    return _default_database