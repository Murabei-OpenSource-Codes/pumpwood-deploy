"""PumpWood DataLake Microservice Deploy."""

import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from .resources.yml__resources import (
    app_deployment, worker_deployment, deployment_postgres,
    secrets, services__load_balancer, test_postgres)


class PumpWoodDatalakeMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self, db_password: str,
                 microservice_password: str,
                 bucket_name: str,
                 app_version: str,
                 worker_version: str,
                 disk_name: str = None,
                 disk_size: str = None,
                 postgres_public_ip: str = None,
                 firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-datalake",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 worker_replicas: int = 1,
                 worker_n_parallel: int = 4,
                 worker_chunk_size: int = 1000,
                 worker_query_limit: int = 1000000,
                 worker_limits_memory: str = "60Gi",
                 worker_limits_cpu: str = "12000m",
                 worker_requests_memory: str = "20Mi",
                 worker_requests_cpu: str = "1m",
                 postgres_limits_memory: str = "60Gi",
                 postgres_limits_cpu: str = "12000m",
                 postgres_requests_memory: str = "20Mi",
                 postgres_requests_cpu: str = "1m"):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            microservice_password(str): Microservice password.
            postgres_public_ip (str): Postgres public IP.
            firewall_ips (list): List the IPs allowed to connect to datalake.
            bucket_name (str): Name of the bucket (Storage)
            app_version (str): Verison of the App Image.
            worker_version (str): Verison of the Worker Image.

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
          app_debug (str): TRUE or FALSE, set app in debug mode.
          app_replicas (int) = 1: Number of replicas in app deployment.
          app_timeout (int): Timeout in seconds for the guinicorn workers.
          app_workers (int): Number of workers to spaw at guinicorn.
          app_limits_memory (str) = "60Gi": Memory limits for app pods.
          app_limits_cpu (str) = "12000m": CPU limits for app pods.
          app_requests_memory (str) = "20Mi": Memory requests for app pods.
          app_requests_cpu (str) = "1m": CPU requests for app pods.
          worker_replicas (int) = 1:
          worker_n_chunks (str) = 5: n chunks working o data loader.
          worker_chunk_size (str) = 5000: Size of the datalake chunks.
          worker_limits_memory (str) = "60Gi": Memory requests for worker
            pods.
          worker_limits_cpu (str) = "12000m": CPU requests for worker pods.
          worker_requests_memory (str) = "20Mi": Memory requests for worker
            pods.
          worker_requests_cpu (str) = "1m": CPU requests for worker pod.
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
        disk_deploy = (disk_name is not None and disk_size is not None)
        if disk_deploy and test_db_version is not None:
            raise Exception(
                "When working with test database, disk is not used.")

        postgres_certificates = create_ssl_key_ssl_crt()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()

        self.postgres_public_ip = postgres_public_ip
        self.firewall_ips = firewall_ips

        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)

        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database

        self.repository = repository
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
        self.worker_replicas = worker_replicas
        self.worker_n_parallel = worker_n_parallel
        self.worker_chunk_size = worker_chunk_size
        self.worker_query_limit = worker_query_limit
        self.worker_limits_memory = worker_limits_memory
        self.worker_limits_cpu = worker_limits_cpu
        self.worker_requests_memory = worker_requests_memory
        self.worker_requests_cpu = worker_requests_cpu

        # Database
        self.postgres_limits_memory = postgres_limits_memory
        self.postgres_limits_cpu = postgres_limits_cpu
        self.postgres_requests_memory = postgres_requests_memory
        self.postgres_requests_cpu = postgres_requests_cpu

        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self, kube_client):
        """
        Create deployment file.

        Args:
            kube_client: Client to communicate with Kubernets cluster.
        """
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt)

        volume_postgres_text_f = None
        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version,
                requests_memory=self.postgres_requests_memory,
                requests_cpu=self.postgres_requests_cpu,
                limits_memory=self.postgres_limits_memory,
                limits_cpu=self.postgres_limits_cpu)

        elif self.disk_size is not None:
            volume_postgres_text_f = kube_client.create_volume_yml(
                disk_name=self.disk_name,
                disk_size=self.disk_size,
                volume_claim_name="postgres-pumpwood-datalake")
            deployment_postgres_text_f = deployment_postgres.format(
                requests_memory=self.postgres_requests_memory,
                requests_cpu=self.postgres_requests_cpu,
                limits_memory=self.postgres_limits_memory,
                limits_cpu=self.postgres_limits_cpu)

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
            limits_memory=self.worker_limits_memory)

        list_return = [{
            'type': 'secrets', 'name': 'pumpwood_datalake__secrets',
            'content': secrets_text_formated, 'sleep': 5}]
        if volume_postgres_text_f is not None:
            list_return.append({
                'type': 'volume', 'name': 'pumpwood_datalake__volume',
                'content': volume_postgres_text_f, 'sleep': 10})
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

        if self.firewall_ips is not None and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'pumpwood_datalake__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})

        return list_return
