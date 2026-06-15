"""Object storage parameter types for Pumpwood deploy."""
from dataclasses import dataclass
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployStorage(PumpwoodDeployDataclassMixin):
    """Base class for object storage deployment parameters."""


@dataclass
class PumpwoodDeployStorageGCP(PumpwoodDeployStorage):
    """GCP object storage parameters."""
    credential_file: str

    def __init__(self, credential_file: str):
        """Initialize GCP storage credentials.

        Args:
            credential_file (str):
                Path to the service account JSON file. The file must
                be named ``key-storage.json`` for container mounts.

        Returns:
            None:
                Always returns None.
        """
        self.credential_file = credential_file


@dataclass
class PumpwoodDeployStorageAzure(PumpwoodDeployStorage):
    """Azure Blob Storage parameters."""
    storage_connection_string: str

    def __init__(self, storage_connection_string: str):
        """Initialize Azure storage credentials.

        Args:
            storage_connection_string (str):
                Azure Blob Storage connection string.

        Returns:
            None:
                Always returns None.
        """
        self.storage_connection_string = storage_connection_string


@dataclass
class PumpwoodDeployStorageAWS(PumpwoodDeployStorage):
    """AWS S3 storage parameters."""
    access_key_id: str
    secret_access_key: str

    def __init__(self, access_key_id: str, secret_access_key: str):
        """Initialize AWS S3 storage credentials.

        Args:
            access_key_id (str):
                Access key ID for the S3 service user.
            secret_access_key (str):
                Secret access key for the S3 service user.

        Returns:
            None:
                Always returns None.
        """
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
