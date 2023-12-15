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
hive_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'trino/resources/deploy__hive.yml').read().decode()
postgres__test = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'trino/resources/postgres__test.yml').read().decode()
secrets_trino = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'trino/resources/secrets.yml').read().decode()


class TrinoMicroservice:
    """Deploy Metabase as microservice."""

    def __init__(self,
                 shared_secret: str,
                 catalog_dir_zip_path: str,
                 bucket_name: str,
                 worker_replicas: int = 1,
                 worker_limits_memory: str = "60Gi",
                 worker_limits_cpu: str = "12000m",
                 worker_requests_memory: str = "20Mi",
                 worker_requests_cpu: str = "1m",
                 coordenator_limits_memory: str = "60Gi",
                 coordenator_limits_cpu: str = "12000m",
                 coordenator_requests_memory: str = "20Mi",
                 coordenator_requests_cpu: str = "1m",
                 hive_postgres_username: str = "hive",
                 hive_postgres_password: str = "hive",
                 hive_postgres_database: str = "hive_metastore",
                 hive_postgres_host: str = "postgres-hive-metastore",
                 hive_postgres_port: str = "5432",
                 hive_metastore_requests_memory: str = "20Mi",
                 hive_metastore_requests_cpu: str = "1m",
                 hive_metastore_limits_memory: str = "60Gi",
                 hive_metastore_limits_cpu: str = "12000m",
                 test_db_hive_metastore_version: str = None,
                 test_db_hive_metastore_repository: str = 'southamerica-east1-docker.pkg.dev/repositorio-geral-170012/pumpwood-images/',
                 test_db_hive_metastore_limits_memory: str = "3Gi",
                 test_db_hive_metastore_limits_cpu: str = "4000m"):
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

        # Hive deploy
        self.bucket_name = bucket_name
        self._hive_postgres_username = base64.b64encode(
            hive_postgres_username.encode()).decode()
        self._hive_postgres_password = base64.b64encode(
            hive_postgres_password.encode()).decode()
        self.hive_postgres_database = hive_postgres_database
        self.hive_postgres_host = hive_postgres_host
        self.hive_postgres_port = hive_postgres_port

        # Cluster requirements
        self.worker_limits_memory = worker_limits_memory
        self.worker_limits_cpu = worker_limits_cpu
        self.worker_requests_memory = worker_requests_memory
        self.worker_requests_cpu = worker_requests_cpu
        self.coordenator_limits_memory = coordenator_limits_memory
        self.coordenator_limits_cpu = coordenator_limits_cpu
        self.coordenator_requests_memory = coordenator_requests_memory
        self.coordenator_requests_cpu = coordenator_requests_cpu
        self.hive_metastore_requests_memory = hive_metastore_requests_memory
        self.hive_metastore_requests_cpu = hive_metastore_requests_cpu
        self.hive_metastore_limits_memory = hive_metastore_limits_memory
        self.hive_metastore_limits_cpu = hive_metastore_limits_cpu

        # Test database
        self.test_db_hive_metastore_version = \
            test_db_hive_metastore_version
        self.test_db_hive_metastore_repository = (
            test_db_hive_metastore_repository + "/"
            if test_db_hive_metastore_repository is not None else "")
        self.test_db_hive_metastore_limits_memory = \
            test_db_hive_metastore_limits_memory
        self.test_db_hive_metastore_limits_cpu = \
            test_db_hive_metastore_limits_cpu

    def create_deployment_file(self, **kwargs):
        """create_deployment_file."""
        # General secrets
        frm_secrets_trino = secrets_trino.format(
            shared_secret=self._shared_secret,
            hive_database_user=self._hive_postgres_username,
            hive_database_password=self._hive_postgres_password)
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

        # Hive metastore
        frm_hive_deployment = hive_deployment.format(
            requests_memory=self.hive_metastore_requests_memory,
            requests_cpu=self.hive_metastore_requests_cpu,
            limits_memory=self.hive_metastore_limits_memory,
            limits_cpu=self.hive_metastore_limits_cpu,
            database_host=self.hive_postgres_host,
            database_port=self.hive_postgres_port,
            database_db=self.hive_postgres_database,
            bucket_name=self.bucket_name)

        frm_postgres__test = None
        if self.test_db_hive_metastore_version is not None:
            frm_postgres__test = postgres__test.format(
                version=self.test_db_hive_metastore_version,
                repository=self.test_db_hive_metastore_repository,
                limits_memory=self.test_db_hive_metastore_limits_memory,
                limits_cpu=self.test_db_hive_metastore_limits_cpu)

        list_return = [
            {'type': 'secrets', 'name': 'trino__secrets',
             'content': frm_secrets_trino, 'sleep': 1}]

        if frm_postgres__test is not None:
            list_return.append(
                {'type': 'deploy',
                 'name': 'trino__postgres_test_hive_metastore',
                 'content': frm_postgres__test, 'sleep': 1})

        list_return.extend([
            {'type': 'deploy', 'name': 'trino__hive_metastore',
             'content': frm_hive_deployment, 'sleep': 3},
            {'type': 'secrets_file', 'name': 'trino--catalog-file-secret',
             'path': self._catalog_dir_zip_path, 'sleep': 1},
            {'type': 'deploy', 'name': 'trino__coordinator',
             'content': frm_coordinator_deployment, 'sleep': 0},
            {'type': 'deploy', 'name': 'trino__worker',
             'content': frm_worker_deployment, 'sleep': 0},
        ])
        return list_return
