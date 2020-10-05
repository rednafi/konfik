from konfik import Konfik

from pathlib import Path

BASE_DIR = Path(".").parent
CONFIG_PATH = BASE_DIR / "config.toml"

konfik = Konfik(config_path=CONFIG_PATH)

print(konfik.config.bash.var.A)
print(konfik.config.bash.var.C)

# config.run('bash.cmd.')
