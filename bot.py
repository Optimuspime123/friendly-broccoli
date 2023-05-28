import os
import logging
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from reportlab.pdfgen import canvas
from docx2pdf import convert as docx2pdf_convert
from pydub import AudioSegment

# Replace with your bot token
BOT_TOKEN = 'your_bot_token_here'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hello! Send me a text message, .txt file, .docx file, or .flac file, and I will convert it.')

def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if update.message.document:
        file_id = update.message.document.file_id
        file_name, file_ext = os.path.splitext(update.message.document.file_name)

        if file_ext.lower() == '.txt':
            convert_txt_to_pdf(update, context, file_id, file_name)
        elif file_ext.lower() == '.docx':
            convert_docx_to_pdf(update, context, file_id, file_name)
        elif file_ext.lower() == '.flac':
            convert_flac_to_mp3(update, context, file_id, file_name)
        else:
            update.message.reply_text("File format not supported. Please send a .txt, .docx or .flac file.")
    elif update.message.text:
        convert_text_to_pdf(update, context, update.message.text)
    else:
        update.message.reply_text("Please send a text message, .txt file, .docx file, or .flac file.")

def convert_txt_to_pdf(update: Update, context: CallbackContext, file_id: str, file_name: str):
    txt_file = context.bot.get_file(file_id)
    pdf_output = BytesIO()
    c = canvas.Canvas(pdf_output)

    with BytesIO() as txt_stream:
        txt_file.download(out=txt_stream)
        txt_stream.seek(0)
        text = txt_stream.read().decode('utf-8')

    for i, line in enumerate(text.splitlines()):
        c.drawString(10, 800 - i * 15, line)

    c.save()
    pdf_output.seek(0)
    context.bot.send_document(chat_id=update.message.chat_id, document=InputFile(pdf_output, filename=f"{file_name}.pdf"))

def convert_docx_to_pdf(update: Update, context: CallbackContext, file_id: str, file_name: str):
    docx_file = context.bot.get_file(file_id)

    with BytesIO() as docx_stream, BytesIO() as pdf_stream:
        docx_file.download(out=docx_stream)
        docx_stream.seek(0)
        docx2pdf_convert(docx_stream, pdf_stream)
        pdf_stream.seek(0)
        context.bot.send_document(chat_id=update.message.chat_id, document=InputFile(pdf_stream, filename=f"{file_name}.pdf"))

def convert_flac_to_mp3(update: Update, context: CallbackContext, file_id: str, file_name: str):
    flac_file = context.bot.get_file(file_id)

    with BytesIO() as flac_stream, BytesIO() as mp3_stream:
        flac_file.download(out=flac_stream)
        flac_stream.seek(0)
        flac_audio = AudioSegment.from_file(flac_stream, format='flac')
        flac_audio.export(mp3_stream, format='mp3')
        mp3_stream.seek(0)
        context.bot.send_audio(chat_id=update.message.chat_id, audio=InputFile(mp3_stream, filename=f"{file_name}.mp3"))

def convert_text_to_pdf(update: Update, context: CallbackContext, text: str):
    pdf_output = BytesIO()
    c = canvas.Canvas(pdf_output)

    for i, line in enumerate(text.splitlines()):
        c.drawString(10, 800 - i * 15, line)

    c.save()
    pdf_output.seek(0)
    context.bot.send_document(chat_id=update.message.chat_id, document=InputFile(pdf_output, filename="converted_text.pdf"))

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text | Filters.document, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
