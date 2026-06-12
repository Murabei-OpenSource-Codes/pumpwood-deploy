"""Module to define K8s typing for parameter."""
from dataclasses import dataclass
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployK8sParameter(PumpwoodDeployDataclassMixin):
    """General definition of k8s deploy parameters."""


@dataclass
class PumpwoodDeployK8sParameterGCP(PumpwoodDeployK8sParameter):
    """Class to define K8s parameters for GCP provider."""
    cluster_name: str
    """Name of the K8s cluster."""
    zone: str
    """Zone associated with the cluster."""
    project: str
    """ID of the project at GCP."""


@dataclass
class PumpwoodDeployK8sParameterAzure(PumpwoodDeployK8sParameter):
    """Class to define K8s parameters for GCP provider."""
    subscription: str
    """Subscription associated with Cluster Deploy."""
    resource_group: str
    """Resorce group at which the solution was deployed."""
    k8s_resource_group: str
    """AKS resource group associated with the K8s deploy."""
    aks_resource: str
    """."""


@dataclass
class PumpwoodDeployK8sParameterAWS(PumpwoodDeployK8sParameter):
    """Class to define K8s parameters for GCP provider."""
    region: str
    """AWS region associated with K8s deploy."""
    cluster_name: str
    """Name of the cluster."""
