import sys
import os

# Aseguramos que Python pueda encontrar los módulos en la carpeta 'src' o actual
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import TypedDict, Literal
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

try:
    from src.prompts import router_prompt, response_prompt, chat_prompt
    from src.tools import search_zoodatavision_data
except ImportError:
    from prompts import router_prompt, response_prompt, chat_prompt
    from tools import search_zoodatavision_data


class AgentState(TypedDict):
    question: str
    category: str       
    context: str        
    answer: str         

llm = ChatOllama(
    model="gemma3:4b", 
    temperature=0,     
    top_p=0.9,
    top_k=40
)

def router_node(state: AgentState):
    print(f"\n[ROUTER] Analizando intención: '{state['question']}'")
    
    chain = router_prompt | llm | StrOutputParser()
    
    try:
        category = chain.invoke({"question": state["question"]})
        clean_category = category.strip().upper()
        
        if "SEARCH" in clean_category:
            clean_category = "SEARCH"
        elif "CHAT" in clean_category:
            clean_category = "CHAT"
        else:
            clean_category = "CHAT"
            
    except Exception as e:
        print(f"Error en Router: {e}")
        clean_category = "CHAT"
    
    print(f"[ROUTER] Decisión: {clean_category}")
    return {"category": clean_category}

def search_node(state: AgentState):
    print("[SEARCH] Consultando base de datos de ZooDataVision...")
    
    context_text = search_zoodatavision_data.invoke(state["question"])
    
    return {"context": context_text}

def generate_node(state: AgentState):
    print("[GENERATE] Redactando respuesta basada en datos...")
    
    chain = response_prompt | llm | StrOutputParser()
    response = chain.invoke({
        "context": state["context"], 
        "question": state["question"]
    })
    
    return {"answer": response}

def chat_node(state: AgentState):
    print("[CHAT] Generando respuesta conversacional...")
    
    chain = chat_prompt | llm | StrOutputParser()
    response = chain.invoke({"question": state["question"]})
    
    return {"answer": response}


workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("search", search_node)
workflow.add_node("generate", generate_node)
workflow.add_node("chat", chat_node)

workflow.set_entry_point("router")

def decide_next_step(state: AgentState) -> Literal["search", "chat"]:
    if state["category"] == "SEARCH":
        return "search"
    else:
        return "chat"

workflow.add_conditional_edges(
    "router",
    decide_next_step
)

workflow.add_edge("search", "generate")
workflow.add_edge("generate", END)
workflow.add_edge("chat", END)

app = workflow.compile()

# --- 5. BLOQUE DE PRUEBA ---
if __name__ == "__main__":
    print("🦁 --- BOT ZOODATAVISION INICIADO ---")
    print("(Escribe 'salir' para terminar)")
    
    while True:
        user_input = input("\n👤 Tú: ")
        if user_input.lower() in ["salir", "exit"]:
            break
            
        inputs = {"question": user_input}
        
        try:
            result = app.invoke(inputs)
            print(f"\n🤖 Bot:\n{result['answer']}")
        except Exception as e:
            print(f"\n❌ Error en la ejecución: {e}")