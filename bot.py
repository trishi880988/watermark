import telebot
import os
import moviepy.editor as mp
import random

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

user_data = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, "👋 Hello! Send me a video and I'll add your watermark text on it.\n\n1️⃣ Send video\n2️⃣ Enter watermark text\n3️⃣ Get video back 🎬")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.chat.id
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    video_path = f'downloads/{user_id}_input.mp4'
    with open(video_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    user_data[user_id] = {'video_path': video_path}
    
    bot.reply_to(message, "✅ Video received! Now send me the watermark text 🖊️.")

@bot.message_handler(func=lambda message: message.chat.id in user_data and 'video_path' in user_data[message.chat.id])
def handle_watermark(message):
    user_id = message.chat.id
    watermark_text = message.text
    video_path = user_data[user_id]['video_path']
    
    output_path = f'downloads/{user_id}_watermarked.mp4'
    
    bot.send_message(user_id, "🌀 Processing your video, please wait...")

    # Apply watermark dynamically
    clip = mp.VideoFileClip(video_path)
    txt_clip = (mp.TextClip(watermark_text, fontsize=40, color='white', font="Arial-Bold")
                .set_position(lambda t: ('center', random.randint(50, int(clip.h - 50))))
                .set_duration(clip.duration)
                .margin(left=10, right=10, top=10, bottom=10, color=(0,0,0,0)))
    
    final = mp.CompositeVideoClip([clip, txt_clip])
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')

    with open(output_path, 'rb') as vid:
        bot.send_video(user_id, vid, caption="✅ Here's your watermarked video!")

    # Cleanup
    os.remove(video_path)
    os.remove(output_path)
    user_data.pop(user_id)

bot.infinity_polling()


