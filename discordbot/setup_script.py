# Very quick and ditry setup script
# This will get the base info for the bot running
# Lots of it isn't used yet, since channel IDs and role IDs need to be fixed
# You can skip those if you like and just stick with the bot token, prefix, and description

import json
from pathlib import Path
import time

settings = {}
channels = {}
roles = {}

if not Path("wallets.json").exists():
    with open("data/wallets.json","a+") as f:
        f.write("{}")

print("Hello! Thanks for using Amadeus!~ Let's get you set up real quick before we're up and running. You'll need the following on hand to get started:")
print("- Token\n- Description (Can be anything, shows in help message)\n- Prefix\n- Bot Owner ID\n- Server Owner ID\n- Log Channel ID\n- Bot Commands Channel ID\n- Welcome channel ID\n- Admin Role ID\n- Mod Role ID\n- Bot Role ID\n- Default Role ID (Assigned when a member joins)")
print("Current step: settings.json setup")

token = input("Bot token: ")
settings["token"] = token
desc = input("Bot description: ")
settings["description"] = desc
prefix = input("Bot prefix: ")
settings["prefix"] = prefix
ownerid = input("Bot owner ID: ")
settings["bot_owner"] = ownerid
serverowner = input("Server owner ID: ")
settings["server_owner"] = serverowner
with open("data/settings.json","w") as f:
    json.dump(settings, f, indent=2, sort_keys=True)

print("\nsettings.json setup complete~ Next up, channels:\nNote, this is unnecessary right now but will be used eventually. Fill these in if you like")

logs = input("Log channel ID: ")
channels["logs"] = logs
botcmds = input("Bot commands channel ID: ")
channels["bot-commands"] = botcmds
welcome = input("Welcome channel ID: ")
channels["welcome"] = welcome
with open("data/channels.json","w") as f:
    json.dump(channels, f, indent=2, sort_keys=True)

print("\nChannel setup complete~ Final setup step, roles:\nNote, this is also unnecessary right now but will again be used eventually. Fill these in if you like")

admin = input("Admin role ID: ")
roles["admin"] = admin
mod = input("Moderator role ID: ")
roles["mod"] = mod
bot = input("Bot role ID: ")
roles["bot"] = bot
default = input("Default role ID: ")
roles["default"] = default
with open("data/roles.json","w") as f:
    json.dump(roles, f, indent=2, sort_keys=True)

print("\nSetup complete! Welcome to Amadeus!~")
print("All changes have been saved. Feel free to either close this window or wait for it to close automatically~")
time.sleep(10)
