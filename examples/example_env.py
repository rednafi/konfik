from pathlib import Path

from konfik import Konfik

# Define the config paths
BASE_DIR = Path(__file__).parent
CONFIG_PATH_ENV = BASE_DIR / "config.env"

# Initialize the Konfik class
konfik = Konfik(config_path=CONFIG_PATH_ENV)

# Serialize and print the dotenv config file
konfik.show_config()

# Access the variables in the config files via dot notation
config = konfik.config

# Access and print the variables in env file
print(config.TITLE)
print(config.NAME)
print(config.DOB)
print(config.SERVER)
print(config.PORT)
