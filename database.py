import aiohttp
from tortoise import Tortoise

from bot import conf
from bot.clients.faceit import FaceitClient
from bot.clients.models.faceit.match_stats import MatchStatistics
from bot.db.models_tortoise import Elo, Match, Player
from bot.web.models.events import MatchFinished


async def db_fetch_data(pl_items: int = 50, mc_items: int = 50, elo_items: int = 50):
    players_data = await Player.all().limit(pl_items).values_list()
    matches_data = await Match.all().limit(mc_items).values_list()
    elo_data = await Elo.all().limit(elo_items).values_list()
    await Tortoise.close_connections()
    return players_data, matches_data, elo_data


async def db_match_finished(match: MatchFinished, statistics: MatchStatistics):
    print("started tortoise match finished save")
    async with aiohttp.ClientSession(headers=conf.FACEIT_HEADERS) as session:
        for match_round in statistics.rounds:
            await Match.get_or_create(id=match_round.match_id, date=match.timestamp)
            for team in match_round.teams:
                for player in team.players:
                    await Player.get_or_create(id=player.player_id)
                    player_details = await FaceitClient.player_details_by_id(session, player.player_id)
                    await Elo.create(
                        match_id=match_round.match_id,
                        player_id=player.player_id,
                        elo=player_details.games.csgo.faceit_elo,
                    )
    await Tortoise.close_connections()
