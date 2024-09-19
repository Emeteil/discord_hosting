from utils.files_extractor_tools import *
import requests
import json
import time

def initialize_files_data(files_data):
    files_urls = f"{settings['disbox_server']}/files/get/{settings['hash_discord_webhooks_url']}"
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.get(files_urls)
            response.raise_for_status()
            json_data = response.json()
            break
        except (requests.RequestException, json.JSONDecodeError):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else: return
    
    files_path = set()
    def process_directory(directory, path=""):
        for name, info in directory['children'].items():
            current_path = f"{path}/{name}" if path else name
            
            if info['type'] == 'file':
                files_path.add(current_path)
            
            if info['type'] == 'file' and current_path in files_data:
                continue
            
            if info['type'] == 'file':
                try:
                    segment_ids = json.loads(info['content'])
                    file_size = info['size']
                    
                    segments = [get_segment_info(segment_id) for segment_id in segment_ids]
                    files_data[current_path] = {
                        'segments': segments,
                        'file_size': file_size
                    }
                except (json.JSONDecodeError, KeyError):
                    continue
            elif info['type'] == 'directory':
                process_directory(info, current_path)
    
    process_directory(json_data)
    
    for path in list(files_data.keys()):
        if path not in files_path:
            files_data.pop(path)