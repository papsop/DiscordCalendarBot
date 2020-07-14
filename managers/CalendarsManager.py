import discord
from datetime import datetime, timedelta
from managers.helpers.embeds import Embeds

class CalendarsManager:
    _bot = None
    _teamupManager = None
    _databaseManager = None

    def __init__(self, bot):
        self._bot = bot
        self._teamupManager = self._bot._teamupManager
        self._databaseManager = self._bot._databaseManager
        print("✓ CalendarsManager initialized")
    
    def create_calendar_embed(self, calendar_data):
        embed = discord.Embed()
        # default settings
        embed.color = Embeds.color_info
        embed.set_footer(text="nice")
        embed.timestamp = datetime.now()
        embed.title = "\_" * 20 + "CALENDAR ID {0}".format(calendar_data["ID"]) + "\_" * 20
        # content
        embed.add_field(name="Monday XX-XX", value="```ini\n[nice]\n20:00 - 22:00 - something```", inline=False)
        embed.add_field(name="Monday XX-XX", value="```ini\n[nice] ```", inline=False)
        embed.add_field(name="Monday XX-XX", value="```ini\n[nice] ```", inline=False)
        embed.add_field(name="Monday XX-XX", value="```ini\n[nice] ```", inline=False)
        embed.add_field(name="Monday XX-XX", value="```ini\n[nice] ```", inline=False)
        embed.add_field(name="Monday XX-XX", value="```ini\n[nice] ```", inline=False)
        embed.add_field(name="Monday XX-XX", value="```ini\n[nice] ```", inline=False)
        return embed

    async def update_calendar_embed(self, server_id, calendar_id):
        calendar = None
        try:
            calendar = self._databaseManager.get_calendar(server_id, calendar_id)
        except Exception as e:
            raise e
        
        if calendar == None:
            raise Exception("Calendar with this combination of server_id and calendar_id doesn't exist.")
        
        #
        # TODO: Check everything, if missing - delete from DB
        #
        guild = self._bot._client.get_guild(calendar["server_id"])
        channel = guild.get_channel(calendar["channel_id"])
        message = await channel.fetch_message(calendar["message_id"])
        
        calendar_embed = self.create_calendar_embed({"ID": calendar["ID"]})

        await message.edit(content="...", embed=calendar_embed)