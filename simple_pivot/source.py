from pandas import DataFrame


class BaseSource:
    def load(self) -> DataFrame:
        raise NotImplementedError()


class DBSource(BaseSource):
    def __init__(self):
        """TODO"""

    def load(self) -> DataFrame:
        """TODO"""