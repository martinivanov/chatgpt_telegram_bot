import yaml
import dotenv
from pathlib import Path

import os

config_dir = None
if "CONFIG_DIR" in os.environ:
    config_dir = Path(os.environ["CONFIG_DIR"]).resolve()
else:
    config_dir = Path(__file__).parent.parent.resolve() / "config"

print(config_dir)

# load yaml config
with open(config_dir / "config.yml", 'r') as f:
    config_yaml = yaml.safe_load(f)

# load .env config
dotenv.load_dotenv(config_dir / "config.env", override=False)
config_env = os.environ

# config parameters
telegram_token = config_yaml["telegram_token"]
openai_api_key = config_yaml["openai_api_key"]
use_chatgpt_api = config_yaml.get("use_chatgpt_api", True)
allowed_telegram_usernames = config_yaml["allowed_telegram_usernames"]
new_dialog_timeout = config_yaml["new_dialog_timeout"]
mongodb_uri = f"mongodb://mongo:{config_env['MONGODB_PORT']}"
webhook_port = config_env.get("PORT", 8000)
webhook_url = config_env.get("WEBHOOK_URL", None)
db_type = config_env.get("DB_TYPE", "mongodb")
gcs_project = config_env.get("GCS_PROJECT", None)
gcs_bucket = config_env.get("GCS_BUCKET", None)

# chat_modes
with open(config_dir / "chat_modes.yml", 'r') as f:
    chat_modes = yaml.safe_load(f)

# prices
chatgpt_price_per_1000_tokens = config_yaml.get("chatgpt_price_per_1000_tokens", 0.002)
gpt_price_per_1000_tokens = config_yaml.get("gpt_price_per_1000_tokens", 0.02)
whisper_price_per_1_min = config_yaml.get("whisper_price_per_1_min", 0.006)
