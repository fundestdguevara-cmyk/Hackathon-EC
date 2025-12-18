import os
import pandas as pd
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "RESULTS", "predicciones.csv")
PERSIST_DIRECTORY = os.path.join(BASE_DIR, "zoodatavision_store")
MODEL_NAME = "nomic-embed-text"

def load_and_process_data():
    """
    Lee el CSV y genera documentos enriquecidos (filas + resúmenes).
    """
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"No se encuentra el CSV en: {CSV_PATH}")

    print(f"Procesando datos desde: {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    all_documents = []

    print("   - Indexando registros individuales...")
    for _, row in df.iterrows():
        clase_limpia = row['clase_predicha'].replace('_', ' ').lower()
        
        content = (
            f"Registro individual: Imagen {row['archivo']}. "
            f"Clase detectada: {row['clase_predicha']} ({clase_limpia}). "
            f"Confianza: {row['confianza']}."
        )
        meta = {
            "tipo": "registro_individual",
            "clase": row['clase_predicha'],
            "archivo": row['archivo']
        }
        all_documents.append(Document(page_content=content, metadata=meta))

    print("   - Generando resúmenes estratégicos...")
    
    conteo = df['clase_predicha'].value_counts()
    
    conteo_text = "RESUMEN OFICIAL DE CANTIDADES Y CLASES (USAR PARA CONTEOS):\n"
    conteo_text += f"Total de imágenes analizadas: {len(df)}.\n"
    conteo_text += "Desglose por clase detectada:\n"
    
    for clase, cantidad in conteo.items():
        nombre_natural = clase.replace('_', ' ').lower() + "s" # Pluralización simple
        conteo_text += f"- Clase '{clase}' ({nombre_natural}): {cantidad} detecciones.\n"
    
    all_documents.append(Document(page_content=conteo_text, metadata={"tipo": "resumen_global"}))

    # Resumen de Estadísticas de Confianza
    stats_text = (
        f"ESTADÍSTICAS DE CONFIANZA:\n"
        f"- Promedio global: {df['confianza'].mean():.4f}\n"
        f"- Mínima: {df['confianza'].min():.4f}\n"
        f"- Máxima: {df['confianza'].max():.4f}\n"
    )
    all_documents.append(Document(page_content=stats_text, metadata={"tipo": "resumen_stats"}))

    return all_documents

def get_vector_store():
    embedding_function = OllamaEmbeddings(model=MODEL_NAME)

    if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
        return Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_function, collection_name="zoodatavision_knowledge")

    print("Creando nueva base de datos vectorial...")
    docs = load_and_process_data()
    
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_function,
        persist_directory=PERSIST_DIRECTORY,
        collection_name="zoodatavision_knowledge"
    )
    print(f"Base de datos guardada en: {PERSIST_DIRECTORY}")
    return vector_store

def retrieve_info(query: str):
    try:
        vector_store = get_vector_store()
    except Exception as e:
        return f"Error al acceder a la base de datos: {e}"

    results = vector_store.similarity_search(query, k=4)
    

    summary_docs = vector_store.get(where={"tipo": "resumen_global"})
    
    context_text = ""
    
    if summary_docs and summary_docs['documents']:
        global_summary = summary_docs['documents'][0]
        context_text += f"--- DATOS GLOBALES (Prioridad para conteos) ---\n{global_summary}\n-------------------------------------------\n\n"

    context_text += "--- DETALLES RELEVANTES ENCONTRADOS ---\n"
    for doc in results:
        # Evitamos duplicar el resumen si ya salió en la búsqueda semántica
        if doc.metadata.get("tipo") != "resumen_global":
            context_text += f"{doc.page_content}\n"
            if doc.metadata.get("tipo") == "registro_individual":
                context_text += f"   [Ref: {doc.metadata.get('archivo', 'N/A')}]\n"
            context_text += "---\n"
    
    return context_text

if __name__ == "__main__":
    print("\n🦁 Probando Data Loader Mejorado...")
    # Prueba crítica
    preguntas = ["¿Cuántos mamíferos grandes hay?", "¿Qué clases existen?"]
    for p in preguntas:
        print(f"\n❓ Pregunta: {p}")
        print(f"📄 Contexto generado:\n{retrieve_info(p)[:500]}...")