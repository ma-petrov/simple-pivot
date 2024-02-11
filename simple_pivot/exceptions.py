class BaseError(Exception):
    message: str

    def __init__(self, *args):
        super().__init__(" ".join([self.message, *args]))


class AggColError(BaseError):
    message = (
        "agg_col is expected to be column name (with type str) "
        "or computable expression (with type Callable)."
    )


class IncorrectExpressionFormatError(BaseError):
    message = "agg_col must be column name or expression."


class ValueTypeError(BaseError):
    message = "agg_col must be str."


class WrongConfigKeysError(BaseError):
    message = "В конфигурацию сводной таблицы нельзя передать указанные ключи."


class MissingConfigKeyError(BaseError):
    message = "Отсутствует обязательный ключ конфигурации."
