"""PumpWood DataLake Microservice Deploy."""
import os
import base64
import pkg_resources


coordinator_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'trino/resources/deploy__coordenator.yml').read().decode()
worker_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'trino/resources/deploy__worker.yml').read().decode()
secrets_trino = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'trino/resources/secrets.yml').read().decode()


class TrinoMicroservice:
    """Deploy Metabase as microservice."""

    def __init__(self,
                 shared_secret: str,
                 catalog_dir_zip_path: str,
                 worker_replicas: int = 1,
                 worker_limits_memory: str = "60Gi",
                 worker_limits_cpu: str = "12000m",
                 worker_requests_memory: str = "20Mi",
                 worker_requests_cpu: str = "1m",
                 coordenator_limits_memory: str = "60Gi",
                 coordenator_limits_cpu: str = "12000m",
                 coordenator_requests_memory: str = "20Mi",
                 coordenator_requests_cpu: str = "1m",):
        """
        __init__: Class constructor.

        Args:
            shared_secret (str): Coordenator/Workers shared secret.
            catalog_dir_zip (str): Catalog directiory zip file path. It
                is a path to the catalog directiory containing
                database connections.
        Kwargs:
            No Kwargs.
        Returns:
          TrinoMicroservice: New Object
        Raises:
          No especific raises.
        Example:
          No example yet.
        """
        self._shared_secret = base64.b64encode(shared_secret.encode()).decode()
        self._catalog_dir_zip_path = catalog_dir_zip_path
        self.worker_replicas = worker_replicas
        self.base_path = os.path.dirname(__file__)

        # Cluster requirements
        self.worker_limits_memory = worker_limits_memory
        self.worker_limits_cpu = worker_limits_cpu
        self.worker_requests_memory = worker_requests_memory
        self.worker_requests_cpu = worker_requests_cpu
        self.coordenator_limits_memory = coordenator_limits_memory
        self.coordenator_limits_cpu = coordenator_limits_cpu
        self.coordenator_requests_memory = coordenator_requests_memory
        self.coordenator_requests_cpu = coordenator_requests_cpu

    def create_deployment_file(self, **kwargs):
        """create_deployment_file."""
        # General secrets
        frm_secrets_trino = secrets_trino.format(
            shared_secret=self._shared_secret)
        frm_coordinator_deployment = coordinator_deployment.format(
            requests_memory=self.coordenator_requests_memory,
            requests_cpu=self.coordenator_requests_cpu,
            limits_memory=self.coordenator_limits_memory,
            limits_cpu=self.coordenator_limits_cpu)
        frm_worker_deployment = worker_deployment.format(
            replicas=self.worker_replicas,
            requests_memory=self.worker_requests_memory,
            requests_cpu=self.worker_requests_cpu,
            limits_memory=self.worker_limits_memory,
            limits_cpu=self.worker_limits_cpu)

        list_return = [
            {'type': 'secrets', 'name': 'trino__secrets',
             'content': frm_secrets_trino, 'sleep': 1},
            {'type': 'secrets_file', 'name': 'trino--catalog-file-secret',
             'path': self._catalog_dir_zip_path, 'sleep': 1},
            {'type': 'deploy', 'name': 'trino__coordinator',
             'content': frm_coordinator_deployment, 'sleep': 0},
            {'type': 'deploy', 'name': 'trino__worker',
             'content': frm_worker_deployment, 'sleep': 0},
        ]
        return list_return
