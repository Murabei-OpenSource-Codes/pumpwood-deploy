"""Module to define K8s typing for parameter."""
from dataclasses import dataclass
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployStorage(PumpwoodDeployDataclassMixin):
    """Class to define K8s parameters for GCP storage."""


@dataclass
class PumpwoodDeployStorageGCP(PumpwoodDeployStorage):
    """Class to define K8s parameters for GCP storage."""
    credential_file: str
    """Path to local file with service user with storage access.
    Must be named key-storage.json
    """


@dataclass
class PumpwoodDeployStorageAzure(PumpwoodDeployStorage):
    """Class to define K8s parameters for Azure storage."""
    storage_connection_string: str
    """Storage connection string for Azure Blob Storage."""


@dataclass
class PumpwoodDeployStorageAWS(PumpwoodDeployStorage):
    """Class to define K8s parameters for AWS storage."""
    access_key_id: str
    """Access key id for the service user with s3 access."""
    secret_access_key: str
    """Secret access key for the service user with s3 access."""
