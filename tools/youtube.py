import streamlit as st
import yt_dlp
import os
import time

def run_tool():
    st.subheader("📺 YouTube Video Downloader")
    st.info("ℹ️ Works on Mobile! The server downloads it first, then sends it to you.")

    # 1. User Inputs URL
    url = st.text_input("Paste YouTube URL here:")
    
    if url:
        # 2. Setup options for yt-dlp
        # We use a temporary filename to avoid conflicts
        temp_file = "downloaded_video.mp4"
        
        ydl_opts = {
            'format': 'best[ext=mp4]',  # Get best quality MP4
            'outtmpl': temp_file,       # Save as this filename
            'quiet': True,
        }

        # 3. Download Button Logic
        if st.button("Fetch & Process Video"):
            progress_text = st.empty()
            progress_text.text("⏳ Server is downloading video... (Please wait)")
            
            try:
                # Run the download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_title = info.get('title', 'video')
                    
                # 4. Check if file exists
                if os.path.exists(temp_file):
                    progress_text.text("✅ Downloaded to Server! Ready for you.")
                    
                    # 5. Create the 'Download to Mobile' button
                    with open(temp_file, "rb") as file:
                        st.download_button(
                            label="⬇️ Download to Device",
                            data=file,
                            file_name=f"{video_title}.mp4",
                            mime="video/mp4"
                        )
                    
                    # Cleanup: Delete the file from server after showing button to save space
                    # Note: In a real app, you might use a scheduled cleanup, 
                    # but for now we keep it simple.
                    
            except Exception as e:
                st.error(f"Error: {e}")