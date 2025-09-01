import os
from multiprocessing import Pool
from PIL import Image, ImageTk
from PIL import Image as pil
from pkg_resources import parse_version
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
from pkg_resources import parse_version

if parse_version(pil.__version__)>=parse_version('10.0.0'):
    Image.ANTIALIAS=Image.LANCZOS
from moviepy.editor import VideoFileClip, CompositeVideoClip

# Input and output folders
speaking_folder = "" 
gameplay_folder = ""  
output_folder = ""   

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Target portrait resolution (e.g., 1080x1920 for 9:16 aspect ratio)
target_width = 1080
target_height = 1920

def process_combination(speaking_file, gameplay_file):
    speaking_path = os.path.join(speaking_folder, speaking_file)
    gameplay_path = os.path.join(gameplay_folder, gameplay_file)

    # Load videos with audio
    speaking_clip = VideoFileClip(speaking_path)
    gameplay_clip = VideoFileClip(gameplay_path)

    # Ensure videos are square or adjust to match
    if speaking_clip.w != speaking_clip.h or gameplay_clip.w != gameplay_clip.h:
        print(f"Warning: {speaking_file} or {gameplay_file} is not square. Resizing to square.")
        speaking_clip = speaking_clip.resize(min(speaking_clip.w, speaking_clip.h))
        gameplay_clip = gameplay_clip.resize(min(gameplay_clip.w, gameplay_clip.h))

    # Calculate heights for 45:55 split
    total_height = target_height
    top_height = int(total_height * 0.45)  
    bottom_height = int(total_height * 0.55)  

    # Resize and zoom speaking clip to fit 1080px width, slight zoom to remove black space
    target_speaking_width = target_width  
    speaking_scale = target_speaking_width / speaking_clip.w * 1.15  # 15% zoom to fill width
    speaking_resized = speaking_clip.resize(speaking_scale)
    speaking_resized = speaking_resized.crop(x_center=speaking_resized.w/2, y_center=speaking_resized.h/2,
                                           width=target_speaking_width, height=top_height)

    # Resize and zoom gameplay clip to fit 55% height, slightly zoomed in
    gameplay_scale = bottom_height / gameplay_clip.h * 1.2
    gameplay_resized = gameplay_clip.resize(gameplay_scale)
    gameplay_resized = gameplay_resized.crop(x_center=gameplay_resized.w/2, y_center=gameplay_resized.h/2,
                                           width=target_width, height=bottom_height)

    # Stack videos vertically, preserving audio from speaking clip (primary audio source)
    final_video = CompositeVideoClip([speaking_resized.set_position((0, 0)),
                                    gameplay_resized.set_position((0, top_height))],
                                    size=(target_width, target_height))

    # Set duration to the speaking clip's duration and keep its audio
    final_video = final_video.set_duration(speaking_clip.duration)
    final_video = final_video.set_audio(speaking_clip.audio) 


    speaking_base = os.path.splitext(speaking_file)[0]
    if speaking_base.startswith("Clip maker project-"):
        speaking_base = speaking_base[len("Clip maker project-"):] 
    gameplay_base = os.path.splitext(gameplay_file)[0]
    output_file = os.path.join(output_folder, f"{speaking_base}_{gameplay_base}.mp4")


    final_video.write_videofile(output_file, fps=60, codec="libx264", preset="ultrafast", audio_codec="aac")

    # Close the clips
    speaking_clip.close()
    gameplay_clip.close()
    print(f"Completed rendering: {output_file}")

# Get all speaking and gameplay files
speaking_files = [f for f in os.listdir(speaking_folder) if f.endswith((".mp4", ".mov"))]
gameplay_files = [f for f in os.listdir(gameplay_folder) if f.endswith((".mp4", ".mov"))]
combinations = [(s, g) for s in speaking_files for g in gameplay_files]  # All possible combinations

# Process combinations sequentially
if __name__ == '__main__':
    for speaking_file, gameplay_file in combinations:

        process_combination(speaking_file, gameplay_file)
