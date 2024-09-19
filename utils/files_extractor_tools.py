from typing import List
from urllib.parse import urlparse, parse_qs
from flask import Response
from settings import *
import mimetypes
import requests

def build_full_file_response(response, content_type: str, file_size: int) -> Response:
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(file_size),
        'Accept-Ranges': 'bytes'
    }
    return Response(response, headers=headers)

def build_partial_file_response(
        response, content_type: str, start_byte: int, end_byte: int, 
        file_size: int, content_length: int
    ) -> Response:
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(content_length),
        'Content-Range': f'bytes {start_byte}-{end_byte}/{file_size}',
        'Accept-Ranges': 'bytes'
    }
    return Response(response, status=206, headers=headers)

def parse_range_header(range_header: str, file_size: int) -> (int, int): # type: ignore
    range_value = range_header.split('=')[1]
    start_byte, end_byte = range_value.split('-')
    start_byte = int(start_byte)
    end_byte = int(end_byte) if end_byte else file_size - 1
    return start_byte, end_byte

def extract_domain_and_surl(url):
    return urlparse(url).netloc, parse_qs(urlparse(url).query).get('surl', [''])[0]

def fetch_segments(segment_urls: List[str], segment_sizes: List[int], start_byte: int, end_byte: int):
    current_byte = 0

    for url, size in zip(segment_urls, segment_sizes):
        segment_start = current_byte
        segment_end = current_byte + size - 1

        if end_byte < segment_start:
            break

        if start_byte > segment_end:
            current_byte += size
            continue

        fetch_start = max(start_byte, segment_start) - segment_start
        fetch_end = min(end_byte, segment_end) - segment_start

        response = requests.get(url, headers={'Range': f'bytes={fetch_start}-{fetch_end}'}, stream=True)
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=1024):
            yield chunk

        current_byte += size

def get_segment_info(segment_id) -> (str, int): # type: ignore
    response = requests.get(f"{settings['discord_webhooks_url']}/messages/{segment_id}")
    response.raise_for_status()
    json_data = response.json()
    return json_data['attachments'][0]['url'], json_data['attachments'][0]['size']

def get_content_type(file_path):
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type if content_type is not None else "application/octet-stream"