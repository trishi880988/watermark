import subprocess
import random

def add_watermark(input_video, output_video, text):
    move_x = random.randint(50, 300)
    move_y = random.randint(50, 300)
    
    cmd = [
        'ffmpeg',
        '-i', input_video,
        '-vf', f"drawtext=text='{text}':fontsize=24:fontcolor=white@0.6:x=mod(t*{move_x}, (w-text_w)):y=mod(t*{move_y}, (h-text_h)):box=1:boxcolor=black@0.3:boxborderw=5",
        '-codec:a', 'copy',
        output_video,
        '-y'
    ]
    subprocess.run(cmd, check=True)
