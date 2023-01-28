from uuid import UUID

from pydantic import BaseModel


class SubscribedPlayers(BaseModel):
    AYUDESEE: UUID = UUID("ad42c90b-45a9-49b6-8ab0-9c8662330543")
    NAPAD: UUID = UUID("278790a2-1f08-4350-bd96-427f7dcc8722")
    MORZY: UUID = UUID("18e2a663-9e20-4db9-8b29-3c3cbdff30ac")
    HAWK: UUID = UUID("8cbb0b36-4c6b-4ebd-a92b-829234016626")
    DELPIX: UUID = UUID("e1cddcbb-afdc-4e8e-abf2-eea5638f0363")
    SPARTACUS: UUID = UUID("9da3572e-1960-4ba0-bd3c-d38ef34c1f1c")
    DG: UUID = UUID("b8e5cd07-1b43-4203-9173-465fddcd391f")
    QZAC: UUID = UUID("4e7d1f6c-9045-4800-8eda-23c892dcd814")
    DANTIST: UUID = UUID("24785d80-7265-4f50-970e-1c02666ede56")

    def __contains__(self, item: str | UUID):
        if isinstance(item, str):
            item = UUID(hex=item)
        return item in self.__dict__.values()


class ColorTuple(BaseModel):
    WHITE: tuple[int, int, int, int] = (255, 255, 255, 255)
    GREEN: tuple[int, int, int, int] = (0, 190, 0, 255)
    ORANGE: tuple[int, int, int, int] = (255, 165, 0, 255)
    RED: tuple[int, int, int, int] = (170, 0, 0, 255)


class AvailableMaps(BaseModel):
    ANCIENT: str = "de_ancient"
    DUST_2: str = "de_dust2"
    INFERNO: str = "de_inferno"
    MIRAGE: str = "de_mirage"
    NUKE: str = "de_nuke"
    OVERPASS: str = "de_overpass"
    TRAIN: str = "de_train"
    VERTIGO: str = "de_vertigo"
    ANUBIS: str = "de_anubis"

    def __contains__(self, item: str):
        return item in self.__dict__.values()


subscribers = SubscribedPlayers()
colors = ColorTuple()
available_maps = AvailableMaps()
