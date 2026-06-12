"""Abstract classes for Pumpwood deploy."""
from abc import ABC, abstractmethod
from pumpwood_deploy.type import ABCPumpwoodDeploy


class BasePumpwoodDeployMicroservice(ABC):
    """Base class to implement microservice deploy in K8s."""

    @abstractmethod
    def create_deployment_file(self, kube_client=None, **kwargs
                               ) -> list[ABCPumpwoodDeploy] | list[dict]:
        """Create_deployment_file.

        Args:
            kube_client (Kubernets):
                Instance of `kubernets.kubernets.Kubernets` object to help
                attacing disks to pods and other Kubernets operations.
            **kwargs:
                Compatilibity with other versions.
        """
        raise NotImplementedError("Create deployment file is not implemented")