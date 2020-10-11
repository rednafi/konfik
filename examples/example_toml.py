from konfik import Konfik

# Define the config path
CONFIG_PATH_TOML = "config.toml"

# Initialize the konfik class
konfik = Konfik(config_path=CONFIG_PATH_TOML)

# Serialize and print the confile file
konfik.serialize()

# Get the configuration dictionary from the konfik class
config_toml = konfik.config

# Access and print the variables
print(config_toml.title)
print(config_toml.owner)
print(config_toml.owner.dob)
print(config_toml.database.ports)
print(config_toml.servers.alpha.ip)
print(config_toml.clients)
