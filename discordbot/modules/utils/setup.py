from json import dump


class Setup:

    def settings():
        settings = {}
        token = input("Bot token: ")
        desc = input("Bot description: ")
        prefix = input("Bot prefix: ")

        settings["token"] = token
        settings["description"] = desc
        settings["prefix"] = prefix
        with open("data/settings.json", "w") as config:
            dump(settings, config, indent=2, sort_keys=True)

        return settings

    def channels():
        channels = {}
        logs = input("Log channel ID: ")
        botcmds = input("Bot commands channel ID: ")
        welcome = input("Welcome channel ID: ")

        channels["logs"] = logs
        channels["bot-commands"] = botcmds
        channels["welcome"] = welcome
        with open("data/channels.json", "w") as config:
            dump(channels, config, indent=2, sort_keys=True)

        return channels

    def roles():
        roles = {}
        admin = input("Admin role ID: ")
        mod = input("Moderator role ID: ")
        bot = input("Bot role ID: ")
        default = input("Default role ID: ")

        roles["admin"] = admin
        roles["mod"] = mod
        roles["bot"] = bot
        roles["default"] = default
        with open("data/roles.json", "w") as config:
            dump(roles, config, indent=2, sort_keys=True)

        return roles
