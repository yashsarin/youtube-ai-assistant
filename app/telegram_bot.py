import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.vector_store import VectorStore
from app.utils import get_transcript, chunk_text, ask_llm

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("8621062492:AAHunfsI1z6pwWPdtuRSdwNhFK2j0cTKd2A")

# Initialize Vector DB
vector_db = VectorStore()

# Store user session state
user_state = {}


# ---------------------------
# START COMMAND
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a YouTube link to index the transcript.\n"
        "After that, you can ask questions about the video."
    )


# ---------------------------
# HANDLE TEXT MESSAGE
# ---------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id

    # If message contains YouTube link
    if "youtube.com" in user_message or "youtu.be" in user_message:
        await update.message.reply_text("📥 Fetching transcript...")

        try:
            transcript = get_transcript(user_message)

            chunks = chunk_text(transcript)

            vector_db.add_texts(chunks)

            user_state[chat_id] = True

            await update.message.reply_text(
                "✅ Transcript indexed successfully!\n"
                "Now ask me anything about this video."
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    else:
        # If transcript not indexed yet
        if not user_state.get(chat_id):
            await update.message.reply_text(
                "⚠ Please send a YouTube link first."
            )
            return

        # Semantic Search
        await update.message.reply_text("🔎 Searching relevant context...")

        try:
            relevant_chunks = vector_db.search(user_message, k=5)
            context_text = "\n\n".join(relevant_chunks)

            answer = ask_llm(context_text, user_message)

            await update.message.reply_text(answer)

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")


# ---------------------------
# RUN BOT
# ---------------------------
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()