"""PumpWood Estimation Microservice Deploy.

This microservice is associated with estimation of mathematical models,
defining parameters associated with model and attributes that will be
considered inputs and outputs of the models.
"""
import os
import pkg_resources
import base64


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_estimation/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_estimation/'
    'resources/deploy__app.yml').read().decode()
worker_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_estimation/'
    'resources/deploy__worker.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_estimation/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodEstimationMicroservice:
    """PumpWoodEstimationMicroservice."""

    def __init__(self,
                 bucket_name: str,
                 app_version: str,
                 worker_version: str,
                 microservice_password: str = "microservice--estimation",
                 db_password: str = "pumpwood",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 workers_timeout: int = 300,
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-estimation",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 datalake_db_username: str = "pumpwood",
                 datalake_db_host: str = "postgres-pumpwood-datalake",
                 datalake_db_port: str = "5432",
                 datalake_db_database: str = "pumpwood",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 worker_replicas: int = 1,
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
        self.datalake_db_username = datalake_db_username
        self.datalake_db_host = datalake_db_host
        self.datalake_db_port = datalake_db_port
        self.datalake_db_database = datalake_db_database

        # App
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_version = app_version
        self.repository = repository
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Worker
        self.worker_replicas = worker_replicas
        self.worker_version = worker_version
        self.worker_limits_memory = worker_limits_memory
        self.worker_limits_cpu = worker_limits_cpu
        self.worker_requests_memory = worker_requests_memory
        self.worker_requests_cpu = worker_requests_cpu

        # Postgres
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self, **kwargs):
        """
        Create deployment file.

        Args:
            No args.
        """
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)

        app_deployment_formated = \
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
        worker_deployment_text_formated = worker_deployment.format(
            repository=self.repository,
            version=self.worker_version,
            replicas=self.worker_replicas,
            bucket_name=self.bucket_name,
            datalake_db_username=self.datalake_db_username,
            datalake_db_host=self.datalake_db_host,
            datalake_db_port=self.datalake_db_port,
            datalake_db_database=self.datalake_db_database,
            limits_memory=self.worker_limits_memory,
            limits_cpu=self.worker_limits_cpu,
            requests_memory=self.worker_requests_memory,
            requests_cpu=self.worker_requests_cpu)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_estimation__secrets',
             'content': secrets_text_formated, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append(
                {'type': 'deploy', 'name': 'pumpwood_estimation__postgres',
                 'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_estimation__deploy',
             'content': app_deployment_formated, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_estimation__rawdata',
             'content': worker_deployment_text_formated, 'sleep': 0})
        return list_return
