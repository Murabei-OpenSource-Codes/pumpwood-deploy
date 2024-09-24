"""PumpWood ETL Microservice Deploy."""
import os
import pkg_resources
import base64


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_etl/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_etl/'
    'resources/deploy__app.yml').read().decode()
worker_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_etl/'
    'resources/deploy__worker.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_etl/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodETLMicroservice:
    """PumpWoodETLMicroservice."""

    def __init__(self,
                 microservice_password: str,
                 bucket_name: str,
                 app_version: str,
                 worker_version: str,
                 db_password: str = "pumpwood",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 workers_timeout: int = 300,
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 debug: str = "FALSE",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-etl",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_cpu: str = "1m",
                 app_requests_memory: str = "20Mi",
                 worker_replicas: int = 1,
                 worker_limits_memory: str = "60Gi",
                 worker_limits_cpu: str = "12000m",
                 worker_requests_memory: str = "20Mi",
                 worker_requests_cpu: str = "1m"):
        """
        __init__: Class constructor.

        Args:
            microservice_password (str): Microservice password.
            disk_size (str): Disk size (ex.: 50Gi, 100Gi)
            disk_name (str): Name of the disk that will be used in postgres
            postgres_public_ip (str): Postgres public IP.
            bucket_name (str): Name of the bucket (Storage)
            app_version (str): Verison of the estimation app imageself.
            worker_version (str): Version of the raw data worker.

        Kwargs:
            db_password (str): password at database.
            repository (str): Repository to pull Image.
            workers_timeout (int): Time in seconds to timeout of uwsgi worker.
            db_username (str): Database connection username.
            db_host (str): Database connection host.
            db_port (str): Database connection port.
            db_database (str): Database connection database.

        Returns:
          PumpWoodDatalakeMicroservice: New Object

        Raises:
          No especific raises.

        Example:
          No example yet.
        """
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        self.debug = debug
        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)
        self.repository = repository

        # App
        self.app_version = app_version
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Worker
        self.worker_version = worker_version
        self.worker_replicas = worker_replicas
        self.worker_limits_memory = worker_limits_memory
        self.worker_limits_cpu = worker_limits_cpu
        self.worker_requests_memory = worker_requests_memory
        self.worker_requests_cpu = worker_requests_cpu

        # Database
        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self, **kwargs):
        """
        Create deployment file.

        Args:
            kube_client: Client to communicate with Kubernets cluster.
        """
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)

        deployment_queue_manager_text_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.app_version,
                bucket_name=self.bucket_name,
                replicas=self.app_replicas,
                debug=self.app_debug,
                n_workers=self.app_workers,
                workers_timeout=self.app_timeout,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database,
                limits_memory=self.app_limits_memory,
                limits_cpu=self.app_limits_cpu,
                requests_memory=self.app_requests_memory,
                requests_cpu=self.app_requests_cpu)

        worker_deployment_text_frmted = worker_deployment.format(
            repository=self.repository,
            version=self.worker_version,
            replicas=self.worker_replicas,
            bucket_name=self.bucket_name,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            limits_memory=self.worker_limits_memory,
            limits_cpu=self.worker_limits_cpu,
            requests_memory=self.worker_requests_memory,
            requests_cpu=self.worker_requests_cpu)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_etl__secrets',
             'content': secrets_text_formated, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append(
                {'type': 'deploy', 'name': 'pumpwood_etl__postgres',
                 'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_etl__deploy',
             'content': deployment_queue_manager_text_frmtd, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_etl__worker',
             'content': worker_deployment_text_frmted, 'sleep': 0})
        return list_return
