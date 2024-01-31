class BaseError(Exception):
    message: str

    def __init__(self):
        super().__init__(self.message)


class AggColError(BaseError):
    message = (
        "agg_col is expected to be column name (with type str) "
        "or computable expression (with type Callable)."
    )


class IncorrectExpressionFormatError(BaseError):
    message = "agg_col must be column name or expression"


class ValueTypeError(BaseError):
    message = "agg_col must be str"
