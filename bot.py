import os
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import asyncio

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("watermark_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Ensure fonts directory exists
os.makedirs("fonts", exist_ok=True)

@app.on_message(filters.video & filters.private)
async def watermark_video(client, message: Message):
    if message.video.file_size > 314572800:  # 300MB = 300*1024*1024 bytes
        await message.reply_text("❌ Bhai 300MB se chhota video bhejna padega! 🚫")
        return

    await message.reply_text("✅ Video mila! Watermark lagaya ja raha hai... ⏳")

    video_path = await message.download()
    output_path = "watermarked.mp4"
    
    watermark_text = "Join-@skillwithgaurav"

    command = [
        "ffmpeg", "-i", video_path,
        "-vf",
        f"drawtext=fontfile=fonts/Poppins-Bold.ttf:text='{watermark_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=w/2+50*sin(2*PI*t/5):y=h/2+50*cos(2*PI*t/5):rotate=PI/4*t",
        "-preset", "ultrafast",
        "-threads", "1",
        "-c:a", "copy",
        output_path
    ]

    process = await asyncio.create_subprocess_exec(*command)
    await process.communicate()

    await message.reply_video(video=output_path, caption="✅ Watermark lag gaya bhai! 🎉")

    os.remove(video_path)
    os.remove(output_path)

app.run()
