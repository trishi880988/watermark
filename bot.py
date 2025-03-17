import telebot
import os
import subprocess

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

# Create downloads directory if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    video_path = f'downloads/{chat_id}_input.mp4'

    with open(video_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    user_data[chat_id] = {'video_path': video_path}
    bot.reply_to(message, "✅ Video received! Now send me the watermark text.")

@bot.message_handler(func=lambda m: m.chat.id in user_data and 'text' not in user_data[m.chat.id])
def handle_watermark_text(message):
    chat_id = message.chat.id
    watermark_text = message.text
    user_data[chat_id]['text'] = watermark_text

    bot.reply_to(message, "⚙️ Applying watermark, please wait...")

    input_path = user_data[chat_id]['video_path']
    output_path = f'downloads/{chat_id}_output.mp4'

    # FFmpeg command to add moving watermark
    cmd = [
        'ffmpeg', '-i', input_path,
        '-vf', f"drawtext=text='{watermark_text}':fontcolor=white:fontsize=24:x='mod(t*50, W)':y='mod(t*30, H/2)':box=1:boxcolor=black@0.5:boxborderw=5",
        '-codec:a', 'copy', output_path
    ]

    subprocess.run(cmd)

    with open(output_path, 'rb') as video_file:
        bot.send_video(chat_id, video_file, caption="✅ Done! Here is your watermarked video.")

    # Cleanup
    os.remove(input_path)
    os.remove(output_path)
    user_data.pop(chat_id)

bot.polling()

