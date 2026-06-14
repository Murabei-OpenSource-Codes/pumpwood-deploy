"""Kubernetes provider parameter types for Pumpwood deploy."""
from dataclasses import dataclass
from .general import PumpwoodDeployDataclassMixin


@dataclass
class PumpwoodDeployK8sParameter(PumpwoodDeployDataclassMixin):
    """Base class for Kubernetes deployment parameters."""


@dataclass
class PumpwoodDeployK8sParameterGCP(PumpwoodDeployK8sParameter):
    """GCP cluster connection parameters."""
    cluster_name: str
    zone: str
    project: str

    def __init__(self, cluster_name: str, zone: str, project: str):
        """Initialize GCP cluster connection parameters.

        Args:
            cluster_name (str):
                Name of the GKE cluster.
            zone (str):
                GCP zone associated with the cluster.
            project (str):
                Google Cloud project identifier.
        """
        self.cluster_name = cluster_name
        self.zone = zone
        self.project = project


@dataclass
class PumpwoodDeployK8sParameterAzure(PumpwoodDeployK8sParameter):
    """Azure AKS cluster connection parameters."""
    subscription: str
    resource_group: str
    k8s_resource_group: str
    aks_resource: str

    def __init__(self, subscription: str, resource_group: str,
                 k8s_resource_group: str, aks_resource: str):
        """Initialize Azure cluster connection parameters.

        Args:
            subscription (str):
                Azure subscription identifier.
            resource_group (str):
                Resource group that owns the AKS deployment.
            k8s_resource_group (str):
                Resource group created by AKS for cluster components.
            aks_resource (str):
                AKS cluster resource name.
        """
        self.subscription = subscription
        self.resource_group = resource_group
        self.k8s_resource_group = k8s_resource_group
        self.aks_resource = aks_resource


@dataclass
class PumpwoodDeployK8sParameterAWS(PumpwoodDeployK8sParameter):
    """AWS EKS cluster connection parameters."""
    region: str
    cluster_name: str

    def __init__(self, region: str, cluster_name: str):
        """Initialize AWS cluster connection parameters.

        Args:
            region (str):
                AWS region associated with the EKS cluster.
            cluster_name (str):
                EKS cluster name.
        """
        self.region = region
        self.cluster_name = cluster_name
