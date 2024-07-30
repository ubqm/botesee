from pydantic import BaseModel

from src.clients.models.faceit.match_details import MatchDetails
from src.web.models.events import MatchReady


class DetailsMatchDict(BaseModel):
    match_details: MatchDetails
    match_ready: MatchReady
