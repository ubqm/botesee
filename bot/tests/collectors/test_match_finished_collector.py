import aiohttp
import pytest

from bot import conf
from bot.clients.faceit import FaceitClient
from bot.discord_bot.models.embed import NickEloStorage, PlayerStorage
from image_collectors import MatchFinishedImCol
from bot.web.models.events import MatchFinished


@pytest.mark.asyncio
async def test_initialization(match_finished: MatchFinished):
    print(f"{match_finished = }")
    async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
        statistics = await FaceitClient.match_stats(session, match_finished.payload.id)
    mf_imcol = MatchFinishedImCol(
        match_finished, statistics, NickEloStorage(players=[PlayerStorage(nickname="Test", elo=1)])
    )
    print(mf_imcol)
