"""PumpWood DataLake Microservice Deploy."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from .resources.yml__resources import (
    app_deployment, deployment_postgres, secrets, services__load_balancer,
    volume_postgres, test_postgres, decision_model_yml)


class PumpWoodDescisionMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self, db_password: str, microservice_password: str,
                 bucket_name: str, version_app: str,
                 disk_name: str = None, disk_size: str = None,
                 postgres_public_ip: str = None, firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 replicas: int = 1,
                 workers_timeout: int = 300,
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 debug: str = "FALSE"):
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
          disk_size (str): Disk size (ex.: 50Gi, 100Gi)
          disk_name (str): Name of the disk that will be used in postgres
          replicas (int) = 1: Number of replicas in app deployment.
          workers_timeout (str): Time to workout time for guicorn workers.
          n_chunks (str) = 5: n chunks working o data loader.
          chunk_size (str) = 5000: Size of the datalake chunks.
          repository (str) = "gcr.io/repositorio-geral-170012": Repository to
            pull Image
          test_db_version (str): Set a test database with version.
          test_db_repository (str): Define a repository for the test
            database.
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
        self.replicas = replicas
        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)
        self.workers_timeout = workers_timeout
        self.repository = repository

        self.version_app = version_app

        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self):
        """create_deployment_file."""
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt)
        volume_postgres_text_formated = volume_postgres.format(
            disk_size=self.disk_size, disk_name=self.disk_name)

        volume_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)
        else:
            volume_postgres_text_f = volume_postgres.format(
                disk_size=self.disk_size,
                disk_name=self.disk_name)
            deployment_postgres_text_f = deployment_postgres

        deployment_text_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.version_app,
                bucket_name=self.bucket_name,
                workers_timeout=self.workers_timeout,
                debug=self.debug,
                replicas=self.replicas)

        if volume_postgres_text_f is not None:
            list_return = [
                {'type': 'volume', 'name': 'pumpwood_decision__volume',
                 'content': volume_postgres_text_formated, 'sleep': 10}]
        else:
            list_return = []

        list_return.extend([
            {'type': 'secrets',
             'name': 'pumpwood_decision__secrets',
             'content': secrets_text_formated, 'sleep': 5},

            {'type': 'deploy',
             'name': 'pumpwood_decision__postgres',
             'content': deployment_postgres_text_f, 'sleep': 0},

            {'type': 'deploy', 'name': 'pumpwood_decision__deploy',
             'content': deployment_text_frmtd, 'sleep': 0},
        ])

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

    def __init__(self, decision_model_name: str, version: str,
                 bucket_name: str, repository: str):
        """
        __init__.

        Args:
            decision_model_name (str): Name of the decision model.
            version (str): Model version.
            version (str): Version of the model.
            repository (str): Repository path.
        """
        self.base_path = os.path.dirname(__file__)
        self.decision_model_name = decision_model_name
        self.repository = repository
        self.version = version
        self.bucket_name = bucket_name

    def create_deployment_file(self):
        """Create Google Trends deployment files."""
        decision_model_frmted = decision_model_yml.format(
            decision_model_name=self.decision_model_name,
            repository=self.repository,
            bucket_name=self.bucket_name,
            version=self.version)

        return [{
                'type': 'deploy',
                'name': 'decision_model__{}__worker'.format(
                    self.decision_model_name),
                'content': decision_model_frmted, 'sleep': 0}]

    def end_points(self):
        """Return microservices end-points."""
        return self.end_points
