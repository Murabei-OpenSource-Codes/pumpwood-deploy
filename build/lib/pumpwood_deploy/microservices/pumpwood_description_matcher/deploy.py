"""Deploy Description Microservice.

Desription Microservice is used to integrate different Pumpwood
deploy in other to dimenstions between them can be shared and variables
transfered between DataLakes.
"""
import pkg_resources
import os
import base64


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_description_matcher/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_description_matcher/'
    'resources/deploy__app.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_description_matcher/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodDescriptionMatcherMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self,
                 microservice_password: str,
                 bucket_name: str,
                 app_version: str,
                 db_password: str = "pumpwood",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-description-matcher",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m"):
        """
        __init__: Class constructor.

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
        """
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)
        self.repository = repository.rstrip("/")

        # App
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_version = app_version
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Database
        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository.rstrip("/")

    def create_deployment_file(self, **kwargs):
        """
        Create deployment file.

        Args:
            No kwargs.
        """
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)

        deployment_text_frmtd = \
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

        list_return = [
            {'type': 'secrets',
             'name': 'pumpwood_description_matcher__secrets',
             'content': secrets_text_formated, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append(
                {'type': 'deploy',
                 'name': 'pumpwood_description_matcher__postgres',
                 'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_description_matcher__deploy',
             'content': deployment_text_frmtd, 'sleep': 0})
        return list_return
