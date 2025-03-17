import os
import telebot
import moviepy.editor as mp
import random
import redis
from celery import Celery

# Heroku environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize bot and Redis
bot = telebot.TeleBot(BOT_TOKEN)
r = redis.from_url(REDIS_URL)

# Celery setup for background tasks
celery = Celery('tasks', broker=REDIS_URL)

# Temporary storage for videos
if not os.path.exists("downloads"):
    os.makedirs("downloads")

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
    
    # Store video path in Redis
    r.set(f'{user_id}_video_path', video_path)
    
    bot.reply_to(message, "✅ Video received! Now send me the watermark text 🖊️.")

@bot.message_handler(func=lambda message: r.exists(f'{message.chat.id}_video_path'))
def handle_watermark(message):
    user_id = message.chat.id
    watermark_text = message.text
    video_path = r.get(f'{user_id}_video_path').decode('utf-8')
    
    # Start background task
    process_video.delay(user_id, video_path, watermark_text)
    bot.reply_to(message, "🌀 Processing your video, please wait...")

# Celery task for video processing
@celery.task
def process_video(user_id, video_path, watermark_text):
    output_path = f'downloads/{user_id}_watermarked.mp4'
    
    # Apply watermark dynamically
    clip = mp.VideoFileClip(video_path)
    txt_clip = (mp.TextClip(watermark_text, fontsize=40, color='white', font="Arial-Bold")
                .set_position(lambda t: ('center', random.randint(50, int(clip.h - 50))))
                .set_duration(clip.duration)
                .margin(left=10, right=10, top=10, bottom=10, color=(0,0,0,0)))
    
    final = mp.CompositeVideoClip([clip, txt_clip])
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # Send the processed video back to the user
    with open(output_path, 'rb') as vid:
        bot.send_video(user_id, vid, caption="✅ Here's your watermarked video!")

    # Cleanup
    os.remove(video_path)
    os.remove(output_path)
    r.delete(f'{user_id}_video_path')

# Start the bot
bot.infinity_polling()
