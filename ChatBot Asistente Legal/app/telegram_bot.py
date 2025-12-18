import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 🔹 Diccionario de leyes y endpoints
LAWS = {
    "Código del Trabajo": "http://127.0.0.1:8001/ask/Código del Trabajo",
    "Ley Organica de Educacion Intercultural LOEI": "http://127.0.0.1:8001/ask/Ley Organica de Educacion Intercultural LOEI",
    "Ley Orgánica de Transporte": "http://127.0.0.1:8001/ask/Ley Orgánica de Transporte",
    "Código Orgánico Integral Penal": "http://127.0.0.1:8001/ask/Código Orgánico Integral Penal"
}

# 🔹 Mensaje de bienvenida con botón "Empezar"
async def bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Bienvenido al *Asistente Legal*.\n\n"
        "Presiona el botón *Empezar* para ir al menú de leyes 🚀"
    )
    keyboard = [[InlineKeyboardButton("Empezar", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

# 🔹 Menú interactivo
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in LAWS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("📚 Selecciona la ley que deseas consultar:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("📚 Selecciona la ley que deseas consultar:", reply_markup=reply_markup)

# 🔹 Botón presionado
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_law = query.data

    if selected_law == "menu":
        await menu(update, context)
        return

    context.user_data["selected_law"] = selected_law
    await query.edit_message_text(
        text=f"✅ Has seleccionado: *{selected_law}*\n\nAhora escribe tu pregunta.",
        parse_mode="Markdown"
    )

# 🔹 Pregunta legal
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    selected_law = context.user_data.get("selected_law", "Código del Trabajo")
    api_url = LAWS[selected_law]

    payload = {"question": user_question, "top_k": 3}
    try:
        response = requests.post(api_url, json=payload)
        data = response.json()
        answer = data.get("answer", "No se encontró información relevante.")
    except Exception as e:
        answer = f"⚠️ Error al consultar la API: {e}"

    await update.message.reply_text(answer)

# 🔹 Lanzamiento del bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # ✅ Detecta saludos para iniciar
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)\b(hola|hol|buenas|hey|iniciar)\b'), bienvenida))

    # ✅ Botones
    app.add_handler(CallbackQueryHandler(button))

    # ✅ Preguntas legales (todo lo que no sea saludo)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.Regex(r'(?i)\b(hola|hol|buenas|hey|iniciar)\b'), handle_message))

    print("🤖 Bot legal activo en Telegram.")
    app.run_polling()