"""Crawler for CryptoCurrency."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from .resources.yml__resources import (
    app_deployment, worker_deployment, deployment_postgres,
    secrets, services__load_balancer,
    volume_postgres)


class CryptoCurrencyCrawler:
    """CryptoCurrencyCrawler."""

    def __init__(self, db_password: str, microservice_password: str,
                 disk_size: str, disk_name: str,
                 bucket_name: str,
                 version_app: str, version_worker: str,
                 postgres_public_ip: str = None, firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 workers_timeout: int = 300):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            microservice_password(str): Microservice password.
            disk_size (str): Disk size (ex.: 50Gi, 100Gi)
            disk_name (str): Name of the disk that will be used in postgres
            bucket_name (str): Name of the bucket (Storage)
            version_app (str): Verison of the App image
            version_worker (str): Version of the Worker image.
        Kwargs:
            repository (str): Repository to pull Image
            postgres_public_ip (str): Postgres public IP.
            firewall_ips (list): List the IPs allowed to connect to datalake.
            workers_timeout (str): Time to workout time for guicorn workers.
        Returns:
          PumpWoodETLMicroservice: New Object

        Raises:
          No especific raises.

        Example:
          No example yet.

        """
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

        self.workers_timeout = workers_timeout
        self.repository = repository
        self.version_app = version_app
        self.version_worker = version_worker

    def create_deployment_file(self):
        """create_deployment_file."""
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt)
        volume_postgres_text_formated = volume_postgres.format(
            disk_size=self.disk_size, disk_name=self.disk_name)

        deployment_postgres_text_formated = deployment_postgres

        deployment_queue_manager_text_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.version_app,
                bucket_name=self.bucket_name,
                workers_timeout=self.workers_timeout)

        worker_deployment_text_frmted = worker_deployment.format(
            repository=self.repository, version=self.version_worker,
            bucket_name=self.bucket_name)

        list_return = [
            {'type': 'secrets', 'name': 'crawlercryptocurrency__secrets',
             'content': secrets_text_formated, 'sleep': 5},

            {'type': 'volume', 'name': 'crawlercryptocurrency__volume',
             'content': volume_postgres_text_formated, 'sleep': 10},

            {'type': 'deploy', 'name': 'crawlercryptocurrency__postgres',
             'content': deployment_postgres_text_formated, 'sleep': 0},

            {'type': 'deploy', 'name': 'crawlercryptocurrency__deploy',
             'content': deployment_queue_manager_text_frmtd, 'sleep': 0},

            {'type': 'deploy', 'name': 'crawlercryptocurrency__worker',
             'content': worker_deployment_text_frmted, 'sleep': 0},
        ]

        if self.firewall_ips is not None and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'crawlercryptocurrency__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})

        return list_return
