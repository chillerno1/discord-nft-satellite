import uuid
import logging
import argparse

from discord.ext import commands
from utils.logging import setup_logging

from cogs.satellites import NFT

log = logging.getLogger(__name__)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Bot to display the NFT floor price of a collection on OpenSea.")
    parser.add_argument('--discord-token',
                        '-t',
                        type=str,
                        required=True,
                        help="The token for this Discord bot.")
    parser.add_argument('--alias',
                        '-a',
                        type=str,
                        required=True,
                        help="Alias for collection to display in the Discord activity (i.e. BAYC).")
    parser.add_argument('--url',
                        '-u',
                        type=str,
                        required=True,
                        help="OpenSea API URL of any NFT asset that belongs to the desired collection.")

    args = parser.parse_args()

    satellite = commands.Bot(command_prefix=str(uuid.uuid4()))
    satellite.add_cog(NFT(bot=satellite, alias=args.alias, url=args.url))

    with setup_logging():
        satellite.run(args.discord_token)
