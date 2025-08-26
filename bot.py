import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set in Render environment

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a DOC, DOCX, JPG, or PNG file and I’ll convert it to PDF for free!")

# Handle DOC/DOCX upload
async def handle_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    input_filename = update.message.document.file_name
    input_path = f"{update.message.document.file_unique_id}_{input_filename}"
    output_path = input_path.rsplit(".", 1)[0] + ".pdf"

    # Download file
    await file.download_to_drive(input_path)

    # Convert using LibreOffice
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", "."
    ])

    # Send PDF
    with open(output_path, "rb") as pdf:
        await update.message.reply_document(pdf)

    # Cleanup
    os.remove(input_path)
    os.remove(output_path)

# Handle image upload (JPG/PNG → PDF)
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file() if update.message.photo else await update.message.document.get_file()
    input_filename = getattr(update.message.document, "file_name", "image.jpg")
    input_path = f"{update.message.message_id}_{input_filename}"
    output_path = input_path.rsplit(".", 1)[0] + ".pdf"

    # Download file
    await file.download_to_drive(input_path)

    # Convert image to PDF
    image = Image.open(input_path).convert("RGB")
    image.save(output_path, "PDF", resolution=100.0)

    # Send PDF
    with open(output_path, "rb") as pdf:
        await update.message.reply_document(pdf)

    # Cleanup
    os.remove(input_path)
    os.remove(output_path)

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # DOC/DOCX
    app.add_handler(MessageHandler(
        filters.Document.FileExtension("doc") | filters.Document.FileExtension("docx"),
        handle_word
    ))
    # Images (jpg, jpeg, png)
    app.add_handler(MessageHandler(
        filters.Document.FileExtension("jpg") |
        filters.Document.FileExtension("jpeg") |
        filters.Document.FileExtension("png") |
        filters.PHOTO,
        handle_image
    ))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
