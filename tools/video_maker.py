import streamlit as st
import os
import requests
import tempfile
import platform
import urllib.parse
import random
import math
from moviepy import * # --- HELPER: Fix Font on Windows ---
def get_font_path():
    system = platform.system()
    if system == "Windows":
        potential_paths = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
            r"C:\Windows\Fonts\seguiemj.ttf"
        ]
        for path in potential_paths:
            if os.path.exists(path):
                return path
    return "Arial"

# --- 1. Robust AI Image Generator ---
def get_ai_image(prompt):
    """Fetches AI image with fallback to stock image on timeout."""
    image_path = None
    
    # Attempt 1: Pollinations AI
    try:
        # random seed + browser headers to prevent caching/blocking
        seed = random.randint(0, 99999)
        safe_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&nologo=true&seed={seed}&model=flux"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Increased timeout to 45s
        response = requests.get(url, stream=True, timeout=45, headers=headers)
        
        if response.status_code == 200:
            fd, path = tempfile.mkstemp(suffix=".jpg")
            with os.fdopen(fd, 'wb') as f:
                f.write(response.content)
            return path
    except Exception as e:
        print(f"AI Gen Warning: {e}")

    # Attempt 2: Fallback to Picsum
    try:
        print("Using Fallback Image...")
        seed = prompt.replace(" ", "")
        url = f"https://picsum.photos/seed/{seed}/1280/720"
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            fd, path = tempfile.mkstemp(suffix=".jpg")
            with os.fdopen(fd, 'wb') as f:
                f.write(response.content)
            return path
    except Exception as e:
        st.error(f"Image Error: {e}")
        return None

# --- 2. Main Video Logic ---
def generate_video_logic(prompt, music_file, volume, duration):
    resolution = (1280, 720)
    font_path = get_font_path()
    
    # A. Setup Background
    bg_image_path = get_ai_image(prompt)
    if bg_image_path:
        bg_clip = ImageClip(bg_image_path)
    else:
        bg_clip = ColorClip(size=resolution, color=(20, 20, 60))

    # Zoom Effect
    bg_clip = bg_clip.with_duration(duration).with_fps(24)
    bg_clip = bg_clip.with_effects([vfx.Resize(lambda t: 1 + (0.05 * t))]).with_position('center')

    # B. Setup Text
    try:
        txt_clip = TextClip(
            text=prompt,
            font=font_path,
            font_size=65,
            color='white',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(1100, 720),
            text_align='center'
        )
        txt_clip = (
            txt_clip.with_position('center')
            .with_duration(duration)
            .with_effects([vfx.FadeIn(1.0), vfx.CrossFadeOut(1.0)])
        )
        video = CompositeVideoClip([bg_clip, txt_clip], size=resolution)
    except:
        video = CompositeVideoClip([bg_clip], size=resolution)

    # C. AUDIO LOGIC (FIXED)
    music_temp_path = None
    if music_file:
        # 1. Save uploaded file to disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tfile:
            tfile.write(music_file.read())
            music_temp_path = tfile.name
        
        try:
            # 2. Load Audio
            audio = AudioFileClip(music_temp_path)
            
            # 3. MANUAL LOOPING (100% Safe)
            # If audio is shorter than video, repeat it.
            if audio.duration < duration:
                # Calculate how many times to repeat
                loop_count = math.ceil(duration / audio.duration)
                # Repeat the clip list and concatenate
                audio = concatenate_audioclips([audio] * loop_count)
            
            # 4. Trim to exact duration
            audio = audio.subclipped(0, duration)
            
            # 5. Set Volume
            audio = audio.with_volume_scaled(volume)
            
            # 6. Attach to video
            video = video.with_audio(audio)
            
        except Exception as e:
            st.error(f"Audio Processing Failed: {e}")
    
    # D. Render
    output_path = os.path.join(tempfile.gettempdir(), "ai_video.mp4")
    
    # Note: audio_codec='aac' is standard. If it fails, try 'libmp3lame'
    video.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac", 
        logger=None
    )
    
    # Clean up
    if bg_image_path and os.path.exists(bg_image_path):
        os.remove(bg_image_path)
    if music_temp_path and os.path.exists(music_temp_path):
        os.remove(music_temp_path)
        
    return output_path

# --- 3. Streamlit UI ---
def run_tool():
    st.header("🎬 Smart AI Video Generator")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_input("Enter Prompt:", placeholder="e.g. A futuristic city")
        duration = st.slider("Duration (sec)", 5, 30, 10)
    
    with col2:
        music = st.file_uploader("Upload Music (MP3)", type=["mp3"])
        vol = 0.5
        if music:
            vol = st.slider("Volume", 0.0, 1.0, 0.5)

    if st.button("Generate Video", type="primary"):
        if not prompt:
            st.warning("Enter a prompt!")
        else:
            with st.spinner("Generating... (Audio processing fixed)"):
                try:
                    path = generate_video_logic(prompt, music, vol, duration)
                    if os.path.exists(path):
                        st.success("✨ Done!")
                        st.video(path)
                        with open(path, "rb") as f:
                            st.download_button("Download", f, "video.mp4", "video/mp4")
                except Exception as e:
                    st.error(f"Error: {e}")