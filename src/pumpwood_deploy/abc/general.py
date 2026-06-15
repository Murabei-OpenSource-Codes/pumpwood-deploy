"""Abstract classes for Pumpwood deploy."""
from abc import ABC, abstractmethod
from pumpwood_deploy.type import PumpwoodDeploy


class BasePumpwoodDeployMicroservice(ABC):
    """Base class for microservice deploy implementations in Kubernetes."""

    @abstractmethod
    def create_deployment_file(self) -> list[PumpwoodDeploy]:
        """Build Kubernetes manifests for the microservice.

        Returns:
            list[PumpwoodDeploy]:
                Ordered deployment objects to apply to the cluster.

        Raises:
            NotImplementedError:
                If the subclass does not implement manifest generation.
        """
        raise NotImplementedError(
            "Create deployment file is not implemented")
