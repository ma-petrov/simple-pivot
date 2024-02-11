from pydantic import ValidationError
from pytest import mark, raises

from simple_pivot.config import Config
from simple_pivot.exceptions import MissingConfigKeyError


@mark.parametrize(
    "config_dict",
    [
        {"totals": 3, "css": 4},
        {"vals": {"val": "v"}, "rows": "a", "totals": 3, "css": 4},
        {"vals": {"val": "v"}, "rows": "a", "cols": "b", "totals": 3},
        {},
        {"rows": "a"},
        {"rows": "a", "cols": "b"},
    ],
)
def test_config__validation_error(config_dict):
    with raises(ValidationError):
        Config(**config_dict)


def test_config__key_errors():
    config_dict = {"vals": {"val": "v"}}

    with raises(MissingConfigKeyError) as e:
        Config(**config_dict)

    assert str(e.value) == (
        "Отсутствует обязательный ключ конфигурации. Нужно передать хотя бы "
        "один из параметров rows, cols."
    )


def test_config__happy_pass():
    def avg_price(price, count):
        return price / count

    def round_3(x):
        return round(x / 3)

    config_dict = {
        "vals": [
            "count",
            avg_price,
            {"val": "price"},
            {
                "val": avg_price,
                "agg_func": "mean",
                "name": "Average price of item",
                "formatting": round_3,
            },
        ],
        "rows": ["year", "month"],
        "cols": "Product category",
    }

    config = Config(**config_dict)
    val_count, val_exp, val_price, val_named_exp = tuple(config.vals)

    assert val_count.val == "count"
    assert val_count.agg_func == "sum"
    assert val_count.name == "sum of count"

    assert val_exp.val == avg_price
    assert val_exp.agg_func == "sum"
    assert val_exp.name == "avg_price"

    assert val_price.val == "price"
    assert val_price.agg_func == "sum"
    assert val_price.name == "sum of price"

    assert val_named_exp.val == avg_price
    assert val_named_exp.agg_func == "mean"
    assert val_named_exp.name == "Average price of item"
    assert val_named_exp.formatting == round_3

    assert config.rows == ["year", "month"]
    assert config.cols == ["Product category"]
