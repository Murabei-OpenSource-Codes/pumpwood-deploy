"""PumpWood DataLake Microservice Deploy."""
import os
import pkg_resources
import base64


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_transformation/'
    'resources/secrets.yml').read().decode()
transformation_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_transformation/'
    'resources/deploy__app.yml').read().decode()
transformation_worker_estimation = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_transformation/'
    'resources/deploy__worker_estimation.yml').read().decode()
transformation_worker_prediction = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_transformation/'
    'resources/deploy__worker_transformation.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_transformation/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodTransformationMicroservice:
    """PumpWoodTransformationMicroservice."""

    def __init__(self,
                 microservice_password: str,
                 bucket_name: str,
                 app_version: str,
                 db_password: str = "pumpwood",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-transformation",
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
                 app_requests_cpu: str = "1m",
                 worker_estimation_replicas: int = 1,
                 worker_estimation_limits_memory: str = "60Gi",
                 worker_estimation_limits_cpu: str = "12000m",
                 worker_estimation_requests_memory: str = "20Mi",
                 worker_estimation_requests_cpu: str = "1m",
                 worker_transformation_replicas: int = 1,
                 worker_transformation_limits_memory: str = "60Gi",
                 worker_transformation_limits_cpu: str = "12000m",
                 worker_transformation_requests_memory: str = "20Mi",
                 worker_transformation_requests_cpu: str = "1m"):
        """
        __init__: Class constructor.

        Args:
          db_password (str): password at database.
          microservice_password (str): Microservice password.
          disk_size (str): Disk size (ex.: 50Gi, 100Gi)
          disk_name (str): Name of the disk that will be used in postgres
          postgres_public_ip (str): Postgres public IP.
          bucket_name (str): Name of the bucket (Storage)
          app_version (str): App version.
          version_rawdata (str): Version of the raw data worker.
          version_dataloader (str): Version of the raw data worker.

        Kwargs:
          firewall_ips (list[str]): List with the IPs to allow connection to
            database.
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

        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)
        self.repository = repository

        # App
        self.app_version = app_version
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers

        self.app_limits_memory = \
            app_limits_memory
        self.app_limits_cpu = \
            app_limits_cpu
        self.app_requests_memory = \
            app_requests_memory
        self.app_requests_cpu = \
            app_requests_cpu
        self.worker_estimation_replicas = \
            worker_estimation_replicas
        self.worker_estimation_limits_memory = \
            worker_estimation_limits_memory
        self.worker_estimation_limits_cpu = \
            worker_estimation_limits_cpu
        self.worker_estimation_requests_memory = \
            worker_estimation_requests_memory
        self.worker_estimation_requests_cpu = \
            worker_estimation_requests_cpu
        self.worker_transformation_replicas = \
            worker_transformation_replicas
        self.worker_transformation_limits_memory = \
            worker_transformation_limits_memory
        self.worker_transformation_limits_cpu = \
            worker_transformation_limits_cpu
        self.worker_transformation_requests_memory = \
            worker_transformation_requests_memory
        self.worker_transformation_requests_cpu = \
            worker_transformation_requests_cpu

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

        transformation_deployment_formated = \
            transformation_deployment.format(
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

        worker_estimation_formated = transformation_worker_estimation.format(
            repository=self.repository,
            version=self.app_version,
            bucket_name=self.bucket_name,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            replicas=self.worker_estimation_replicas,
            limits_memory=self.worker_estimation_limits_memory,
            limits_cpu=self.worker_estimation_limits_cpu,
            requests_memory=self.worker_estimation_requests_memory,
            requests_cpu=self.worker_estimation_requests_cpu)

        worker_prediction_formated = transformation_worker_prediction.format(
            repository=self.repository,
            version=self.app_version,
            bucket_name=self.bucket_name,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            replicas=self.worker_transformation_replicas,
            limits_memory=self.worker_transformation_limits_memory,
            limits_cpu=self.worker_transformation_limits_cpu,
            requests_memory=self.worker_transformation_requests_memory,
            requests_cpu=self.worker_transformation_requests_cpu)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_transformation__secrets',
             'content': secrets_text_formated, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append(
                {'type': 'deploy', 'name': 'pumpwood_transformation__postgres',
                 'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append(
            {'type': 'deploy', 'name': 'pumpwood_transformation__app',
             'content': transformation_deployment_formated, 'sleep': 0})
        list_return.append(
            {'type': 'deploy',
             'name': 'pumpwood_transformation__estimation_worker',
             'content': worker_estimation_formated, 'sleep': 0})
        list_return.append(
            {'type': 'deploy',
             'name': 'pumpwood_transformation__prediction_worker',
             'content': worker_prediction_formated, 'sleep': 0})
        return list_return
