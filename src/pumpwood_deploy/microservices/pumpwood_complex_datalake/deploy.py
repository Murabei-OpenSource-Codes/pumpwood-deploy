"""PumpWood Complex DataLake Microservice Deploy.

Complex datalake stores unstrukturated data such as images, texts, audio and
video. It also permits anotating the database, permiting training models
using this data.
"""
import pkg_resources
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_complex_datalake/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_complex_datalake/'
    'resources/deploy__app.yml').read().decode()
worker_datalake_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_complex_datalake/'
    'resources/worker__datalake.yml').read().decode()
worker_simple_annotation_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_complex_datalake/'
    'resources/worker__simple_anotation.yml').read().decode()
worker_complex_annotation_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_complex_datalake/'
    'resources/worker__complex_anotation.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_complex_datalake/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodComplexDatalakeMicroservice:
    """PumpWood Complex Datalake Microservice."""

    def __init__(self,
                 bucket_name: str,
                 app_version: str,
                 microservice_password: str = "microservice--complex-datalake",
                 worker_datalake_dataloader_version: str,
                 worker_simple_dataloader_version: str,
                 worker_complex_dataloader_version: str,
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-complex-datalake",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 db_password: str = "pumpwood",

                 repository: str = "gcr.io/repositorio-geral-170012",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",

                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",

                 datalake_dataloader_replicas: int = 1,
                 datalake_dataloader_n_parallel: int = 4,
                 datalake_dataloader_chunk_size: int = 1000,
                 datalake_dataloader_query_limit: int = 1000000,
                 datalake_dataloader_limits_memory: str = "60Gi",
                 datalake_dataloader_limits_cpu: str = "12000m",
                 datalake_dataloader_requests_memory: str = "20Mi",
                 datalake_dataloader_requests_cpu: str = "1m",

                 simple_dataloader_replicas: int = 1,
                 simple_dataloader_n_parallel: int = 4,
                 simple_dataloader_chunk_size: int = 1000,
                 simple_dataloader_query_limit: int = 1000000,
                 simple_dataloader_limits_memory: str = "60Gi",
                 simple_dataloader_limits_cpu: str = "12000m",
                 simple_dataloader_requests_memory: str = "20Mi",
                 simple_dataloader_requests_cpu: str = "1m",

                 complex_dataloader_replicas: int = 1,
                 complex_dataloader_n_parallel: int = 4,
                 complex_dataloader_chunk_size: int = 1000,
                 complex_dataloader_query_limit: int = 1000000,
                 complex_dataloader_limits_memory: str = "60Gi",
                 complex_dataloader_limits_cpu: str = "12000m",
                 complex_dataloader_requests_memory: str = "20Mi",
                 complex_dataloader_requests_cpu: str = "1m"):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            microservice_password(str): Microservice password.
            postgres_public_ip (str): Postgres public IP.
            firewall_ips (list): List the IPs allowed to connect to datalake.
            bucket_name (str): Name of the bucket (Storage)
            app_version (str): Version of the App Image.
            worker_datalake_dataloader_version (str): Version of the complex
                datalake dataloader.
            worker_simple_dataloader_version (str): Version of the complex
                simple annotation dataloader.
            worker_complex_dataloader_version (str): Version of the complex
                complex annotation dataloader.

        Kwargs:
          disk_size (str): Disk size (ex.: 50Gi, 100Gi)
          disk_name (str): Name of the disk that will be used in postgres
          repository (str) = "gcr.io/repositorio-geral-170012": Repository to
            pull Image
          test_db_version (str): Set a test database with version.
          test_db_repository (str): Define a repository for the test
            database.
          db_username (str): Database connection username.
          db_host (str): Database connection host.
          db_port (str): Database connection port.
          db_database (str): Database connection database.
          app_replicas (int) = 1: Number of replicas in app deployment.
          app_timeout (int): Timeout in seconds for the guinicorn workers.
          app_workers (int): Number of workers to spaw at guinicorn.
          app_limits_memory (str) = "60Gi": Memory limits for app pods.
          app_limits_cpu (str) = "12000m": CPU limits for app pods.
          app_requests_memory (str) = "20Mi": Memory requests for app pods.
          app_requests_cpu (str) = "1m": CPU requests for app pods.

          *_replicas (int) = 1: Number of replicas associated with
            dataloader.
          *_n_chunks (str) = 5: n chunks working o data loader.
          *_chunk_size (str) = 5000: Size of the datalake chunks.
          *_limits_memory (str) = "60Gi": Memory requests for worker
            pods.
          *_limits_cpu (str) = "12000m": CPU requests for worker pods.
          *_requests_memory (str) = "20Mi": Memory requests for worker
            pods.
          *_requests_cpu (str) = "1m": CPU requests for worker pod.
          postgres_limits_memory (str) = "60Gi":  Memory limits for postgres
            pod.
          postgres_limits_cpu (str) = "12000m":  CPU limits for postgres pod.
          postgres_requests_memory (str) = "20Mi":  Memory request for postgres
            pod.
          postgres_requests_cpu (str) = "1m":  CPU request for postgres pod.

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

        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database
        self.repository = repository.rstrip("/")

        # Image versions
        self.app_debug = app_debug
        self.app_version = app_version
        self.worker_datalake_dataloader_version = \
            worker_datalake_dataloader_version
        self.worker_simple_dataloader_version = \
            worker_simple_dataloader_version
        self.worker_complex_dataloader_version = \
            worker_complex_dataloader_version

        # App
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Worker Datalake
        self.datalake_dataloader_replicas = \
            datalake_dataloader_replicas
        self.datalake_dataloader_n_parallel = \
            datalake_dataloader_n_parallel
        self.datalake_dataloader_chunk_size = \
            datalake_dataloader_chunk_size
        self.datalake_dataloader_query_limit = \
            datalake_dataloader_query_limit
        self.datalake_dataloader_limits_memory = \
            datalake_dataloader_limits_memory
        self.datalake_dataloader_limits_cpu = \
            datalake_dataloader_limits_cpu
        self.datalake_dataloader_requests_memory = \
            datalake_dataloader_requests_memory
        self.datalake_dataloader_requests_cpu = \
            datalake_dataloader_requests_cpu

        # Worker Simple Annotation
        self.simple_dataloader_replicas = \
            simple_dataloader_replicas
        self.simple_dataloader_n_parallel = \
            simple_dataloader_n_parallel
        self.simple_dataloader_chunk_size = \
            simple_dataloader_chunk_size
        self.simple_dataloader_query_limit = \
            simple_dataloader_query_limit
        self.simple_dataloader_limits_memory = \
            simple_dataloader_limits_memory
        self.simple_dataloader_limits_cpu = \
            simple_dataloader_limits_cpu
        self.simple_dataloader_requests_memory = \
            simple_dataloader_requests_memory
        self.simple_dataloader_requests_cpu = \
            simple_dataloader_requests_cpu

        # Worker Complex Annotation
        self.complex_dataloader_replicas = \
            complex_dataloader_replicas
        self.complex_dataloader_n_parallel = \
            complex_dataloader_n_parallel
        self.complex_dataloader_chunk_size = \
            complex_dataloader_chunk_size
        self.complex_dataloader_query_limit = \
            complex_dataloader_query_limit
        self.complex_dataloader_limits_memory = \
            complex_dataloader_limits_memory
        self.complex_dataloader_limits_cpu = \
            complex_dataloader_limits_cpu
        self.complex_dataloader_requests_memory = \
            complex_dataloader_requests_memory
        self.complex_dataloader_requests_cpu = \
            complex_dataloader_requests_cpu

        # Database
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository.rstrip("/")

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

        worker_datalake_deployment_frmted = \
            worker_datalake_deployment.format(
                repository=self.repository,
                version=self.worker_datalake_dataloader_version,
                bucket_name=self.bucket_name,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database,
                n_parallel=self.datalake_dataloader_n_parallel,
                chunk_size=self.datalake_dataloader_chunk_size,
                query_limit=self.datalake_dataloader_query_limit,
                replicas=self.datalake_dataloader_replicas,
                requests_memory=self.datalake_dataloader_requests_memory,
                requests_cpu=self.datalake_dataloader_requests_cpu,
                limits_cpu=self.datalake_dataloader_limits_cpu,
                limits_memory=self.datalake_dataloader_limits_memory)

        worker_simple_annotation_deployment_frmted = \
            worker_simple_annotation_deployment.format(
                repository=self.repository,
                version=self.worker_simple_dataloader_version,
                bucket_name=self.bucket_name,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database,
                n_parallel=self.simple_dataloader_n_parallel,
                chunk_size=self.simple_dataloader_chunk_size,
                query_limit=self.simple_dataloader_query_limit,
                replicas=self.simple_dataloader_replicas,
                requests_memory=self.simple_dataloader_requests_memory,
                requests_cpu=self.simple_dataloader_requests_cpu,
                limits_cpu=self.simple_dataloader_limits_cpu,
                limits_memory=self.simple_dataloader_limits_memory)

        worker_complex_annotation_deployment_frmted = \
            worker_complex_annotation_deployment.format(
                repository=self.repository,
                version=self.worker_complex_dataloader_version,
                bucket_name=self.bucket_name,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database,
                n_parallel=self.complex_dataloader_n_parallel,
                chunk_size=self.complex_dataloader_chunk_size,
                query_limit=self.complex_dataloader_query_limit,
                replicas=self.complex_dataloader_replicas,
                requests_memory=self.complex_dataloader_requests_memory,
                requests_cpu=self.complex_dataloader_requests_cpu,
                limits_cpu=self.complex_dataloader_limits_cpu,
                limits_memory=self.complex_dataloader_limits_memory)

        list_return = [{
            'type': 'secrets',
            'name': 'pumpwood_complex__datalake__secrets',
            'content': secrets_text_formated,
            'sleep': 5}]

        # Postgres
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy',
                'name': 'pumpwood_complex__datalake__postgres',
                'content': deployment_postgres_text_f,
                'sleep': 0})

        # App
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_complex__datalake__deploy',
            'content': app_deployment_frmtd,
            'sleep': 0})

        # Workers
        list_return.append({
            'type': 'deploy',
            'name': 'pumpwood_complex__datalake_dataloader_worker',
            'content': worker_datalake_deployment_frmted,
            'sleep': 0})
        list_return.append({
            'type': 'deploy',
            'name': 'pumpwood_complex__simple_annotation_dataloader_worker',
            'content': worker_simple_annotation_deployment_frmted,
            'sleep': 0})
        list_return.append({
            'type': 'deploy',
            'name': 'pumpwood_complex__complex_annotation_dataloader_worker',
            'content': worker_complex_annotation_deployment_frmted,
            'sleep': 0})
        return list_return
