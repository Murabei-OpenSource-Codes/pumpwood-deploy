"""Abstract classes for Pumpwood deploy."""
from abc import ABC, abstractmethod
from pumpwood_deploy.type import PumpwoodDeploy


class BasePumpwoodDeployMicroservice(ABC):
    """Base class for microservice deploy implementations in Kubernetes."""

    @abstractmethod
    def create_deployment_file(self) -> list[PumpwoodDeploy] | list[dict]:
        """Build Kubernetes manifests for the microservice.

        Returns:
            list[PumpwoodDeploy] | list[dict]:
                Ordered deployment objects or legacy dict payloads.

        Raises:
            NotImplementedError:
                If the subclass does not implement manifest generation.
        """
        raise NotImplementedError("Create deployment file is not implemented")
