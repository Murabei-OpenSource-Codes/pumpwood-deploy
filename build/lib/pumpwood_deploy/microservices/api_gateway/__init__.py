"""Deployment of Api Gateway Microservices."""
from .deploy import (
    ApiGatewayCertbot, ApiGatewayCORSTerminaton)


__all__ = [
    ApiGatewayCertbot, ApiGatewayCORSTerminaton
]
