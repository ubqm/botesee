from enum import Enum, StrEnum
from uuid import UUID


class SubscribedPlayer(Enum):
    UBQM = UUID("ad42c90b-45a9-49b6-8ab0-9c8662330543")
    NAPAD = UUID("278790a2-1f08-4350-bd96-427f7dcc8722")
    MORZY = UUID("18e2a663-9e20-4db9-8b29-3c3cbdff30ac")
    HAWK = UUID("8cbb0b36-4c6b-4ebd-a92b-829234016626")
    DELPIX = UUID("e1cddcbb-afdc-4e8e-abf2-eea5638f0363")
    SPARTACUS = UUID("9da3572e-1960-4ba0-bd3c-d38ef34c1f1c")
    DG = UUID("b8e5cd07-1b43-4203-9173-465fddcd391f")
    QZAC = UUID("4e7d1f6c-9045-4800-8eda-23c892dcd814")
    DANTIST = UUID("24785d80-7265-4f50-970e-1c02666ede56")
    FIERCE = UUID("7f519c1e-64cd-43d0-83df-59c882c705d9")
    PUTJJE = UUID("87dcb2d9-e667-49fc-9282-6826751bea3c")
    KIND = UUID("d1a0fba9-7352-476c-be03-a7babd155f0e")
    GORKIT = UUID("bb9472c5-4c0b-4f91-b6ff-4101d210bdbd")
    MELKIY_WAY = UUID("beac63ad-e635-44ac-8be1-3a44767036e2")
    H8VTK = UUID("8336f93d-92d3-47d5-86b7-cc8ece2fff4b")
    VAAKC = UUID("05e08f8f-bee6-4bf4-8385-b290dd29d099")
    ECO_COBRA = UUID("d0b7218c-a540-423f-960e-f6e9a8b3b10a")
    G3R = UUID("e825ff16-b955-4fb8-8b11-c85f11136eca")
    XMES = UUID("92ae3dc2-cf69-4636-aa66-a2fc595dd44f")
    DETSKI_LEPIT = UUID("ca5af68f-024c-40b1-a0dc-df8f8c50984d")
    VIKTOROVICH = UUID("195921be-11f6-4037-84d0-2899d01e8d7a")
    TIA = UUID("47872fc7-5f59-49dd-a24a-440f1914a517")
    LFS = UUID("602d617c-3ed2-4559-af0a-b326f36e6fde")
    FR1ZE = UUID("34d03f62-4978-4838-bcf5-d3b53c56ccda")


class ColorTuple(tuple, Enum):
    WHITE = (255, 255, 255, 255)
    GREEN = (0, 190, 0, 255)
    ORANGE = (255, 165, 0, 255)
    RED = (170, 0, 0, 255)


class ColorEvaluation(tuple, Enum):
    P_1_MUCH_BETTER = ColorTuple.GREEN, ColorTuple.RED
    P_1_BETTER = ColorTuple.GREEN, ColorTuple.WHITE
    EQUAL = ColorTuple.WHITE, ColorTuple.WHITE
    P_2_BETTER = ColorTuple.WHITE, ColorTuple.GREEN
    P_2_MUCH_BETTER = ColorTuple.RED, ColorTuple.GREEN


class AvailableMaps(StrEnum):
    ANCIENT = "de_ancient"
    DUST_2 = "de_dust2"
    INFERNO = "de_inferno"
    MIRAGE = "de_mirage"
    NUKE = "de_nuke"
    OVERPASS = "de_overpass"
    ANUBIS = "de_anubis"
    TRAIN = "de_train"
    VERTIGO = "de_vertigo"
