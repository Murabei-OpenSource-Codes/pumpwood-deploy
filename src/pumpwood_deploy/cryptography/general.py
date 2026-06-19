"""Module to help creating secrets file content."""
from cryptography.fernet import Fernet


def generate_fernet_key() -> str:
    """Generate a Fernet key for Pumpwood crypto fields.

    The key is encoded as a UTF-8 string for use in YAML manifests.

    Returns:
        str:
            Base64-encoded Fernet key suitable for secret injection.
    """
    return Fernet.generate_key().decode()
