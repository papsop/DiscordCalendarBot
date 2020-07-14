import discord
from .CommandBase import CommandBase

class Ping(CommandBase):

    _commandsManager = None

    def __init__(self, commandsManager):
        self._commandsManager = commandsManager
        self.activation_string = "ping"
        self.sub_commands = "ping"
    
    async def action(self, message):
        return "pong!"