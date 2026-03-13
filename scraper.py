import yt_dlp
import json
import pandas as pd
import datetime
import imageio_ffmpeg

# Define all available fields and their user-friendly Excel column names
AVAILABLE_FIELDS = {
    '1': ('title', 'Video Name'),
    '2': ('url', 'Video URL'),
    '3': ('duration_str', 'Duration'),
    '4': ('tags', 'Tags'),
    '5': ('published_date', 'Published Date'),
    '6': ('views', 'Views'),
    '7': ('thumbnail', 'Thumbnail URL'),
    '8': ('channel', 'Channel Name'),
    '9': ('description', 'Description'),
    '10': ('likes', 'Like Count'),
    '11': ('comments', 'Comment Count'),
    '12': ('subscribers', 'Channel Subscribers'),
    '13': ('category', 'Category'),
    '14': ('is_live', 'Is Live/Stream')
}

def format_duration(seconds):
    """Convert seconds to an easily readable HH:MM:SS format"""
    if not seconds:
        return "Unknown"
    return str(datetime.timedelta(seconds=int(seconds)))

def get_playlist_info(playlist_url, fetch_all=True, start_index=None, end_index=None, selected_keys=None, download=False, resolution=None, interactive_res=False, browser=None):
    ydl_opts = {
        'extract_flat': False,
        'skip_download': True, # We handle downloads separately to allow interactive resolution picking
        'ignoreerrors': True,
        'quiet': False, # Showing output so user knows it's not frozen
        'no_warnings': True,
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    # Note: `(browser,)` or `(browser, None, None, None)` is what yt-dlp expects inside ydl_opts
    if browser:
        if isinstance(browser, tuple):
             ydl_opts['cookiesfrombrowser'] = browser
        else:
             ydl_opts['cookiesfrombrowser'] = (browser,)
    if not fetch_all:
        if start_index:
            ydl_opts['playliststart'] = start_index
        if end_index:
            ydl_opts['playlistend'] = end_index
            
        print(f"\nStarting extraction for videos {start_index} to {end_index}...")
    else:
        print(f"\nStarting deep extraction of all videos from: {playlist_url}")
        
    print("This may take some time depending on the number of videos...")

    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We must pass the dynamic download boolean here so yt-dlp actually pulls the MP4 files
            playlist_dict = ydl.extract_info(playlist_url, download=False)
            
        if not playlist_dict:
            print("No data found or not a valid URL.")
            return []
            
        # If 'entries' is present, it's a playlist. Otherwise, it's likely a single video.
        if 'entries' in playlist_dict:
            entries = playlist_dict.get('entries', [])
        else:
            entries = [playlist_dict]

        for i, entry in enumerate(entries, 1):
            if not entry:
                continue
                
            # Build the raw data dictionary
            duration_sec = entry.get('duration')
            title = entry.get('title', f"Video_{i}")
            
            # Prioritize webpage_url so yt-dlp parses it as a YouTube video instead of a direct file link
            video_url = entry.get('webpage_url')
            if not video_url and entry.get('id'):
                video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
            if not video_url:
                video_url = entry.get('url')
                
            raw_data = {
                'title': title,
                'url': video_url,
                'duration_str': format_duration(duration_sec),
                'tags': ", ".join(entry.get('tags', [])) if entry.get('tags') else "",
                'published_date': entry.get('upload_date'), # Format: YYYYMMDD
                'views': entry.get('view_count'),
                'thumbnail': entry.get('thumbnail'),
                'channel': entry.get('channel') or entry.get('uploader'),
                'description': entry.get('description'),
                'likes': entry.get('like_count'),
                'comments': entry.get('comment_count'),
                'subscribers': entry.get('channel_follower_count'),
                'category': ", ".join(entry.get('categories', [])) if entry.get('categories') else "",
                'is_live': entry.get('is_live') or entry.get('was_live', False)
            }
            
            # Filter the dictionary to only include what the user selected
            vid_data = {}
            for key in selected_keys:
                vid_data[key] = raw_data.get(key)
                
            videos.append(vid_data)
            
            if download and video_url:
                import os
                if not os.path.exists('downloads'):
                    os.makedirs('downloads')
                    
                target_res = resolution
                
                if interactive_res:
                    print(f"\n==============================================")
                    print(f"Video: {title}")
                    
                    formats = entry.get('formats', [])
                    res_set = set()
                    for f in formats:
                        h = f.get('height')
                        if h and isinstance(h, int):
                            res_set.add(h)
                    
                    res_list = sorted(list(res_set), reverse=True)
                    if not res_list:
                        print("No specific resolutions found. Defaulting to best.")
                        target_res = 'best'
                    else:
                        print("Available Resolutions:")
                        for idx, r in enumerate(res_list, 1):
                            print(f"  {idx} - {r}p")
                        print(f"  {len(res_list) + 1} - Best Available (Highest Quality)")
                        
                        ans = input("\nEnter your choice for this video: ").strip()
                        try:
                            ans_idx = int(ans) - 1
                            if 0 <= ans_idx < len(res_list):
                                target_res = str(res_list[ans_idx])
                            else:
                                target_res = 'best'
                        except:
                            target_res = 'best'
                            
                dl_opts = {
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'ignoreerrors': True,
                    'quiet': False, # Allow base output but the corrected URL fixes the generic log spam
                    'no_warnings': True,
                    'noprogress': False,
                    'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
                }
                
                if browser:
                    if isinstance(browser, tuple):
                         dl_opts['cookiesfrombrowser'] = browser
                    else:
                         dl_opts['cookiesfrombrowser'] = (browser,)
                
                if target_res and target_res != 'best':
                    dl_opts['format'] = f'bestvideo[height<={target_res}]+bestaudio/best[height<={target_res}]/best'
                    dl_opts['merge_output_format'] = 'mp4'
                else:
                    dl_opts['format'] = 'bestvideo+bestaudio/best'
                    dl_opts['merge_output_format'] = 'mp4'
                    
                print(f"--> Downloading '{title}' at " + (f"{target_res}p" if target_res != 'best' else "best quality") + "...")
                with yt_dlp.YoutubeDL(dl_opts) as dl_ydl:
                    dl_ydl.download([video_url])
            
    except Exception as e:
        print(f"Error fetching playlist info: {e}")
        
    return videos

if __name__ == "__main__":
    url = input("\n[1] Enter YouTube Playlist URL: ").strip()
    if not url:
        print("URL cannot be empty.")
        exit()

    # ---- NEW SELECTION MENU FOR COLUMNS ----
    print("\n[2] Select Data Columns to Extract:")
    print("  0 - Extract EVERYTHING (Recommended)")
    for key, val in AVAILABLE_FIELDS.items():
        print(f"  {key} - {val[1]}")
    
    col_choice = input("\nEnter chosen numbers (e.g. 1,2,4) or press ENTER to extract everything: ").strip()
    
    selected_keys = []
    selected_names = {}
    
    if not col_choice or col_choice == '0':
        # Default: Everything
        for data_key, excel_name in AVAILABLE_FIELDS.values():
            selected_keys.append(data_key)
            selected_names[data_key] = excel_name
    else:
        # Parse user selection
        choices = [c.strip() for c in col_choice.split(',')]
        for c in choices:
            if c in AVAILABLE_FIELDS:
                data_key = AVAILABLE_FIELDS[c][0]
                excel_name = AVAILABLE_FIELDS[c][1]
                
                selected_keys.append(data_key)
                selected_names[data_key] = excel_name

    if not selected_keys:
        print("No valid columns selected! Defaulting to EVERYTHING.")
        for data_key, excel_name in AVAILABLE_FIELDS.values():
            selected_keys.append(data_key)
            selected_names[data_key] = excel_name

    # ---- EXISTING RANGE MENU ----
    print("\n[3] Select Extraction Option:")
    print("  1 - Scrape ALL videos in the playlist (Default)")
    print("  2 - Scrape a Specific Range (e.g., video 2 to 10)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()

    fetch_all = True
    start_index = None
    end_index = None

    if choice == '2':
        fetch_all = False
        try:
            start_input = input("Enter the starting video number (e.g., 2): ").strip()
            end_input = input("Enter the ending video number (e.g., 10): ").strip()
            
            start_index = int(start_input) if start_input else 1
            end_index = int(end_input) if end_input else None
        except ValueError:
            print("Invalid range input. Please execute the script again using numbers.")
            exit()
            
    # ---- VIDEO DOWNLOAD MENU ----
    print("\n[4] Download Video Files?")
    print("  1 - No, just extract metadata to Excel (Default)")
    print("  2 - Yes, ALSO download the actual video files (.mp4) to a 'downloads' folder")
    
    dl_choice = input("\nEnter choice (1 or 2): ").strip()
    download_videos = (dl_choice == '2')

    resolution = 'best'
    interactive_res = False
    
    if download_videos:
        print("\n[5] Select Download Mode:")
        print("  1 - Same resolution for all downloaded videos")
        print("  2 - Select resolution for EACH video interactively")
        mode_choice = input("\nEnter choice (1 or 2): ").strip()
        
        if mode_choice == '2':
            interactive_res = True
        else:
            print("\n[6] Select Global Video Quality (Resolution):")
            print("  1 - Best Available (Highest Quality)")
            print("  2 - 1080p")
            print("  3 - 720p")
            print("  4 - 480p")
            print("  5 - 360p")
            
            res_choice = input("\nEnter your choice (1-5): ").strip()
            
            if res_choice == '2':
                resolution = '1080'
            elif res_choice == '3':
                resolution = '720'
            elif res_choice == '4':
                resolution = '480'
            elif res_choice == '5':
                resolution = '360'
            else:
                resolution = 'best'

    # ---- BROWSER AUTHENTICATION MENU ----
    print("\n[*] Select Browser for Authentication (Required to bypass YouTube bot detection):")
    print("  1 - Chrome (Default)")
    print("  2 - Edge")
    print("  3 - Firefox")
    print("  4 - Brave")
    print("  5 - Opera")
    print("  6 - Chrome (via keyring - use if option 1 fails)")
    print("  7 - None (Try anonymously - May fail on YouTube)")
    
    browser_choice = input("\nEnter your choice (1-7) or press ENTER for Chrome: ").strip()
    browser_map = {
        '1': 'chrome', 
        '2': 'edge', 
        '3': 'firefox', 
        '4': 'brave', 
        '5': 'opera', 
        '6': ('chrome', None, None, 'keyring'),
        '7': None
    }
    
    selected_browser = browser_map.get(browser_choice, 'chrome')
    if not browser_choice:
        selected_browser = 'chrome'

    # ---- START SCRAPE ----
    video_data = get_playlist_info(
        url, 
        fetch_all=fetch_all, 
        start_index=start_index, 
        end_index=end_index, 
        selected_keys=selected_keys,
        download=download_videos,
        resolution=resolution,
        interactive_res=interactive_res,
        browser=selected_browser
    )
    
    if video_data:
        # Save to EXCEL only (NO JSON)
        excel_output = 'playlist_data.xlsx'
        df = pd.DataFrame(video_data)
        
        # Rename the columns to what the user actually wants to see
        df.rename(columns=selected_names, inplace=True)
        
        df.to_excel(excel_output, index=False, engine='openpyxl')
            
        print(f"\n======================================")
        print(f"Successfully scraped {len(video_data)} videos.")
        print(f"Data saved perfectly to: '{excel_output}'")
    else:
        print("\nNo data scraped. Please check URL or network.")
