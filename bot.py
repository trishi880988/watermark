import os
import cv2
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from PIL import Image, ImageDraw, ImageFont

# States
VIDEO, WATERMARK_TEXT = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎥 Send me a video to extract thumbnail & add watermark.")
    return VIDEO

async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    file = await video.get_file()
    await file.download_to_drive("input_video.mp4")
    await update.message.reply_text("✅ Video received! Now, send watermark text:")
    return WATERMARK_TEXT

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['watermark_text'] = text
    await update.message.reply_text("🟢 Processing thumbnail...")

    # Extract thumbnail using OpenCV
    cap = cv2.VideoCapture("input_video.mp4")
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("thumbnail.jpg", frame)
    cap.release()

    # Apply watermark on thumbnail
    img = Image.open("thumbnail.jpg").convert("RGBA")
    txt = Image.new('RGBA', img.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)
    font = ImageFont.truetype("arial.ttf", 40)
    text_width, text_height = draw.textsize(text, font=font)
    position = (img.size[0] - text_width - 20, img.size[1] - text_height - 20)
    draw.text(position, text, font=font, fill=(255,0,0,180))
    watermarked = Image.alpha_composite(img, txt)
    watermarked = watermarked.convert("RGB")
    watermarked.save("final_thumbnail.jpg")

    await update.message.reply_photo(photo=open("final_thumbnail.jpg", "rb"), caption="✅ Thumbnail watermarked successfully!")

    # Cleanup
    os.remove("input_video.mp4")
    os.remove("thumbnail.jpg")
    os.remove("final_thumbnail.jpg")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled!")
    return ConversationHandler.END

async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            VIDEO: [MessageHandler(filters.VIDEO, get_video)],
            WATERMARK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("✅ Bot is running!")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
