import time

class CommandsManager:
    _bot = None
    _cacheManager = None
    _static_commands = []
    _commands = []
    _defaultPrefix = '!'

    def __init__(self, bot):
        self._bot = bot
        self._cacheManager = bot._cacheManager
        print("✓ CommandsManager initialized")

    def register_command(self, commandClass):
        command = commandClass(self)
        self._commands.append(command)
        print("  ✓ {0.activation_string} [{0.sub_commands}]".format(command))

    def register_static_command(self, commandClass):
        command = commandClass(self)
        self._static_commands.append(command)
        print("  ✓ {0.activation_string} [{0.sub_commands}]".format(command))

    async def process_message(self, message):
        # ignore direct messages
        if message.guild == None:
            return

        # check commands with custom prefix
        server_data = self._cacheManager.get_server_cache(message.guild.id)
        if server_data != None:
            prefix = server_data["prefix"]
        else:
            prefix = self._defaultPrefix 

        # check static commands
        if message.content.startswith(self._defaultPrefix):
            for command in self._static_commands:
                if message.content[len(self._defaultPrefix):].startswith(command.activation_string):
                    start_time = time.time()
                    result = await command.action(message, prefix)
                    if "embed" in result:
                        result["embed"]["execution_time"] = (time.time() - start_time)
                        await self._bot.send_embed(message.channel, result["embed"])
                    else:
                        await self._bot.send_message(message.channel, result)
                        print("Command took {0}".format(str(time.time() - start_time)))
                    break

        # ignore messages without the prefix
        if message.content[:len(prefix)] != prefix:
            return
        
        for command in self._commands:
            if message.content[len(prefix):].startswith(command.activation_string):
                start_time = time.time()
                result = await command.action(message, prefix)
                if "embed" in result: # maybe later we want to pass more information so keep embed_data in ["embed"]
                    result["embed"]["execution_time"] = (time.time() - start_time)
                    await self._bot.send_embed(message.channel, result["embed"])
                else:
                    await self._bot.send_message(message.channel, result)
                    print("Command took {0}".format(str(time.time() - start_time)))
                break