
class CommandsManager:
    _bot = None
    _cacheManager = None
    _commands = []
    _prefix = '!'

    def __init__(self, bot):
        self._bot = bot
        self._cacheManager = bot._cacheManager
        print("✓ CommandsManager initialized")

    def register_command(self, commandClass):
        command = commandClass(self)
        self._commands.append(command)
        print("  ✓ {0.activation_string}".format(command))

    async def process_message(self, message):
        # ignore messages without the prefix
        server_data = self._cacheManager.get_server_cache(message.guild.id)
        if server_data != None:
            prefix = server_data["prefix"]
        else:
            prefix = "!"

        if message.content[:len(prefix)] != prefix:
            return
        
        for command in self._commands:
            if message.content[len(prefix):].startswith(command.activation_string):
                # TODO: Check for user permissions
                result = await command.action(message)
                if "embed" in result: # maybe later we want to pass more information so keep embed_data in ["embed"]
                     await self._bot.send_embed(message.channel, result["embed"])
                else:
                    await self._bot.send_message(message.channel, result)
                break

#    def list_commands(self, server_id):
#        for command in self._commands:
#            prefix = self._cacheManager.get_prefix_by_server_id(server_id)
#            print(prefix + command.activation_string)