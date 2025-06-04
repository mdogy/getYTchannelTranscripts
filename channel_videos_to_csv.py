import yt_dlp
import pandas as pd
from datetime import datetime, date
import re
import os
import sys
import argparse

def prompt_channel_url():
    return input('Enter YouTube channel URL: ').strip()

def get_channel_video_ids(channel_url):
    # Clean up the URL
    channel_url = channel_url.strip()
    
    # Handle different URL formats
    if '/channel/' in channel_url:
        channel_id = channel_url.split('/channel/')[-1].split('/')[0]
        channel_url = f'https://www.youtube.com/channel/{channel_id}/videos'
    elif '/c/' in channel_url:
        channel_url = channel_url.replace('/c/', '/channel/') + '/videos'
    elif '/@' in channel_url:
        # For @handles, we need to use a different approach
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'extract_flat_playlist': True,
            'playlist_items': 'all'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(channel_url, download=False)
                if info and 'entries' in info:
                    return info
            except Exception as e:
                print(f"Error with handle URL: {str(e)}")
                # Try alternative URL format
                channel_url = channel_url.replace('/@', '/channel/') + '/videos'
    else:
        # Assume it's a channel ID
        channel_url = f'https://www.youtube.com/channel/{channel_url}/videos'

    # Now get all videos from the channel
    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
        'extract_flat_playlist': True,
        'playlist_items': 'all',
        'ignoreerrors': True
    }
    
    print(f"Attempting to extract videos from: {channel_url}")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            if not info:
                print("No channel information found")
                return None
            if 'entries' not in info:
                print("No video entries found in channel")
                return None
            return info
        except Exception as e:
            print(f"Error extracting channel info: {str(e)}")
            return None

def parse_upload_date(upload_date_str):
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
    parser = argparse.ArgumentParser(description='Download YouTube channel video metadata to CSV.')
    parser.add_argument('--channel', type=str, help='YouTube channel URL')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD, default: today)')
    parser.add_argument('--log', type=str, help='Log file to write stdout and stderr')
    args = parser.parse_args()

    # Gather required and optional input BEFORE redirecting stdout/stderr
    channel_url = args.channel
    if not channel_url:
        channel_url = prompt_channel_url()

    # Parse dates or use defaults
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        except Exception:
            print(f"Invalid start date format: {args.start_date}")
            sys.exit(1)
    else:
        start_date = None
    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        except Exception:
            print(f"Invalid end date format: {args.end_date}")
            sys.exit(1)
    else:
        end_date = date.today()

    # Now redirect stdout/stderr if requested
    if args.log:
        log_file = open(args.log, 'w')
        sys.stdout = log_file
        sys.stderr = log_file

    info = get_channel_video_ids(channel_url)
    if not info:
        print("Failed to get channel information")
        sys.exit(1)

    channel_name = info.get('title', '')
    entries = info.get('entries', [])
    print(f"Found {len(entries)} entries in channel playlist.")
    
    rows = []
    for entry in entries:
        if not entry or not entry.get('id'):
            continue
            
        video_id = entry.get('id', '')
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        upload_date_str = entry.get('upload_date')
        
        if not upload_date_str:
            print(f"No upload_date for {video_url}, skipping.")
            continue
            
        upload_date = parse_upload_date(upload_date_str)
        if start_date and upload_date < start_date:
            print(f"{video_url} upload date {upload_date} before start date {start_date}, skipping.")
            continue
        if end_date and upload_date > end_date:
            print(f"{video_url} upload date {upload_date} after end date {end_date}, skipping.")
            continue
            
        title = entry.get('title', '')
        duration = entry.get('duration')
        if duration is not None:
            hours = int(duration) // 3600
            minutes = (int(duration) % 3600) // 60
            seconds = int(duration) % 60
            length_str = f"{hours}:{minutes:02}:{seconds:02}"
        else:
            length_str = ''
            
        print(f"Adding video: {title} ({video_url})")
        rows.append([
            video_id,
            channel_name,
            channel_url,
            video_url,
            title,
            length_str,
            upload_date_str
        ])

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
        'length',
        'upload_date'
    ])
    
    df.to_csv(csv_filename, index=False)
    print(f"CSV file written: {csv_filename}")
    if not rows:
        print("WARNING: No video data rows were written. Check the debug output above for possible causes.")

    if args.log:
        log_file.close()

if __name__ == '__main__':
    main() 