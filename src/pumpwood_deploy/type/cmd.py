"""Deploy command types for Pumpwood deploy."""
from dataclasses import dataclass
from typing import ClassVar
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployCMD(PumpwoodDeployDataclassMixin):
    """Base class for deploy command descriptors."""


@dataclass
class PumpwoodDeployCMDRun(PumpwoodDeployCMD):
    """Shell script command executed during deployment."""
    file: str
    """Path to the generated deploy shell script."""
    _type: str = "run"
    sleep: int = 5
    """Seconds to wait after the script finishes."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}
