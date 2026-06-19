"""Cryptography helpers for Pumpwood deploy secrets.

This package provides utilities to generate cryptographic material used
when building Kubernetes secret manifests for Pumpwood microservices.

The main entry point is ``generate_fernet_key`` in ``general``, which
creates Fernet keys encoded for injection into YAML deploy files.
"""
from .general import generate_fernet_key


__all__ = [
    generate_fernet_key,
]
