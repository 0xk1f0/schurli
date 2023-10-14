import toml
from os import getenv, path
from schurli.src.bot import bot

# Load the config.toml and version file
VERSION = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
CFG_PATH = getenv("CONF_PATH") or "/var/lib/powerBot/config"
CONFIG = toml.load(path.join(CFG_PATH, "config.toml"))


def main():
    # Print hello message
    print(
        f"""
    Starting Version {VERSION}..

                  __               ___ 
       __________/ /_  __  _______/ (_)
      / ___/ ___/ __ \/ / / / ___/ / / 
     (__  ) /__/ / / / /_/ / /  / / /  
    /____/\___/_/ /_/\__,_/_/  /_/_/   

    ~ by 0xk1f0
    """
    )
    # Run this sht
    bot.run(CONFIG["discord"]["bot_token"])
