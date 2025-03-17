import os
import telebot
from watermark import add_watermark
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎥 Send me a video to watermark!")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    video_path = f"downloads/{message.chat.id}_input.mp4"
    with open(video_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    user_data[message.chat.id] = video_path
    bot.reply_to(message, "✅ Video received! Now send me the watermark text.")

@bot.message_handler(func=lambda m: m.chat.id in user_data and m.text)
def handle_text(message):
    watermark_text = message.text
    input_path = user_data.pop(message.chat.id)
    output_path = f"downloads/{message.chat.id}_output.mp4"

    bot.reply_to(message, "⏳ Adding watermark... Please wait!")

    add_watermark(input_path, output_path, watermark_text)

    with open(output_path, 'rb') as video:
        bot.send_video(message.chat.id, video)

    os.remove(input_path)
    os.remove(output_path)

bot.polling()
