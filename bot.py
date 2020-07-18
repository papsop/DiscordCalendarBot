import config

import discord
from BotClass import Bot
from commands.Help import Help
from commands.GetStarted import GetStarted
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
bot._commandsManager.register_command( Help )
bot._commandsManager.register_command( Setup )
bot._commandsManager.register_command( Calendar )
bot._commandsManager.register_command( GetStarted )
print("=================================")

# ==================
#   Discord events
# ==================
@bot._client.event
async def on_ready():
    print("Bot user: {0.user}".format(bot._client))
    bot._client.loop.create_task(bot.periodic_update_calendars())
    bot._client.loop.create_task(bot.periodic_clean_db())
    print("=================================")

@bot._client.event
async def on_message(message):
    if message.author != bot._client.user:
        await bot._commandsManager.process_message(message)

# run the discord client
bot.run_client(config.bot['token'])