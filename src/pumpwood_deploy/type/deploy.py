"""Deployment manifest types for Pumpwood deploy."""
from dataclasses import dataclass
from typing import ClassVar
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeploy(PumpwoodDeployDataclassMixin):
    """Base class for Kubernetes deployment manifest payloads."""


@dataclass
class PumpwoodDeploySecret(PumpwoodDeploy):
    """Inline Kubernetes Secret manifest."""
    name: str
    """Manifest file name prefix."""
    content: str
    """Rendered YAML content."""
    _type: str = "secrets"
    sleep: int = 5
    """Seconds to wait after applying the manifest."""
    namespace: str | None = None
    """Optional target namespace override."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeploySecretFile(PumpwoodDeploy):
    """Kubernetes Secret created from one or more local files."""
    name: str
    """Secret resource name."""
    path: str
    """Local file path or list of paths serialized for deploy."""
    _type: str = "secrets_file"
    sleep: int = 5
    """Seconds to wait after applying the secret."""
    namespace: str | None = None
    """Optional target namespace override."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployDeployment(PumpwoodDeploy):
    """Kubernetes Deployment manifest."""
    name: str
    """Manifest file name prefix."""
    content: str
    """Rendered YAML content."""
    _type: str = "deploy"
    sleep: int = 5
    """Seconds to wait after applying the manifest."""
    namespace: str | None = None
    """Optional target namespace override."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployConfigMap(PumpwoodDeploy):
    """Inline Kubernetes ConfigMap manifest."""
    name: str
    """Manifest file name prefix."""
    content: str
    """Rendered YAML content."""
    _type: str = "configmap"
    sleep: int = 5
    """Seconds to wait after applying the manifest."""
    namespace: str | None = None
    """Optional target namespace override."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployConfigMapFile(PumpwoodDeploy):
    """Kubernetes ConfigMap created from a local file."""
    file_name: str
    """Resource file name used inside the generated manifest."""
    name: str
    """ConfigMap resource name."""
    _type: str = "configmap_file"
    file_path: str = None
    """Optional local source file path."""
    content: str = None
    """Optional inline file content."""
    keyname: str = None
    """Optional ConfigMap data key override."""
    namespace: str | None = None
    """Optional target namespace override."""
    sleep: int = 5
    """Seconds to wait after applying the manifest."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployVolume(PumpwoodDeploy):
    """Persistent volume claim manifest for provider disks."""
    name: str
    """Manifest file name prefix."""
    disk_name: str
    """Provider disk identifier."""
    disk_size: str
    """Requested disk size."""
    volume_claim_name: str
    """Kubernetes persistent volume claim name."""
    _type: str = "volume"
    sleep: int = 10
    """Seconds to wait after applying the manifest."""
    namespace: str | None = None
    """Optional target namespace override."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}


@dataclass
class PumpwoodDeployService(PumpwoodDeploy):
    """Kubernetes Service manifest."""
    name: str
    """Manifest file name prefix."""
    content: str
    """Rendered YAML content."""
    _type: str = "service"
    sleep: int = 0
    """Seconds to wait after applying the manifest."""
    namespace: str | None = None
    """Optional target namespace override."""
    _RENAME_FIELDS: ClassVar[dict[str, str]] = {"_type": "type"}
