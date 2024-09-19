from utils.api_response import *
from utils.files_data import *
from flask import request
from copy import deepcopy
from settings import *

@app.route("/api/admin/ping", methods=['GET'])
async def ping_server():
    return apiResponse({"message": "Pong!"})

@app.route("/api/admin/update_info", methods=['GET'])
async def update_info():
    if request.args['admin_token'] != settings['admin_token']:
        raise ApiError(401)
    
    files_data = deepcopy(manager.get_files_data())
    initialize_files_data(files_data)
    manager.set_files_data(files_data)
    return apiResponse("", 204)

@app.route("/error_page", methods=['GET'])
async def error_page_cheack():
    args = request.args
    status_code: int = int(args.get("code", 500))
    raise ApiError(
        code = status_code
    )