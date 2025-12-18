"""
Procesador Principal de Señas

Integra la base de datos, reconocimiento de voz y síntesis de voz
para proporcionar una interfaz unificada de procesamiento de señas.

Autor: Signify Team
Versión: 2.0.0
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from audio.speech_engine import (
    SpeechEngine,
    VoiceRecognitionEngine,
    get_speech_engine,
    get_voice_recognition,
)
from database.signs_database import SignEntry, SignsDatabase, get_database_instance


@dataclass
class SearchResult:
    """
    Resultado de búsqueda de señas.
    
    Attributes:
        query: Consulta de búsqueda original
        found: Si se encontró una coincidencia exacta
        exact_match: Entrada de seña con coincidencia exacta
        similar_matches: Lista de coincidencias similares con puntuación
        search_time: Tiempo de búsqueda en segundos
        timestamp: Marca de tiempo de la búsqueda
    """
    query: str
    found: bool
    exact_match: Optional[SignEntry] = None
    similar_matches: List[Tuple[SignEntry, float]] = field(default_factory=list)
    search_time: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def get_best_match(self) -> Optional[SignEntry]:
        """
        Obtiene la mejor coincidencia disponible.
        
        Returns:
            SignEntry de la mejor coincidencia o None si no hay coincidencias
        """
        if self.exact_match:
            return self.exact_match
        elif self.similar_matches:
            return self.similar_matches[0][0]
        return None
    
    def get_confidence_score(self) -> float:
        """
        Obtiene el puntaje de confianza de la búsqueda.
        
        Returns:
            Puntaje de confianza entre 0.0 y 1.0
        """
        if self.exact_match:
            return 1.0
        elif self.similar_matches:
            return self.similar_matches[0][1]
        return 0.0


class SignProcessor:
    """
    Procesador principal que maneja todas las operaciones de señas.
    
    Integra la base de datos de señas, el motor de síntesis de voz
    y el reconocimiento de voz para proporcionar una interfaz unificada.
    """
    
    # Configuraciones por defecto
    DEFAULT_SIMILAR_RESULTS = 5
    DEFAULT_VOICE_DURATION = 5
    MIN_SIMILARITY_THRESHOLD = 0.3
    
    def __init__(self) -> None:
        """Inicializa el procesador de señas."""
        self.database = get_database_instance()
        self.speech_engine = get_speech_engine()
        self.voice_recognition = get_voice_recognition()
        self.search_history: List[SearchResult] = []
        self._category_keywords = self._initialize_category_keywords()
    
    def _initialize_category_keywords(self) -> Dict[str, List[str]]:
        """
        Inicializa las palabras clave por categoría.
        
        Returns:
            Diccionario con categorías y sus palabras clave asociadas
        """
        return {
            "saludos": ["hola", "adiós", "buenas", "chao", "saludo", "despedida"],
            "familia": ["padre", "madre", "hijo", "hermano", "esposo", "familia", "papá", "mamá"],
            "números": ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"],
            "días": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
            "meses": ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
            "alfabeto": list("abcdefghijklmnopqrstuvwxyz"),
            "trabajo": ["empleo", "trabajador", "jefe", "colegio", "universidad", "estudiar", "trabajo"],
            "preguntas": ["qué", "dónde", "cuánto", "para qué", "cómo", "cuándo", "quién"],
            "colores": ["rojo", "azul", "verde", "amarillo", "negro", "blanco", "rosa", "morado"],
            "animales": ["perro", "gato", "pájaro", "pez", "caballo", "vaca", "cerdo", "pollo"],
            "comida": ["agua", "pan", "leche", "carne", "pollo", "arroz", "fruta", "verdura"],
            "emociones": ["feliz", "triste", "enojado", "sorprendido", "miedo", "amor", "odio"]
        }
    
    def search_sign(self, query: str, include_similar: bool = True, 
                   max_similar: int = DEFAULT_SIMILAR_RESULTS, language: str = "ecuatoriano") -> SearchResult:
        """
        Busca una seña en la base de datos.
        
        Args:
            query: Palabra a buscar
            include_similar: Si incluir búsquedas similares
            max_similar: Número máximo de resultados similares
            language: Idioma en el que buscar
            
        Returns:
            SearchResult con los resultados de la búsqueda
        """
        if not query or not query.strip():
            return SearchResult(query="", found=False)
        
        start_time = time.time()
        # Normalizar la consulta para búsqueda pero mantener la original para mostrar
        original_query = query.strip()
        normalized_query = self._normalize_search_query(original_query)
        
        # Búsqueda exacta con la consulta normalizada
        exact_match = self.database.search_exact(normalized_query, language)
        
        # Búsqueda similar si no hay coincidencia exacta
        similar_matches = []
        if not exact_match and include_similar:
            similar_matches = self.database.search_fuzzy(
                normalized_query, 
                max_results=max_similar,
                min_similarity=self.MIN_SIMILARITY_THRESHOLD,
                language=language
            )
        
        search_time = time.time() - start_time
        
        result = SearchResult(
            query=original_query,  # Mantener la consulta original
            found=exact_match is not None,
            exact_match=exact_match,
            similar_matches=similar_matches,
            search_time=search_time
        )
        
        # Agregar a historial
        self.search_history.append(result)
        
        return result
    
    def _normalize_search_query(self, query: str) -> str:
        """
        Normaliza una consulta de búsqueda para mejorar las coincidencias.
        
        Args:
            query: Consulta original del usuario
            
        Returns:
            Consulta normalizada para búsqueda
        """
        if not query or not query.strip():
            return ""
        
        # Convertir a minúsculas y limpiar espacios
        normalized = query.strip().lower()
        
        # Remover caracteres especiales innecesarios pero mantener acentos
        # Solo limpiar espacios múltiples
        normalized = ' '.join(normalized.split())
        
        return normalized

    def search_partial(self, partial_query: str, max_results: int = 10) -> List[SignEntry]:
        """
        Busca señas que contengan la consulta parcial.
        
        Args:
            partial_query: Parte de la palabra a buscar
            max_results: Número máximo de resultados
            
        Returns:
            Lista de SignEntry que contienen la consulta parcial
        """
        if not partial_query or not partial_query.strip():
            return []
        
        return self.database.search_partial(partial_query.strip(), max_results)
    
    def process_voice_search(self, duration: int = DEFAULT_VOICE_DURATION) -> SearchResult:
        """
        Procesa búsqueda por voz.
        
        Args:
            duration: Duración de la grabación en segundos
            
        Returns:
            SearchResult con los resultados
            
        Raises:
            RuntimeError: Si el reconocimiento de voz no está disponible
        """
        if not self.voice_recognition.is_available():
            raise RuntimeError("Motor de reconocimiento de voz no disponible")
        
        # Reconocer voz
        transcribed_text = self.voice_recognition.record_and_transcribe(duration)
        
        if not transcribed_text:
            return SearchResult(
                query="",
                found=False,
                search_time=0.0
            )
        
        # Buscar la seña transcrita
        return self.search_sign(transcribed_text)
    
    def speak_search_result(self, result: SearchResult) -> None:
        """
        Reproduce el resultado de búsqueda usando síntesis de voz.
        
        Args:
            result: Resultado de búsqueda a reproducir
        """
        if not result.query:
            return
        
        if result.found and result.exact_match:
            self.speech_engine.speak_sign_instruction(
                result.exact_match.word,
                result.exact_match.instructions
            )
        elif result.similar_matches:
            # Reproducir la mejor coincidencia similar
            best_match, similarity_score = result.similar_matches[0]
            
            suggestion_text = (
                f"No encontré exactamente '{result.query}', "
                f"pero encontré '{best_match.word}' que es similar. "
                f"{best_match.instructions}"
            )
            
            self.speech_engine.speak_text(suggestion_text)
        else:
            self.speech_engine.speak_search_result(result.query, False)
    
    def speak_search_results(self, results: List[SearchResult]) -> None:
        """
        Reproduce una lista de resultados de búsqueda.
        
        Args:
            results: Lista de resultados de búsqueda a reproducir
        """
        if not results:
            return
        
        # Reproducir solo el primer resultado válido
        for result in results:
            if result and result.query:
                self.speak_search_result(result)
                break

    def get_random_signs(self, count: int = 5) -> List[SignEntry]:
        """
        Obtiene señas aleatorias para práctica.
        
        Args:
            count: Número de señas aleatorias a obtener
            
        Returns:
            Lista de SignEntry aleatorias
        """
        return self.database.get_random_signs(count)
    
    def get_signs_by_category(self, category: str, max_results: int = 20) -> List[SignEntry]:
        """
        Obtiene señas por categoría.
        
        Args:
            category: Categoría a buscar
            max_results: Número máximo de resultados
            
        Returns:
            Lista de señas de la categoría
        """
        if not category:
            return []
        
        category_lower = category.lower().strip()
        
        # Buscar por categoría directa primero
        direct_results = self.database.search_by_category(category, max_results)
        if direct_results:
            return direct_results
        
        # Buscar usando palabras clave predefinidas
        keywords = self._category_keywords.get(category_lower, [category])
        return self.database.get_signs_by_keywords(keywords, max_results)
    
    def get_available_categories(self) -> List[str]:
        """
        Obtiene las categorías disponibles.
        
        Returns:
            Lista de categorías disponibles
        """
        # Combinar categorías de la base de datos y predefinidas
        db_categories = self.database.get_all_categories()
        predefined_categories = list(self._category_keywords.keys())
        
        all_categories = set(db_categories + predefined_categories)
        return sorted(list(all_categories))
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de búsqueda.
        
        Returns:
            Diccionario con estadísticas detalladas
        """
        if not self.search_history:
            return {
                "total_searches": 0,
                "successful_searches": 0,
                "success_rate": 0.0,
                "average_search_time": 0.0,
                "average_confidence": 0.0,
                "most_searched_words": [],
                "database_stats": self.database.get_database_stats()
            }
        
        total_searches = len(self.search_history)
        successful_searches = sum(1 for result in self.search_history if result.found)
        success_rate = (successful_searches / total_searches) * 100
        average_search_time = sum(result.search_time for result in self.search_history) / total_searches
        average_confidence = sum(result.get_confidence_score() for result in self.search_history) / total_searches
        
        # Palabras más buscadas
        word_counts = {}
        for result in self.search_history:
            word = result.query.lower()
            if word:  # Evitar consultas vacías
                word_counts[word] = word_counts.get(word, 0) + 1
        
        most_searched = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_searches": total_searches,
            "successful_searches": successful_searches,
            "success_rate": success_rate,
            "average_search_time": average_search_time,
            "average_confidence": average_confidence,
            "most_searched_words": most_searched,
            "database_stats": self.database.get_database_stats()
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Obtiene métricas de rendimiento del procesador.
        
        Returns:
            Diccionario con métricas de rendimiento
        """
        if not self.search_history:
            return {
                "avg_search_time": 0.0,
                "min_search_time": 0.0,
                "max_search_time": 0.0,
                "total_processing_time": 0.0
            }
        
        search_times = [result.search_time for result in self.search_history]
        
        return {
            "avg_search_time": sum(search_times) / len(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times),
            "total_processing_time": sum(search_times)
        }
    
    def clear_search_history(self) -> None:
        """Limpia el historial de búsquedas."""
        self.search_history.clear()
    
    def get_recent_searches(self, limit: int = 10) -> List[SearchResult]:
        """
        Obtiene las búsquedas más recientes.
        
        Args:
            limit: Número máximo de búsquedas a retornar
            
        Returns:
            Lista de SearchResult más recientes
        """
        if not self.search_history:
            return []
        
        return self.search_history[-limit:] if len(self.search_history) >= limit else self.search_history
    
    def get_successful_searches(self, limit: Optional[int] = None) -> List[SearchResult]:
        """
        Obtiene solo las búsquedas exitosas.
        
        Args:
            limit: Número máximo de resultados (None para todos)
            
        Returns:
            Lista de SearchResult exitosos
        """
        successful = [result for result in self.search_history if result.found]
        
        if limit is not None:
            return successful[-limit:] if len(successful) >= limit else successful
        
        return successful
    
    def export_search_history(self) -> List[Dict[str, Any]]:
        """
        Exporta el historial de búsquedas.
        
        Returns:
            Lista de diccionarios con el historial de búsquedas
        """
        return [
            {
                "query": result.query,
                "found": result.found,
                "word": result.exact_match.word if result.exact_match else None,
                "instructions": result.exact_match.instructions if result.exact_match else None,
                "category": result.exact_match.category if result.exact_match else None,
                "search_time": result.search_time,
                "confidence_score": result.get_confidence_score(),
                "similar_matches_count": len(result.similar_matches),
                "timestamp": result.timestamp
            }
            for result in self.search_history
        ]
    
    def import_search_history(self, history_data: List[Dict[str, Any]]) -> None:
        """
        Importa historial de búsquedas desde datos externos.
        
        Args:
            history_data: Lista de diccionarios con datos de historial
        """
        for data in history_data:
            try:
                # Reconstruir SearchResult desde datos
                exact_match = None
                if data.get("word") and data.get("instructions"):
                    exact_match = SignEntry(
                        word=data["word"],
                        instructions=data["instructions"],
                        category=data.get("category", "General")
                    )
                
                result = SearchResult(
                    query=data["query"],
                    found=data["found"],
                    exact_match=exact_match,
                    search_time=data.get("search_time", 0.0),
                    timestamp=data.get("timestamp", time.time())
                )
                
                self.search_history.append(result)
                
            except (KeyError, TypeError) as e:
                print(f"⚠️ Error al importar entrada de historial: {e}")
    
    def test_audio_components(self) -> Dict[str, bool]:
        """
        Prueba los componentes de audio.
        
        Returns:
            Diccionario con el estado de los componentes de audio
        """
        return {
            "speech_engine_available": hasattr(self.speech_engine, '_is_initialized') and self.speech_engine._is_initialized,
            "voice_recognition_available": self.voice_recognition.is_available(),
            "microphone_available": self.voice_recognition.test_microphone() if self.voice_recognition.is_available() else False
        }
    
    def cleanup(self) -> None:
        """Limpia recursos del procesador."""
        try:
            self.speech_engine.cleanup()
            self.voice_recognition.cleanup()
        except Exception as e:
            print(f"⚠️ Error durante limpieza del procesador: {e}")


# Instancia global singleton del procesador
_processor_instance: Optional[SignProcessor] = None


def get_processor() -> SignProcessor:
    """
    Obtiene la instancia singleton del procesador.
    
    Returns:
        Instancia de SignProcessor
    """
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = SignProcessor()
    return _processor_instance


def search_and_speak(query: str, include_similar: bool = True) -> SearchResult:
    """
    Función de conveniencia para buscar y reproducir una seña.
    
    Args:
        query: Palabra a buscar
        include_similar: Si incluir búsquedas similares
        
    Returns:
        SearchResult con los resultados
    """
    processor = get_processor()
    result = processor.search_sign(query, include_similar)
    processor.speak_search_result(result)
    return result


def voice_search_and_speak(duration: int = 5) -> SearchResult:
    """
    Función de conveniencia para búsqueda por voz.
    
    Args:
        duration: Duración de la grabación en segundos
        
    Returns:
        SearchResult con los resultados
    """
    processor = get_processor()
    result = processor.process_voice_search(duration)
    processor.speak_search_result(result)
    return result


def cleanup_processor() -> None:
    """Limpia la instancia global del procesador."""
    global _processor_instance
    if _processor_instance:
        _processor_instance.cleanup()
        _processor_instance = None