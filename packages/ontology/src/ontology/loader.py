from dataclasses import dataclass, field
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from ontology.models import BatTrachRelation, CungMenh, Huong, NguHanh


@dataclass
class Ontology:
    ngu_hanh: dict[str, NguHanh] = field(default_factory=dict)
    huong: dict[str, Huong] = field(default_factory=dict)
    cung_menh: dict[str, CungMenh] = field(default_factory=dict)
    bat_trach: list[BatTrachRelation] = field(default_factory=list)


def _read_yaml(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected list at root of {path}, got {type(data).__name__}")
    return data


def _data_dir() -> Path:
    return Path(str(files("ontology").joinpath("data")))


@lru_cache(maxsize=1)
def load_ontology(data_dir: Path | None = None) -> Ontology:
    """Load and validate all ontology YAML files. Cached — call freely.

    Pass an explicit `data_dir` to load alternate (e.g. test) data.
    """
    base = data_dir or _data_dir()

    ngu_hanh = [NguHanh(**x) for x in _read_yaml(base / "ngu_hanh.yaml")]
    huong = [Huong(**x) for x in _read_yaml(base / "huong.yaml")]
    cung_menh = [CungMenh(**x) for x in _read_yaml(base / "cung_menh.yaml")]
    bat_trach = [BatTrachRelation(**x) for x in _read_yaml(base / "bat_trach.yaml")]

    return Ontology(
        ngu_hanh={x.key: x for x in ngu_hanh},
        huong={x.key: x for x in huong},
        cung_menh={x.key: x for x in cung_menh},
        bat_trach=bat_trach,
    )
