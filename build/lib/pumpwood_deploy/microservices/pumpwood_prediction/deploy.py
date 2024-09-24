"""PumpWood Prediction Microservice Deploy."""
import os
import pkg_resources
import base64


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_prediction/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_prediction/'
    'resources/deploy__app.yml').read().decode()
worker_rawdata = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_prediction/'
    'resources/deploy__worker_raw_data.yml').read().decode()
worker_dataloader = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_prediction/'
    'resources/deploy__worker_dataloader.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_prediction/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodPredictionMicroservice:
    """PumpWoodTransformationMicroservice."""

    def __init__(self,
                 microservice_password: str,
                 bucket_name: str,
                 app_version: str,
                 worker_rawdata_version: str,
                 worker_dataloader_version: str,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 db_username: str = "pumpwood",
                 db_password: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-prediction",
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
                 raw_replicas: int = 1,
                 raw_limits_memory: str = "60Gi",
                 raw_limits_cpu: str = "12000m",
                 raw_requests_memory: str = "20Mi",
                 raw_requests_cpu: str = "1m",
                 dataloader_replicas: int = 1,
                 dataloader_limits_memory: str = "60Gi",
                 dataloader_limits_cpu: str = "12000m",
                 dataloader_requests_memory: str = "20Mi",
                 dataloader_requests_cpu: str = "1m"):
        """__init__."""
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)

        # Datalake connection
        self.db_username = db_username
        self._db_password = base64.b64encode(
            db_password.encode()).decode()
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
        self.repository = repository.rstrip("/")
        self.app_version = app_version
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Raw data
        self.raw_replicas = raw_replicas
        self.worker_rawdata_version = worker_rawdata_version
        self.raw_limits_memory = raw_limits_memory
        self.raw_limits_cpu = raw_limits_cpu
        self.raw_requests_memory = raw_requests_memory
        self.raw_requests_cpu = raw_requests_cpu

        # Dataloader
        self.worker_dataloader_version = worker_dataloader_version
        self.dataloader_replicas = dataloader_replicas
        self.dataloader_limits_memory = dataloader_limits_memory
        self.dataloader_limits_cpu = dataloader_limits_cpu
        self.dataloader_requests_memory = dataloader_requests_memory
        self.dataloader_requests_cpu = dataloader_requests_cpu

        # Postgres
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository.rstrip("/")

    def create_deployment_file(self, **kwargs):
        """
        Create deployment file.

        Args:
            Non Args.
        """
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)

        deployment_app_text_formated = app_deployment.format(
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

        deployment_rawdata_text_formated = worker_rawdata.format(
            repository=self.repository,
            version=self.worker_rawdata_version,
            replicas=self.raw_replicas,
            bucket_name=self.bucket_name,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            datalake_db_username=self.datalake_db_username,
            datalake_db_host=self.datalake_db_host,
            datalake_db_port=self.datalake_db_port,
            datalake_db_database=self.datalake_db_database,
            limits_memory=self.raw_limits_memory,
            limits_cpu=self.raw_limits_cpu,
            requests_memory=self.raw_requests_memory,
            requests_cpu=self.raw_requests_cpu)

        deployment_dataloader_text_formated = worker_dataloader.format(
            repository=self.repository,
            version=self.worker_dataloader_version,
            bucket_name=self.bucket_name,
            replicas=self.dataloader_replicas,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            limits_memory=self.dataloader_limits_memory,
            limits_cpu=self.dataloader_limits_cpu,
            requests_memory=self.dataloader_requests_memory,
            requests_cpu=self.dataloader_requests_cpu)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_prediction__secrets',
             'content': secrets_text_formated, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append(
                {'type': 'deploy', 'name': 'pumpwood_prediction__postgres',
                 'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_prediction_app',
             'content': deployment_app_text_formated, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_prediction__rawdata_worker',
             'content': deployment_rawdata_text_formated, 'sleep': 0})
        list_return.append(
            {'type': 'deploy',
             'name': 'pumpwood_prediction_dataloader__dataloader_worker',
             'content': deployment_dataloader_text_formated, 'sleep': 0})
        return list_return
