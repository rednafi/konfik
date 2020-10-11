from konfik import Konfik

# Define the config path

CONFIG_PATH_TOML = "config.json"

# Initialize the Konfik class
konfik = Konfik(config_path=CONFIG_PATH_TOML)

# Serialize and print the confile file
konfik.serialize()

# Get the configuration dictionary from the konfik class
config_json = konfik.config

# Access and print the variables in toml file
print(config_json.title)
print(config_json.owner)
print(config_json.owner.dob)
print(config_json.database.ports)
print(config_json.servers.alpha.ip)
print(config_json.clients)
