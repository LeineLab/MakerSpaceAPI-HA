DOMAIN = "makerspaceapi"

CONF_URL = "url"
CONF_TOKEN = "token"
CONF_SCAN_INTERVAL = "scan_interval"

PLATFORMS = ["sensor", "binary_sensor"]

# How often to poll the API (seconds), user-configurable via the options flow
DEFAULT_SCAN_INTERVAL = 300
MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 3600
