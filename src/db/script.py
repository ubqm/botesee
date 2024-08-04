from src.clients.faceit import faceit_client
from src.clients.models.faceit.match_stats import MatchStatistics
from src.db import session_maker
from src.db.repositories.elo import elo_repo
from src.db.repositories.gambling import gambling_repo
from src.db.repositories.match import match_repo
from src.db.repositories.player import player_repo
from src.web.models.events import MatchFinished


async def db_match_finished(match: MatchFinished, statistics: MatchStatistics) -> None:
    async with session_maker() as sa_session:
        for match_stat in statistics.rounds:
            for team in match_stat.teams:
                for player in team.players:
                    player_details = await faceit_client.player_details_by_id(
                        player_id=player.player_id
                    )
                    db_player = await player_repo.get_or_create(
                        session=sa_session, player_uuid=player.player_id
                    )
                    db_match = await match_repo.get_or_create(
                        session=sa_session,
                        match_uuid=match_stat.match_id,
                        stats=statistics,
                        date=match.timestamp,
                        game=match.payload.game,
                    )
                    await elo_repo.create(
                        session=sa_session,
                        player=db_player,
                        match=db_match,
                        elo=getattr(
                            player_details.games, f"{match.payload.game}"
                        ).faceit_elo,
                    )
        await gambling_repo.make_payout(
            session=sa_session, match=match, statistics=statistics
        )
        await sa_session.commit()
