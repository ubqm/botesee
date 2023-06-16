import aiohttp
from bot import conf
from bot.clients.faceit import FaceitClient
from bot.clients.models.faceit.match_stats import MatchStatistics
from bot.db.repositories.elo import EloRepository
from bot.db.repositories.match import MatchRepository
from bot.web.models.events import MatchFinished

from bot.db import Session
from bot.db.repositories.player import PlayerRepository

match_repo = MatchRepository()
elo_repo = EloRepository()
player_repo = PlayerRepository()


async def db_match_finished(match: MatchFinished, statistics: MatchStatistics):
    with Session().begin() as sa_session:
        for match_stat in statistics.rounds:
            for team in match_stat.teams:
                for player in team.players:
                    async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
                        player_details = await FaceitClient.player_details_by_id(session, player.player_id)
                    p1 = player_repo.get_or_create(sa_session, player.player_id)
                    m1 = match_repo.get_or_create(sa_session, match_stat.match_id, date=match.timestamp)
                    elo_repo.create(sa_session, player=p1, match=m1, elo=player_details.games.csgo.faceit_elo)
                    sa_session.session.add(p1)
