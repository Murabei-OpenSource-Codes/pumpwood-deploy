"""Object storage parameter types for Pumpwood deploy."""
from dataclasses import dataclass
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployStorage(PumpwoodDeployDataclassMixin):
    """Base class for object storage deployment parameters."""


@dataclass
class PumpwoodDeployStorageGCP(PumpwoodDeployStorage):
    """Object storage parameters for Google Cloud Storage."""
    credential_file: str
    """Path to the service account JSON file.

    The file must be named ``key-storage.json`` for container mounts.
    """


@dataclass
class PumpwoodDeployStorageAzure(PumpwoodDeployStorage):
    """Object storage parameters for Azure Blob Storage."""
    storage_connection_string: str
    """Azure Blob Storage connection string."""


@dataclass
class PumpwoodDeployStorageAWS(PumpwoodDeployStorage):
    """Object storage parameters for Amazon S3."""
    access_key_id: str
    """Access key ID for the S3 service user."""
    secret_access_key: str
    """Secret access key for the S3 service user."""
