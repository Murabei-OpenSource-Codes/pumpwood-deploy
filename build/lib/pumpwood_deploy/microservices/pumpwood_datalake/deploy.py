"""
PumpWood DataLake Microservice Deploy.

Datalake Microservice is the main service for data storage, it will
define modeling units the main dimension for storing information on
Pumpwood
"""
import os
import pkg_resources
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
    """Deploy Class for Datalake Microservice."""

    def __init__(self,
                 bucket_name: str,
                 app_version: str,
                 worker_version: str,
                 microservice_password: str = "microservice--datalake",
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
        """
        Class Constructor.

        Args:
            bucket_name [str]:
                Name of the bucket that will be associated with pods.
            microservice_password [str]:
                Password associated with service user `microservice--datalake`.
            db_username [str]:
                Username for connection with Postgres.
            db_password [str]:
                Password for connection with Postgres.
            db_host [str]:
                Host for connection with Postgres.
            db_port [str]:
                Port for connection with Postgres.
            db_database [str]:
                Database for connection with Postgres.
            repository [str]:
                Repository that will be used to fetch `pumpwood-datalake-app`
                and `pumpwood-datalake-dataloader-worker` images.
            test_db_version [str]:
                Version of the database for testing.
            test_db_repository [str]:
                Repository associated with testing database.
            test_db_limits_memory [str]:
                Memory limits associated with test database.
            test_db_limits_cpu [str]:
                CPU limits associated with test database.
            app_version [str]:
                Version of the application image.
            app_debug [str]:
                If application is set as DEBUG mode. Values 'TRUE'/'FALSE'.
            app_replicas [int]:
                Number of replicas for application pods.
            app_timeout [int]:
                Timeout in seconds for requests at application.
            app_workers [int]:
                Number of workers that will be spanned at guinicorn.
            app_limits_memory [str]:
                Memory limit associated with application pods.
            app_limits_cpu [str]:
                CPU limit associated with application pods.
            app_requests_memory [str]:
                Memory requested associated with application pods.
            app_requests_cpu [str]:
                CPU requested associated with application pods.
            worker_version [str]:
                Version for the worker pod.
            worker_debug [str]:
                If worker is set as DEBUG mode. Values 'TRUE'/'FALSE'.
            worker_replicas [int]:
                Number of pods that will be deployed for worker.
            worker_n_parallel [int]:
                Number of parallel requests that will be performed to
                upload data to datalake.
            worker_chunk_size [int]:
                Number of rows that will be uploaded to database at each
                parallel request.
            worker_query_limit [int]:
                Number of rows that will be treated at each upload cicle.
            worker_limits_memory [str]:
                Memory limit associated with dataloader worker pods.
            worker_limits_cpu [str]:
                CPU limit associated with dataloader worker pods.
            worker_requests_memory [str]:
                Memory requested associated with dataloader worker pods.
            worker_requests_cpu [str]:
                CPU requested associated with dataloader worker pods.
        """
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
