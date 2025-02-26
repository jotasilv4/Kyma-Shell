import json
import os, sys
from configparser import ConfigParser

os.system(f"wal -i {sys.argv[1]}")

wal_path = os.path.expanduser("~/.cache/wal/colors.json")

nitro_path = os.path.expanduser("~/.config/nitrogen/bg-saved.cfg")
config = ConfigParser()
config.read(nitro_path)

colors_template = os.path.expanduser("~/.config/Kyma-Shell/config/kyma-shell.css")
colors_config = os.path.expanduser("~/.config/Kyma-Shell/styles/colors.css")

with open(wal_path) as file:
    colors = json.load(file)

for section in config.sections():
    if "file" not in config[section]:
        config[section]["file"] = colors["wallpaper"]
    else:
        config[section]["file"] = colors["wallpaper"]

    if "mode" not in config[section]:
        config[section]["mode"] = "0"
    else:
        config[section]["mode"] = "0"
        
with open(nitro_path, "w") as configfile:
    config.write(configfile)

with open(colors_template, "r") as file:
    template = file.read()
    
# Configuration colors
set_colors = {
    "foreground": colors["special"]["foreground"],
    "background": "#080808",
    
    "primary": colors["colors"]["color14"],
    
    "active": colors["colors"]["color4"],
    "default": "#292828"
}

for key, color in set_colors.items():
    placeholder = "{{colors." + key + "}}"
    template = template.replace(placeholder, color)
    
with open(colors_config, "w") as file:
    file.write(template)

print(colors)
    
os.system("nitrogen --restore && fabric-cli exec kyma-shell 'app.set_css()'")