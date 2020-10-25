from pathlib import Path

from konfik import Konfik

# Define the config path
BASE_DIR = Path(__file__).parent
CONFIG_PATH_YAML = BASE_DIR / "config.yaml"

# Initialize the konfik class
konfik = Konfik(config_path=CONFIG_PATH_YAML)

# Serialize and print the confile file
konfik.show_config()

# Get the configuration dictionary from the konfik class
config = konfik.config

# Access and print the variables
print(config.title)
print(config.owner)
print(config.owner.dob)
print(config.database.ports)
print(config.servers.alpha.ip)
print(config.clients)
