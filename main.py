from settings import *

from flask import redirect, url_for
from utils.api_response import *
from utils.files_data import *

import api.admin
import api.files
import events

@app.route("/")
async def mainPage():
    return redirect("/index.html")

def auto_updater():
    while True:
        try:
            files_data = {}
            initialize_files_data(files_data)
            manager.set_files_data(files_data)
        except: pass

if __name__ == '__main__':
    files_data = {}
    initialize_files_data(files_data)
    manager.set_files_data(files_data)
    app.run(
        host = settings['host'], 
        port = settings['port'],
        debug = settings['debug']
    )