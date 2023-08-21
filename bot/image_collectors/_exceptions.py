class NothingException(Exception):
    pass


class BadAPICallException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
