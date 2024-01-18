from bot.clients.faceit import faceit_client
from bot.clients.models.faceit.match_stats import MatchStatistics
from bot.db import Session
from bot.db.repositories.elo import elo_repo
from bot.db.repositories.gambling import gambling_repo
from bot.db.repositories.match import match_repo
from bot.db.repositories.player import player_repo
from bot.web.models.events import MatchFinished


async def db_match_finished(match: MatchFinished, statistics: MatchStatistics) -> None:
    async with Session() as sa_session:
        for match_stat in statistics.rounds:
            for team in match_stat.teams:
                for player in team.players:
                    player_details = await faceit_client.player_details_by_id(player_id=player.player_id)
                    db_player = await player_repo.get_or_create(session=sa_session, player_uuid=player.player_id)
                    db_match = await match_repo.get_or_create(
                        session=sa_session,
                        match_uuid=match_stat.match_id,
                        date=match.timestamp,
                        game=match.payload.game,
                    )
                    await elo_repo.create(
                        session=sa_session,
                        player=db_player,
                        match=db_match,
                        elo=getattr(player_details.games, f"{match.payload.game}").faceit_elo,
                    )
        await gambling_repo.make_payout(session=sa_session, match=match, statistics=statistics)
        await sa_session.commit()
