import os
import streamlit as st
import yt_dlp

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 YouTube Downloader")
st.caption("Download videos in your selected quality.")

# ============================================================
# INPUT
# ============================================================

url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

quality_options = {
    "Best Available": "bestvideo+bestaudio/best",
    "2160p (4K)": "bestvideo[height<=2160]+bestaudio/best",
    "1440p": "bestvideo[height<=1440]+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "360p": "bestvideo[height<=360]+bestaudio/best",
    "240p": "bestvideo[height<=240]+bestaudio/best",
    "144p": "bestvideo[height<=144]+bestaudio/best",
}

quality = st.selectbox(
    "Video Quality",
    list(quality_options.keys())
)

download_type = st.radio(
    "Download Type",
    ["MP4 Video", "MP3 Audio"],
    horizontal=True
)

# ============================================================
# DOWNLOAD
# ============================================================

if st.button("⬇️ Download", use_container_width=True):

    if not url.strip():
        st.error("Please enter a YouTube URL.")
        st.stop()

    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)

    status = st.empty()
    progress = st.progress(0)

    try:

        # ====================================================
        # COMMON OPTIONS
        # ====================================================

        common_options = {
            "noplaylist": True,

            # Retry
            "retries": 10,
            "fragment_retries": 10,
            "extractor_retries": 5,

            # Use IPv4
            "force_ipv4": True,

            # YouTube JavaScript challenge solving
            "js_runtimes": {
                "deno": {}
            },

            # Download EJS components when required
            "remote_components": {
                "ejs": ["github"]
            },

            "quiet": False,
        }

        # ====================================================
        # MP3
        # ====================================================

        if download_type == "MP3 Audio":

            ydl_opts = {
                **common_options,

                "format": "bestaudio/best",

                "outtmpl": os.path.join(
                    download_dir,
                    "%(title)s.%(ext)s"
                ),

                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }

        # ====================================================
        # MP4
        # ====================================================

        else:

            ydl_opts = {
                **common_options,

                "format": quality_options[quality],

                "outtmpl": os.path.join(
                    download_dir,
                    "%(title)s.%(ext)s"
                ),

                "merge_output_format": "mp4",
            }

        # ====================================================
        # START
        # ====================================================

        status.info("⏳ Getting video information...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            title = info.get(
                "title",
                "video"
            )

            filename = ydl.prepare_filename(info)

        # ====================================================
        # MP3 FILE EXTENSION
        # ====================================================

        if download_type == "MP3 Audio":

            filename = (
                os.path.splitext(filename)[0]
                + ".mp3"
            )

        # ====================================================
        # CHECK FILE
        # ====================================================

        if not os.path.exists(filename):

            # Sometimes the merged file has a different extension.
            possible_files = []

            base_name = os.path.splitext(filename)[0]

            for file in os.listdir(download_dir):

                full_path = os.path.join(
                    download_dir,
                    file
                )

                if file.startswith(
                    os.path.basename(base_name)
                ):
                    if os.path.isfile(full_path):
                        possible_files.append(full_path)

            if possible_files:
                filename = possible_files[0]

        # ====================================================
        # SUCCESS
        # ====================================================

        if os.path.exists(filename):

            progress.progress(100)

            status.success(
                "✅ Download completed!"
            )

            st.success(
                f"**{title}**"
            )

            with open(filename, "rb") as file:

                file_data = file.read()

            if download_type == "MP3 Audio":

                st.download_button(
                    label="📥 Save MP3",
                    data=file_data,
                    file_name=os.path.basename(
                        filename
                    ),
                    mime="audio/mpeg",
                    use_container_width=True
                )

            else:

                st.download_button(
                    label="📥 Save MP4",
                    data=file_data,
                    file_name=os.path.basename(
                        filename
                    ),
                    mime="video/mp4",
                    use_container_width=True
                )

        else:

            status.error(
                "❌ Download completed, "
                "but the output file was not found."
            )

    # ========================================================
    # ERROR
    # ========================================================

    except Exception as error:

        progress.empty()

        status.error(
            "❌ Download failed."
        )

        st.error(
            str(error)
        )
