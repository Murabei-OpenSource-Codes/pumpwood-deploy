"""Module to define Pumpwood deploy associated types."""
from dataclasses import dataclass
from typing import ClassVar
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeploy(PumpwoodDeployDataclassMixin):
    """General class used to deploy pumpwood components."""


@dataclass
class PumpwoodDeploySecret(PumpwoodDeploy):
    """Class used to deploy secrets using pumpwood deploy."""
    _type: str = "secrets"
    name: str
    content: str
    sleep: int = 5
    namespace: str | None = None
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}
    """Rename field on the dataclass and the response, this migth be
       particullary usefull when dealling with fields like 'in', which is
       not avaiable."""


@dataclass
class PumpwoodDeploySecretFile(PumpwoodDeploy):
    """Class used to deploy secrets files using pumpwood deploy."""
    _type: str = "secrets_file"
    name: str
    path: str
    sleep: int = 5
    namespace: str | None = None
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployDeployment(PumpwoodDeploy):
    """Class used to deploy deployments."""
    _type: str = "deploy"
    name: str
    content: str
    sleep: int = 0
    namespace: str | None = None
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployConfigMap(PumpwoodDeploy):
    """Class used to deploy configmaps."""
    _type: str = "configmap"
    name: str
    content: str
    sleep: int = 0
    namespace: str | None = None
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployConfigMapFile(PumpwoodDeploy):
    """Class used to deploy configmap file."""
    _type: str = "configmap_file"
    file_name: str
    name: str
    file_path: str = None
    content: str = None
    keyname: str = None
    namespace: str | None = None
    sleep: int = 0
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployVolume(PumpwoodDeploy):
    """Class used to deploy volumes."""
    _type: str = "volume"
    name: str
    content: str
    sleep: int = 0
    namespace: str | None = None
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployService(PumpwoodDeploy):
    """Class used to deploy services."""
    _type: str = "service"
    name: str
    content: str
    sleep: int = 0
    namespace: str | None = None
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}