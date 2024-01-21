import discord
from loguru import logger

from src import EnvType
from src.discord_bot.client import DiscordClient, discord_client


class MockedDiscordClient(DiscordClient):
    def __init__(self):
        super().__init__(faceit_channel_id=1, intents=discord.Intents.all())
        self.faceit_channel = True

    async def on_ready(self, *args, **kwargs):
        logger.info("on_ready Mocked Discord Client")

    @staticmethod
    def compile_binary_image(*args, **kwargs):
        logger.info("compile_binary_image Mocked Discord Client")

    @staticmethod
    def is_contains_media(*args, **kwargs):
        logger.info("is_contains_media Mocked Discord Client")

    @staticmethod
    def is_stats_request(*args, **kwargs):
        logger.info("is_stats_request Mocked Discord Client")

    @staticmethod
    def is_compare_request(*args, **kwargs):
        logger.info("is_compare_request Mocked Discord Client")

    async def on_message(self, *args, **kwargs):
        logger.info("on_message Mocked Discord Client")

    async def on_raw_reaction_add(self, *args, **kwargs):
        logger.info("on_raw_reaction_add Mocked Discord Client")

    async def on_raw_reaction_remove(self, *args, **kwargs):
        logger.info("on_raw_reaction_remove Mocked Discord Client")

    async def _handle_reaction_event(self, *args, **kwargs):
        logger.info("_handle_reaction_event Mocked Discord Client")

    async def post_faceit_message_ready(self, *args, **kwargs):
        logger.info("post_faceit_message_ready Mocked Discord Client")

    async def post_faceit_message_finished(self, *args, **kwargs):
        logger.info("post_faceit_message_finished Mocked Discord Client")

    async def post_faceit_message_aborted(self, *args, **kwargs):
        logger.info("post_faceit_message_aborted Mocked Discord Client")

    async def delete_message_by_faceit_match_id(self, *args, **kwargs):
        logger.info("delete_message_by_faceit_match_id Mocked Discord Client")

    async def update_score_for_match(self, *args, **kwargs):
        logger.info("update_score_for_match Mocked Discord Client")


def discord_factory(env: EnvType) -> DiscordClient:
    match env:
        case EnvType.PROD:
            return discord_client
        case EnvType.DEV:
            return MockedDiscordClient()
        case _:
            return MockedDiscordClient()
