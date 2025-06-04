import yt_dlp
import pandas as pd
from datetime import datetime, date
import re
import os

# Prompt user for input
def prompt_inputs():
    channel_url = input('Enter YouTube channel URL: ').strip()
    start_date_str = input('Enter start date (YYYY-MM-DD) [optional]: ').strip()
    end_date_str = input('Enter end date (YYYY-MM-DD) [default: today]: ').strip()
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else date.today()
    return channel_url, start_date, end_date

# Use yt-dlp to extract video info
def get_channel_video_ids(channel_url):
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
        'forcejson': True,
        'dump_single_json': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
    return info

def get_video_metadata(video_url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(video_url, download=False)

def parse_upload_date(upload_date_str):
    # yt-dlp returns upload_date as 'YYYYMMDD' string
    return datetime.strptime(upload_date_str, '%Y%m%d').date()

def get_unique_csv_filename(base_name, output_dir):
    base_path = os.path.join(output_dir, base_name)
    if not os.path.exists(base_path + '.csv'):
        return base_path + '.csv'
    i = 1
    while True:
        candidate = f"{base_path}_{i}.csv"
        if not os.path.exists(candidate):
            return candidate
        i += 1

def main():
    channel_url, start_date, end_date = prompt_inputs()
    info = get_channel_video_ids(channel_url)
    channel_name = info.get('title', '')
    entries = info.get('entries', [])
    rows = []
    for entry in entries:
        video_id = entry.get('id', '')
        if not video_id:
            continue
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        try:
            video_info = get_video_metadata(video_url)
        except Exception as e:
            print(f"Failed to get info for {video_url}: {e}")
            continue
        upload_date_str = video_info.get('upload_date')
        if not upload_date_str:
            continue
        upload_date = parse_upload_date(upload_date_str)
        if start_date and upload_date < start_date:
            continue
        if end_date and upload_date > end_date:
            continue
        title = video_info.get('title', '')
        duration = video_info.get('duration')
        # duration is in seconds, convert to H:MM:SS
        if duration is not None:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            length_str = f"{hours}:{minutes:02}:{seconds:02}"
        else:
            length_str = ''
        rows.append([
            video_id,
            channel_name,
            channel_url,
            video_url,
            title,
            length_str
        ])
    # Write to CSV in output directory
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    safe_channel_name = re.sub(r'\W+', '_', channel_name) or 'channel'
    csv_filename = get_unique_csv_filename(safe_channel_name + '_videos', output_dir)
    df = pd.DataFrame(rows, columns=[
        'video_id',
        'channel_name',
        'channel_url',
        'video_url',
        'title',
        'length'
    ])
    df.to_csv(csv_filename, index=False)
    print(f"CSV file written: {csv_filename}")

if __name__ == '__main__':
    main() 