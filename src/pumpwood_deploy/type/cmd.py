"""Deploy command types for Pumpwood deploy."""
from dataclasses import dataclass
from typing import ClassVar
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployCMD(PumpwoodDeployDataclassMixin):
    """Base class for deploy command descriptors."""


@dataclass
class PumpwoodDeployCMDRun(PumpwoodDeployCMD):
    """Audit shell script executed during deployment."""
    file: str
    """Path to the generated audit shell script under ``outputs/``."""
    _type: str = "run"
    """Command type identifier."""
    sleep: int = 5
    """Seconds to wait after the script finishes."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}
