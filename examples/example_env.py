from konfik import Konfik

# Define the config paths
CONFIG_PATH_ENV = "config.env"

# Initialize the Konfik class
konfik_env = Konfik(config_path=CONFIG_PATH_ENV)

# Serialize and print the dotenv config file
konfik_env.serialize()

# Access the variables in the config files via dot notation
config_env = konfik_env.config

# Access and print the variables in env file
print(config_env.TITLE)
print(config_env.NAME)
print(config_env.DOB)
print(config_env.SERVER)
print(config_env.PORT)
