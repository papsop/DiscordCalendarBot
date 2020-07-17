import config

import discord
from BotClass import Bot
from commands.Ping import Ping
from commands.Setup import Setup
from commands.Calendar import Calendar

# Create instance of the bot
print("=================================")
print("Initializing Bot and Managers...")
bot = Bot()
print("=================================")

# =====================
#   Register commands
# =====================
print("Successfully registered commands:")
bot._commandsManager.register_command( Ping )
bot._commandsManager.register_command( Setup )
bot._commandsManager.register_command( Calendar )
print("=================================")

# ==================
#   Discord events
# ==================
@bot._client.event
async def on_ready():
    print("Bot user: {0.user}".format(bot._client))
    bot._client.loop.create_task(bot.periodic_update_calendars())
    print("=================================")

@bot._client.event
async def on_message(message):
    if message.author != bot._client.user:
        await bot._commandsManager.process_message(message)

# run the discord client
bot.run_client(config.bot['token'])