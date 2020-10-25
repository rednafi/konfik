from pathlib import Path

from konfik import Konfik

# Define the config path
BASE_DIR = Path(__file__).parent
CONFIG_PATH_JSON = BASE_DIR / "config.json"

# Initialize the Konfik class
konfik = Konfik(config_path=CONFIG_PATH_JSON)

# Serialize and print the confile file
konfik.show_config()

# Get the configuration dictionary from the konfik class
config = konfik.config

# Access and print the variables in toml file
print(config.title)
print(config.owner)
print(config.owner.dob)
print(config.database.ports)
print(config.servers.alpha.ip)
print(config.clients)
