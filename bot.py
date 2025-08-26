import os
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document
from PIL import Image

# Telegram bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a Word (.docx) file or an image (JPG/PNG), and I’ll convert it into a PDF for you."
    )

# Convert Word .docx file into PDF
async def docx_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
        await file.download_to_drive(temp_docx.name)

        doc = Document(temp_docx.name)
        pdf_path = temp_docx.name.replace(".docx", ".pdf")

        c = canvas.Canvas(pdf_path, pagesize=letter)
        y = 750
        for para in doc.paragraphs:
            c.drawString(50, y, para.text)
            y -= 20
            if y < 50:
                c.showPage()
                y = 750
        c.save()

    with open(pdf_path, "rb") as pdf_file:
        await update.message.reply_document(pdf_file)

# Convert image (JPG/PNG) into PDF
async def image_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file() if update.message.photo else await update.message.document.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        await file.download_to_drive(temp_img.name)

        img = Image.open(temp_img.name)
        pdf_path = temp_img.name + ".pdf"

        img.convert("RGB").save(pdf_path, "PDF")

    with open(pdf_path, "rb") as pdf_file:
        await update.message.reply_document(pdf_file)

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FILE_EXTENSION("docx"), docx_to_pdf))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, image_to_pdf))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
