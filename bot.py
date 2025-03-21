import os
from pyrogram import Client, filters
from PIL import Image, ImageDraw, ImageFont

# ---------- CONFIG ----------
API_ID = 20219694  # ✅ Integer hai, quotes me mat daalo
API_HASH = "your_api_hash"  # <-- apna API HASH daalo
BOT_TOKEN = "your_bot_token"  # <-- apna BOT TOKEN daalo
FONT_PATH = "Poppins-Bold.ttf"  # Font file ko isi naam se folder me rakho
WATERMARK_TEXT = "Join-@skillwithgaurav"

bot = Client("thumb_watermark_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.video & filters.private)
async def process_video(client, message):
    await message.reply("✅ Video Received! Processing thumbnail...")

    # Download the video
    video_path = await message.download()
    thumb_raw = "thumb_raw.jpg"
    thumb_watermarked = "thumb_done.jpg"

    # Extract thumbnail using ffmpeg
    os.system(f"ffmpeg -i \"{video_path}\" -ss 00:00:01.000 -vframes 1 {thumb_raw}")

    # Open thumbnail image
    im = Image.open(thumb_raw).convert("RGB")
    draw = ImageDraw.Draw(im)
    W, H = im.size

    # Load font and calculate position
    font_size = int(H * 0.06)
    font = ImageFont.truetype(FONT_PATH, font_size)
    text = WATERMARK_TEXT
    text_width, text_height = draw.textsize(text, font=font)

    x = (W - text_width) / 2
    y = H - text_height - 80

    # Apply shadow
    draw.text((x+2, y+2), text, font=font, fill="black")
    # Apply main text
    draw.text((x, y), text, font=font, fill="white")

    im.save(thumb_watermarked)

    await message.reply("✅ Watermark added! Sending video back...")

    # Send back video with watermarked thumbnail
    await message.reply_video(video=video_path, thumb=thumb_watermarked, caption="✅ Watermark done!")

    # Clean up
    os.remove(video_path)
    os.remove(thumb_raw)
    os.remove(thumb_watermarked)


print("🤖 Bot is running...")
bot.run()
