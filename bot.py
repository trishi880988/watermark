import os
from pyrogram import Client, filters
import ffmpeg
from PIL import Image, ImageDraw, ImageFont

# ---------- CONFIG ----------
API_ID = int(20219694)
API_HASH = "29d9b3a01721ab452fcae79346769e29"
BOT_TOKEN = "your_bot_token_here"  # <-- Sirf yaha apna bot token daal do
FONT_PATH = "Poppins-Bold.ttf"
WATERMARK_TEXT = "Join-@skillwithgaurav"

bot = Client("thumb_watermark_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@bot.on_message(filters.video & filters.private)
async def process_video(client, message):
    await message.reply("✅ Video Received! Processing thumbnail...")

    # Download video
    video_path = await message.download()
    thumb_raw = "thumb_raw.jpg"
    thumb_watermarked = "thumb_done.jpg"

    # Extract thumbnail using ffmpeg
    os.system(f"ffmpeg -i '{video_path}' -ss 00:00:01.000 -vframes 1 {thumb_raw}")

    # Open thumbnail image
    im = Image.open(thumb_raw).convert("RGB")
    draw = ImageDraw.Draw(im)
    W, H = im.size

    # Load font and position text
    font_size = int(H * 0.06)
    font = ImageFont.truetype(FONT_PATH, font_size)
    text = WATERMARK_TEXT
    text_width, text_height = draw.textsize(text, font=font)

    x = (W - text_width) / 2  # Center
    y = H - text_height - 80  # Bottom se thoda upar

    # Shadow
    draw.text((x+2, y+2), text, font=font, fill="black")
    # Main text
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
