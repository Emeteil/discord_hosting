from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from hashlib import sha256
import secrets
import yaml, os

with open("settings.yml", "r", encoding="utf-8") as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)

if settings['load_dotenv']:
    load_dotenv()

for env in settings['environment_variables']:
    settings[env] = os.environ.get(env)

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)

if "discord_webhooks_url" in settings:
    settings['hash_discord_webhooks_url'] = sha256(
        str(settings['discord_webhooks_url']).encode('utf-8')
    ).hexdigest()
    settings['discord_webhooks_url'] = settings['discord_webhooks_url']\
        .replace('discord.com', 'discordapp.com')

if "json" in dir(app) and hasattr(app.json, 'ensure_ascii'):
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    app.json.compact = False

app.config["JSON_AS_ASCII"] = False
app.config["JSON_SORT_KEYS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config['SECRET_KEY'] = settings.get("flask_secret", secrets.token_urlsafe(32))

if "admin_token" not in settings:
    settings['admin_token'] = secrets.token_urlsafe(32)

class FilesDataManager:
    def __init__(self):
        self._files_data = {}

    def get_files_data(self):
        return self._files_data

    def set_files_data(self, data):
        self._files_data = data

manager = FilesDataManager()