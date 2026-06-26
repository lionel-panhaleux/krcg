"""JSON utilities."""

from typing import (
    Any,
)
import dataclasses
import enum
import functools
import datetime

from .fuzzy_dict import FuzzyDict


@functools.singledispatch
def jsonize(x: Any) -> Any:
    """Prepare a value for JSON encoding."""
    if dataclasses.is_dataclass(x):
        return jsonize(dataclasses.asdict(x))
    return x


@jsonize.register(dict)
def _encode_dict(x: dict) -> dict:
    ret = {k: jsonize(v) for k, v in x.items()}
    return {k: v for k, v in ret.items() if v}


@jsonize.register(FuzzyDict)
def _encode_fuzzy_dict(x: FuzzyDict) -> dict:
    ret = {k: jsonize(v) for k, v in x.items()}
    return {k: v for k, v in ret.items() if v}


@jsonize.register(list)
def _encode_list(x: list) -> list:
    ret = [jsonize(v) for v in x]
    return [v for v in ret if v]


@jsonize.register(enum.Enum)
def _encode_list(x: enum.Enum) -> str:
    return x.value


@jsonize.register(datetime.datetime)
@jsonize.register(datetime.date)
def _encode_datetime(x: datetime.date | datetime.datetime) -> str:
    return x.isoformat()
