"""PumpWood DataLake Microservice Deploy."""
import pkg_resources
import os
import base64


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_datalake/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_datalake/'
    'resources/deploy__app.yml').read().decode()
worker_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_datalake/'
    'resources/deploy__worker.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_datalake/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodDatalakeMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self,
                 microservice_password: str,
                 bucket_name: str,
                 app_version: str,
                 worker_version: str,
                 db_username: str = "pumpwood",
                 db_password: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-datalake",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_limits_memory: str = "1Gi",
                 test_db_limits_cpu: str = "1000m",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 worker_debug: str = "FALSE",
                 worker_replicas: int = 1,
                 worker_n_parallel: int = 4,
                 worker_chunk_size: int = 1000,
                 worker_query_limit: int = 1000000,
                 worker_limits_memory: str = "60Gi",
                 worker_limits_cpu: str = "12000m",
                 worker_requests_memory: str = "20Mi",
                 worker_requests_cpu: str = "1m"):
        """__init__: Class constructor."""
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)

        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database

        self.repository = repository.rstrip("/")
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_version = app_version
        self.worker_version = worker_version

        # App
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Worker
        self.worker_debug = worker_debug
        self.worker_replicas = worker_replicas
        self.worker_n_parallel = worker_n_parallel
        self.worker_chunk_size = worker_chunk_size
        self.worker_query_limit = worker_query_limit
        self.worker_limits_memory = worker_limits_memory
        self.worker_limits_cpu = worker_limits_cpu
        self.worker_requests_memory = worker_requests_memory
        self.worker_requests_cpu = worker_requests_cpu

        # Database
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository.rstrip("/")
        self.test_db_limits_memory = test_db_limits_memory
        self.test_db_limits_cpu = test_db_limits_cpu

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
                version=self.test_db_version,
                limits_memory=self.test_db_limits_memory,
                limits_cpu=self.test_db_limits_cpu)

        app_deployment_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.app_version,
                bucket_name=self.bucket_name,
                replicas=self.app_replicas,
                requests_memory=self.app_requests_memory,
                requests_cpu=self.app_requests_cpu,
                limits_cpu=self.app_limits_cpu,
                limits_memory=self.app_limits_memory,
                workers_timeout=self.app_timeout,
                n_workers=self.app_workers,
                debug=self.app_debug,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database)

        worker_deployment_text_frmted = worker_deployment.format(
            repository=self.repository,
            version=self.worker_version,
            bucket_name=self.bucket_name,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            n_parallel=self.worker_n_parallel,
            chunk_size=self.worker_chunk_size,
            query_limit=self.worker_query_limit,
            replicas=self.worker_replicas,
            requests_memory=self.worker_requests_memory,
            requests_cpu=self.worker_requests_cpu,
            limits_cpu=self.worker_limits_cpu,
            limits_memory=self.worker_limits_memory,
            debug=self.worker_debug)

        list_return = [{
            'type': 'secrets', 'name': 'pumpwood_datalake__secrets',
            'content': secrets_text_formated, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_datalake__postgres',
                'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_datalake__deploy',
            'content': app_deployment_frmtd, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_datalake_dataloader__worker',
            'content': worker_deployment_text_frmted, 'sleep': 0})
        return list_return
