import aiohttp
import asyncio
import logging

from typing import Union
from models.opensea import FloorPrice
from discord.ext import commands, tasks
from discord import Activity, ActivityType


log = logging.getLogger(__name__)


async def get_opensea_floor_price(url: str, alias: str) -> Union[FloorPrice, bool]:

    """Queries the API endpoint of an NFT collection on OpenSea and parses the response to retrieve the floor price.

    .. note:
        API endpoint of a collection, e.g. https://api.opensea.io/collection/boredapeyachtclub
    .. todo:
        Check the base currency of the floor price returned is always in ETH.

    :param url: str
        URL of the collection to call.
    :param alias: str
        Name of the collection, i.e. BAYC.
    :returns:
        NFTPrice object if successful, otherwise False.
    """

    source = "OpenSea"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.json(content_type=None)
                if content:
                    price = content['collection']['stats']['floor_price']
                    return FloorPrice(source=source, price=f"{price} ETH", project=alias)
    except Exception as error:
        log.error(f"[ENDPOINT] [{source}] API response was invalid {error}.")
    log.error(f"[ENDPOINT] [{source}] API request did not return the expected response: {content}.")
    return False


class NFT(commands.Cog):

    """Discord satellite that displays OpenSea NFT floor prices as a user in Discord servers.
     ___________________________________
    |                                  |
    |  35.5 ETH                        |
    |  Watching BAYC floor price on .. |
    |__________________________________|
    """

    def __init__(self,
                 bot: commands.Bot,
                 alias: str,
                 url: str):

        self.bot = bot
        self.bot_type = self.__class__.__name__

        self.alias = alias
        self.url = url

        self.price = ""
        self.status = ""
        self.member_of_guilds = None

        self.updater.start()

    async def update_interface_elements(self, guild_id: int) -> None:

        """Updates the nickname for this bot within a given discord server (guild_id).

        :param guild_id:
            `guild_id` to perform update.
        """

        guild = self.bot.get_guild(guild_id)
        bot_instance = guild.me

        await bot_instance.edit(nick=self.price)

        log.info(f"[UPDATE] [{self.bot_type}] - [{guild}] - [{self.alias}] Nickname: {self.price} Activity: {self.status}")

    async def update_nft_floor_price(self) -> bool:

        """Fetches latest NFT price from sources to update the price and status attributes.

        :returns: bool
            True if successful else False
        """

        nft_floor_price = await get_opensea_floor_price(url=self.url, alias=self.alias)

        if nft_floor_price:
            self.price = f"{nft_floor_price.price}"
            self.status = f"{nft_floor_price.project} floor price on {nft_floor_price.source}"

            return True
        return False

    @tasks.loop(minutes=1)
    async def updater(self):

        """Task to fetch new data and update the bots nickname and activity in Discord.

        .. note:

            Discord nicknames and roles are local to the server, whereas an activity is universal across all servers.

            `nickname` is updated by creating an self.update_interface_elements(guild_id) task for all servers this bot
                is a member of.
                UI: '35.5 ETH'
            `activity` is updated with self.bot.change_presence()
                UI: 'Watching BAYC floor price on OpenSea'
        """

        self.member_of_guilds = [guild.id for guild in self.bot.guilds]
        valid_response = await self.update_nft_floor_price()

        if valid_response:
            await self.bot.change_presence(activity=Activity(type=ActivityType.watching, name=self.status))
            update_jobs = [self.update_interface_elements(guild_id) for guild_id in self.member_of_guilds]
            await asyncio.gather(*update_jobs)

    @updater.before_loop
    async def before_update(self):

        """Ensure this bot is initialized before updating it's nickname or status."""

        await self.bot.wait_until_ready()
        self.member_of_guilds = [guild.id for guild in self.bot.guilds]

        log.info(f"[INIT] [{self.bot_type}] - [{self.alias}] Bot started successfully, active on {len(self.member_of_guilds)} servers.")

    def __str__(self):
        return f"Discord NFT satellite for {self.alias}"

    def __repr__(self):
        return f"<Discord NFT satellite for {self.alias}>"
