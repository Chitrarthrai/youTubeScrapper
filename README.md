# YouTube Playlist & Video Data Scraper

A powerful, intuitive Python tool to scrape deep metadata and video files from YouTube playlists and channels using `yt-dlp`. 

It securely extracts over a dozen data points (including video name, URL, duration, description, tags, likes, category, and more) and saves everything cleanly to an Excel file (`.xlsx`). It also gives you the option to download the actual high-quality `.mp4` video files to your hard drive, completely automating the merging of video and audio with a localized FFmpeg installation.

---

## 🚀 Quick Start (Windows)

We have built a fully automated batch script so you don't need to manually type commands!

### Step 1: Initialize
Ensure you have **Python 3.8+** installed on your system.

### Step 2: Run the Script
Simply **Double-Click** the `run_scraper.bat` file from your File Explorer. 

- The script will automatically create a Virtual Environment strictly for this project.
- It will automatically download, install, and update all required packages (including a localized, portable FFmpeg binary via `imageio-ffmpeg`).
- A stylish terminal will open and ask for your YouTube URL.

*(Note: Do NOT press `Ctrl+C` while it is loading, as that will force-kill the program!)*

---

## 🛠 Features & Menus

Once you input your YouTube URL, the scraper offers an interactive menu to safely customize your work:

### 1. Data Column Selection
You can choose exactly what data you want to extract into your Excel file.
- **Press `Enter`** to extract absolutely ALL available metadata (Recommended).
- Type comma-separated numbers (e.g., `1,2,4,10`) if you only want specific columns.

**Available Data Fields:**
1. Video Name
2. Video URL
3. Duration (Formatted as HH:MM:SS)
4. Tags
5. Published Date
6. Views
7. Thumbnail URL
8. Channel Name
9. Description
10. Like Count
11. Comment Count
12. Channel Subscribers
13. Category
14. Is Live/Stream

### 2. Custom Extraction Ranges
- **Choice 1:** Scrape **ALL** videos in the playlist/channel.
- **Choice 2:** Scrape a **Specific Range**. You will provide the `start` video number and `end` video number (e.g., videos 2 to 10).

### 3. Video Downloading & Resolution Selection
- **Skip Downloading:** Only extract the lightning-fast metadata to Excel.
- **Download Files:** Extract the metadata to Excel AND download the high-quality `.mp4` video files to a new `downloads/` folder!
  
If you choose to download files, you will be prompted with **Download Modes**:
- **Same resolution for all videos:** Set a global video quality (Best, 1080p, 720p, 480p, 360p) for the entire playlist.
- **Select resolution for EACH video interactively:** The script will list available resolutions for *each individual video* right before downloading it, allowing you to manually pick the exact quality on a case-by-case basis.

*(Note: The tool automatically uses `imageio-ffmpeg` to perfectly stitch separate audio and high-quality video formats together without requiring global FFmpeg system installations.)*

---

## 📂 Output

When scraping finishes:
1. All organized metadata is automatically exported to a clean Excel spreadsheet named **`playlist_data.xlsx`** inside this exact folder.
2. If you chose to download the videos, your stitched `.mp4` files will be safely stored inside the **`downloads/`** folder.

## 💻 Manual Developer Installation

If you prefer to run things manually via terminal rather than using the `.bat` file:

```powershell
# 1. Create Virtual Environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Install Requirements
pip install -r requirements.txt

# 4. Run Scraper
python scraper.py
```
