# utils.py
import json
import logging
import os
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
 
# Set up logging (industry standard: file + console, with levels)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
 
class ConfigError(Exception):
    """Custom exception for config issues."""
    pass
 
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def load_config(config_path: str = "config.json") -> Dict[str, str]:
    """Load API configs from JSON, fallback to env vars for security."""
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        # Override with env vars (better for prod; e.g., set via dotenv)
        config['gemini_api_key'] = os.getenv('GEMINI_API_KEY', config.get('gemini_api_key'))
        config['hubspot_api_key'] = os.getenv('HUBSPOT_API_KEY', config.get('hubspot_api_key'))
        config['sender_email'] = os.getenv('SENDER_EMAIL', config.get('sender_email'))
         
        # Require Gemini key and other essentials (we now use Gemini for all agents)
        required_keys = ['hubspot_api_key', 'sender_email', 'gemini_api_key']
        missing = [k for k in required_keys if not config.get(k)]
        if missing:
            raise ConfigError(f"Missing config keys: {missing}")
         
        logger.info("Config loaded successfully.")
        return config
    except Exception as e:
        logger.error(f"Config load failed: {str(e)}")
        raise