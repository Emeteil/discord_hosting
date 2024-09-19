from utils.files_extractor_tools import *
from utils.api_response import *
from flask import request
from settings import *

@app.route("/api/files", methods=["GET"])
async def get_files():
    return apiResponse(
        list(
            manager.get_files_data().keys()
        )
    )

@app.route("/<path:file_path>", methods=["GET"])
async def get_file(file_path: str):
    if file_path not in manager.get_files_data():
        raise ApiError(404)

    file_info = manager.get_files_data()[file_path]
    segments = file_info['segments']
    file_size = file_info['file_size']
    
    segment_urls, segment_sizes = zip(*segments)
    
    range_header = request.headers.get('Range', None)
    
    content_type: str = get_content_type(file_path)
    
    if range_header is None:
        file_content = fetch_segments(segment_urls, segment_sizes, 0, file_size - 1)
        return build_full_file_response(
            file_content,
            content_type,
            file_size
        )
    
    start_byte, end_byte = parse_range_header(range_header, file_size)
    file_content = fetch_segments(segment_urls, segment_sizes, start_byte, end_byte)
    content_length = end_byte - start_byte + 1
    
    return build_partial_file_response(
        file_content,
        content_type,
        start_byte,
        end_byte,
        file_size,
        content_length
    )