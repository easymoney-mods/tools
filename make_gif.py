import numpy as np
from moviepy import VideoFileClip

def make_gif(input_path, output_path, fps=15):
    print("Loading video...")
    try:
        clip = VideoFileClip(input_path)
    except Exception as e:
        print(f"Error loading video: {e}")
        print("Make sure your video is named 'my_video.mp4' and is in the exact same folder as this script!")
        return
    
    # Sample a frame at 30% into the video to avoid black intro screens
    frame = clip.get_frame(clip.duration * 0.3)
    gray = np.mean(frame, axis=2)
    
    threshold = 25 
    
    # Scan only the center crosshair to avoid corner watermarks
    height, width = gray.shape
    center_row = gray[height // 2, :]  
    center_col = gray[:, width // 2]   
    
    cols = np.where(center_row > threshold)[0]
    rows = np.where(center_col > threshold)[0]
    
    if len(rows) > 0 and len(cols) > 0:
        top, bottom = rows[0], rows[-1]
        left, right = cols[0], cols[-1]
        
        # Add a 2-pixel padding to ensure a clean cut
        padding = 2
        top = min(top + padding, clip.h - 1)
        bottom = max(bottom - padding, 0)
        left = min(left + padding, clip.w - 1)
        right = max(right - padding, 0)

        print(f"Smart crop applied (ignoring corners): (L:{left} R:{right} T:{top} B:{bottom})")
        cropped = clip.cropped(x1=left, y1=top, x2=right, y2=bottom)
    else:
        print("No black bars detected.")
        cropped = clip

    print("Converting to GIF. This might take a moment depending on the video length...")
    cropped.write_gif(output_path, fps=fps)
    print(f"Success! Saved as {output_path}")

if __name__ == "__main__":
    # The script looks for this exact file name
    INPUT = "my_video.mp4" 
    OUTPUT = "final_loop.gif"
    
    make_gif(INPUT, OUTPUT)