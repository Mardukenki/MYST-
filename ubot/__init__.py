import sys
from logging import INFO, basicConfig, getLogger
from time import time

import telethon
from telethon.errors.rpcerrorlist import (AccessTokenExpiredError,
                                          AccessTokenInvalidError,
                                          TokenInvalidError)
from telethon.network.connection.tcpabridged import \
    ConnectionTcpAbridged as CTA

from .custom import ExtendedEvent
from .loader import Loader
from .settings import Settings

if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
    print("This program requires at least Python 3.6.0 to work correctly, exiting.")
    sys.exit(1)

startup_time = time()


class MicroBot():
    client = None
    settings = Settings()
    logger = None
    loader = None

    def __init__(self):
        self.start_logger()
        self.start_client()
        self.start_loader()

    def run_until_done(self):
        self.loader.load_all_modules()
        self.logger.info("Client successfully started.")
        self.client.run_until_disconnected()
        self.client.loop.run_until_complete(self.loader.aioclient.close())

    def start_loader(self):
        self.loader = Loader(self.client, self.logger, self.settings)

    def start_logger(self):
        basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO)
        self.logger = getLogger(__name__)

    def start_client(self):
        api_key = self.settings.get_config("api_key")
        api_hash = self.settings.get_config("api_hash")
        bot_token = self.settings.get_config("bot_token")

        self.client = telethon.TelegramClient('Bot', api_key, api_hash, connection=CTA)

        try:
            self.client.start(bot_token=bot_token)
        except (TokenInvalidError, AccessTokenExpiredError, AccessTokenInvalidError):
            self.logger.error("The bot token provided is invalid, exiting.")
            sys.exit(2)

    async def stop_client(self, reason=None):
        if reason:
            self.logger.info("Stopping client for reason: %s", reason)
        else:
            self.logger.info("Stopping client.")

        await self.loader.aioclient.close()
        await self.client.disconnect()


telethon.events.NewMessage.Event = ExtendedEvent

micro_bot = MicroBot()
ldr = micro_bot.loader
client = micro_bot.client
logger = micro_bot.logger

try:
    micro_bot.run_until_done()
except:
    micro_bot.client.loop.run_until_complete(micro_bot.stop_client())
