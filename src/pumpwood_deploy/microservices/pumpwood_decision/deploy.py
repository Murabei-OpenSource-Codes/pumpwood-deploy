"""PumpWood DataLake Microservice Deploy."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from .resources.yml__resources import (
    app_deployment, deployment_postgres, secrets, services__load_balancer,
    test_postgres, decision_model_yml)


class PumpWoodDescisionMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self, db_password: str,
                 microservice_password: str,
                 bucket_name: str,
                 version_app: str,
                 disk_name: str = None,
                 disk_size: str = None,
                 postgres_public_ip: str = None,
                 firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 debug: str = "FALSE",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-decision",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 app_replicas: int = 1,
                 workers_timeout: int = 300,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 postgres_limits_memory: str = "60Gi",
                 postgres_limits_cpu: str = "12000m",
                 postgres_requests_memory: str = "20Mi",
                 postgres_requests_cpu: str = "1m",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012"):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            microservice_password(str): Microservice password.
            postgres_public_ip (str): Postgres public IP.
            firewall_ips (list): List the IPs allowed to connect to datalake.
            bucket_name (str): Name of the bucket (Storage)
            version_app (str): Verison of the App Image.
            version_worker (str): Verison of the Worker Image.

        Kwargs:
          app_replicas (int) = 1: Number of replicas in app deployment.
          app_limits_memory (str) = "60Gi": Memory limits for app pods.
          app_limits_cpu (str) = "12000m": CPU limits for app pods.
          app_requests_memory (str) = "20Mi": Memory requests for app pods.
          app_requests_cpu (str) = "1m": CPU requests for app pods.
          postgres_limits_memory (str) = "60Gi":  Memory limits for postgres
            pod.
          postgres_limits_cpu (str) = "12000m":  CPU limits for postgres pod.
          postgres_requests_memory (str) = "20Mi":  Memory request for postgres
            pod.
          postgres_requests_cpu (str) = "1m":  CPU request for postgres pod.
          disk_size (str): Disk size (ex.: 50Gi, 100Gi)
          disk_name (str): Name of the disk that will be used in postgres.
          workers_timeout (str): Time to workout time for guicorn workers.
          n_chunks (str) = 5: n chunks working o data loader.
          chunk_size (str) = 5000: Size of the datalake chunks.
          repository (str) = "gcr.io/repositorio-geral-170012": Repository to
            pull Image
          test_db_version (str): Set a test database with version.
          test_db_repository (str): Define a repository for the test
            database.
          db_username (str): Database connection username.
          db_host (str): Database connection host.
          db_port (str): Database connection port.
          db_database (str): Database connection database.

        Returns:
          PumpWoodDatalakeMicroservice: New Object

        Raises:
          No especific raises.
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

        self.debug = debug
        self.app_replicas = app_replicas
        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)
        self.workers_timeout = workers_timeout

        # App
        self.repository = repository
        self.version_app = version_app
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Database
        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database
        self.postgres_limits_memory = postgres_limits_memory
        self.postgres_limits_cpu = postgres_limits_cpu
        self.postgres_requests_memory = postgres_requests_memory
        self.postgres_requests_cpu = postgres_requests_cpu
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self, kube_client):
        """
        create_deployment_file.

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
                volume_claim_name="postgres-pumpwood-decision")
            deployment_postgres_text_f = deployment_postgres.format(
                requests_memory=self.postgres_requests_memory,
                requests_cpu=self.postgres_requests_cpu,
                limits_memory=self.postgres_limits_memory,
                limits_cpu=self.postgres_limits_cpu)

        deployment_text_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.version_app,
                bucket_name=self.bucket_name,
                workers_timeout=self.workers_timeout,
                debug=self.debug,
                replicas=self.app_replicas,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database,
                requests_memory=self.app_limits_memory,
                requests_cpu=self.app_limits_cpu,
                limits_memory=self.app_requests_memory,
                limits_cpu=self.app_requests_cpu)

        list_return = [{
            'type': 'secrets',
            'name': 'pumpwood_decision__secrets',
            'content': secrets_text_formated, 'sleep': 5}]
        if volume_postgres_text_f is not None:
            list_return.append({
                'type': 'volume', 'name': 'pumpwood_decision__volume',
                'content': volume_postgres_text_f, 'sleep': 10})
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy',
                'name': 'pumpwood_decision__postgres',
                'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_decision__deploy',
            'content': deployment_text_frmtd, 'sleep': 0})

        if self.firewall_ips is not None and \
           self.postgres_public_ip is not None:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'pumpwood_decision__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})
        return list_return


class PumpwoodDecisionModel:
    """Class to help deployment of Decision models."""

    def __init__(self,
                 decision_model_name: str,
                 version: str,
                 bucket_name: str,
                 repository: str,
                 limits_memory: str = "60Gi",
                 limits_cpu: str = "12000m",
                 requests_memory: str = "20Mi",
                 requests_cpu: str = "1m"):
        """
        __init__.

        Args:
            decision_model_name (str): Name of the decision model.
            version (str): Model version.
            version (str): Version of the model.
            repository (str): Repository path.
        Kwargs:
            limits_memory: str = "60Gi"
            limits_cpu: str = "12000m"
            requests_memory: str = "20Mi"
            requests_cpu: str = "1m"
        """
        self.base_path = os.path.dirname(__file__)
        self.decision_model_name = decision_model_name
        self.repository = repository
        self.version = version
        self.bucket_name = bucket_name
        self.limits_memory = limits_memory
        self.limits_cpu = limits_cpu
        self.requests_memory = requests_memory
        self.requests_cpu = requests_cpu

    def create_deployment_file(self, kube_client):
        """Create Google Trends deployment files."""
        decision_model_frmted = decision_model_yml.format(
            decision_model_name=self.decision_model_name,
            repository=self.repository,
            bucket_name=self.bucket_name,
            version=self.version,
            limits_memory=self.limits_memory,
            limits_cpu=self.limits_cpu,
            requests_memory=self.requests_memory,
            requests_cpu=self.requests_cpu)

        return [{
                'type': 'deploy',
                'name': 'decision_model__{}__worker'.format(
                    self.decision_model_name),
                'content': decision_model_frmted, 'sleep': 0}]
