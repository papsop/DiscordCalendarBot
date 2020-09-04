import config
import logging
import discord
import asyncio
from BotClass import Bot
from commands.Help import Help
from commands.GetStarted import GetStarted
from commands.Setup import Setup
from commands.Calendar import Calendar
from commands.ServerInfo import ServerInfo

logging.basicConfig(level=logging.INFO)

# Create instance of the bot
print("=================================")
print("Initializing Bot and Managers...")
bot = Bot()
print("=================================")

# =====================
#   Register commands
# =====================
print("Successfully registered commands:")
bot._commandsManager.register_static_command( Setup )
bot._commandsManager.register_static_command( ServerInfo )
bot._commandsManager.register_command( Help )
bot._commandsManager.register_command( GetStarted )
bot._commandsManager.register_command( Calendar )
print("=================================")

# ==================
#   Discord events
# ==================
@bot._client.event
async def on_ready():
    print("Bot user: {0.user}".format(bot._client))
    # start periodic check loop
    # https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html
    bot.periodic_update_calendars.start()
    bot.periodic_clean_db.start()
    # update bot's game status
    game = discord.Game("calbot.patrikpapso.com")
    await bot._client.change_presence(status=discord.Status.online, activity=game)
    print("=================================")

@bot._client.event
async def on_resumed():
    print("Bot user: {0.user} RESUMED".format(bot._client))
    # start periodic check loop
    # https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html
    bot.periodic_update_calendars.start()
    bot.periodic_clean_db.start()
    # update bot's game status
    game = discord.Game("calbot.patrikpapso.com")
    await bot._client.change_presence(status=discord.Status.online, activity=game)
    print("==========RESUMED==========")

@bot._client.event
async def on_message(message):
    if message.author != bot._client.user:
        await bot._commandsManager.process_message(message)

# run the discord client
bot.run_client(config.bot['token'])