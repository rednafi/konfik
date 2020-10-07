from pathlib import Path

from konfik import Konfik

BASE_DIR = Path(".").parent
CONFIG_PATH = BASE_DIR / "example_config.toml"
konfik = Konfik(config_path=CONFIG_PATH)
konfik.serialize()
# print(config.title)
# print(config.owner.name)
# print(config.owner.dob)
# print(config.database.ports)
# print(config.servers.alpha.ip)
# print(config.clients)
