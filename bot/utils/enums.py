from typing import Generator
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
    FIERCE: UUID = UUID("7f519c1e-64cd-43d0-83df-59c882c705d9")
    PUTJJE: UUID = UUID("87dcb2d9-e667-49fc-9282-6826751bea3c")
    KIND: UUID = UUID("d1a0fba9-7352-476c-be03-a7babd155f0e")
    GORKIT: UUID = UUID("bb9472c5-4c0b-4f91-b6ff-4101d210bdbd")
    MELKIY_WAY: UUID = UUID("beac63ad-e635-44ac-8be1-3a44767036e2")
    H8VTK: UUID = UUID("8336f93d-92d3-47d5-86b7-cc8ece2fff4b")
    VAAKC: UUID = UUID("05e08f8f-bee6-4bf4-8385-b290dd29d099")
    ECO_COBRA: UUID = UUID("d0b7218c-a540-423f-960e-f6e9a8b3b10a")
    G3R: UUID = UUID("e825ff16-b955-4fb8-8b11-c85f11136eca")
    XMES: UUID = UUID("92ae3dc2-cf69-4636-aa66-a2fc595dd44f")
    DETSKI_LEPIT: UUID = UUID("ca5af68f-024c-40b1-a0dc-df8f8c50984d")

    def __contains__(self, item: str | UUID) -> bool:
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
    VERTIGO: str = "de_vertigo"
    ANUBIS: str = "de_anubis"

    def __contains__(self, item: str) -> bool:
        return item in self.__dict__.values()

    def __iter__(self) -> Generator[str, None, None]:
        """Iterate over actual values of instance ('de_ancient', 'de_dust2', ...)"""
        return (it[1] for it in super().__iter__())


subscribers = SubscribedPlayers()
colors = ColorTuple()
available_maps = AvailableMaps()
