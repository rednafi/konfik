from pathlib import Path

from konfik import Konfik

BASE_DIR = Path(".").parent

# Define the config paths
CONFIG_PATH_TOML = BASE_DIR / "example_config.toml"
CONFIG_PATH_ENV = BASE_DIR / "example_config.env"

# Initialize the Konfik class for toml config
konfik_toml = Konfik(config_path=CONFIG_PATH_TOML)

# Serialize and print the toml config file
konfik_toml.serialize()

# Initialize the Konfik class for dotenv config
konfik_env = Konfik(config_path=CONFIG_PATH_ENV)

# Serialize and print the dotenv config file
konfik_env.serialize()

# Access the variables in the config files via dot notation
config_toml = konfik_toml.config
config_env = konfik_env.config

# Access and print the variables in toml file
print(config_toml.title)
print(config_toml.owner.name)
print(config_toml.owner.dob)
print(config_toml.database.ports)
print(config_toml.servers.alpha.ip)
print(config_toml.clients)

# Access and print the variables in
print(config_env.TITLE)
print(config_env.NAME)
print(config_env.DOB)
print(config_env.SERVER)
print(config_env.PORT)
