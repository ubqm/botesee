from pydantic import BaseModel


class NickEloStorage(BaseModel):
    nicknames: str
    elos: str
