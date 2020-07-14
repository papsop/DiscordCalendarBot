import discord
import time
class CommandBase:
    activation_string = None
    help_embed = None
    commands_list_string = None
    sub_commands = None
    
    def __init__(self):
        pass

    async def action(self):
        raise NotImplementedError