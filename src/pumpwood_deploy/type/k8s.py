"""Kubernetes provider parameter types for Pumpwood deploy."""
from dataclasses import dataclass
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployK8sParameter(PumpwoodDeployDataclassMixin):
    """Base class for Kubernetes deployment parameters."""


@dataclass
class PumpwoodDeployK8sParameterGCP(PumpwoodDeployK8sParameter):
    """Kubernetes deployment parameters for Google Cloud."""
    cluster_name: str
    """Name of the GKE cluster."""
    zone: str
    """GCP zone associated with the cluster."""
    project: str
    """Google Cloud project identifier."""


@dataclass
class PumpwoodDeployK8sParameterAzure(PumpwoodDeployK8sParameter):
    """Kubernetes deployment parameters for Microsoft Azure."""
    subscription: str
    """Azure subscription identifier."""
    resource_group: str
    """Resource group that owns the AKS deployment."""
    k8s_resource_group: str
    """Resource group created by AKS for cluster components."""
    aks_resource: str
    """AKS cluster resource name."""


@dataclass
class PumpwoodDeployK8sParameterAWS(PumpwoodDeployK8sParameter):
    """Kubernetes deployment parameters for Amazon Web Services."""
    region: str
    """AWS region associated with the EKS cluster."""
    cluster_name: str
    """EKS cluster name."""
