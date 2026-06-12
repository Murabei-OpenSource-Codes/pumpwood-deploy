"""Module to define Pumpwood deploy associated types."""
from dataclasses import dataclass
from typing import ClassVar
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployCMD(PumpwoodDeployDataclassMixin):
    """Commands that will be ran at the deployment."""


@dataclass
class PumpwoodDeployCMDRun(PumpwoodDeployCMD):
    """Commands that will be ran at the deployment."""
    _type: str = "run"
    file: str
    sleep: int = 5
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}