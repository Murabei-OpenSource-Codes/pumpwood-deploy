"""Crawler for CryptoCurrency."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from .resources.yml__resources import (
    app_deployment, worker_candle_deployment,
    worker_balance_deployment, worker_order_deployment,
    deployment_postgres, secrets, services__load_balancer,
    volume_postgres)


class CrawlerCriptoCurrency:
    """CrawlerCriptoCurrency."""

    def __init__(self, db_password: str, microservice_password: str,
                 bitfinex_api_key: str, bitfinex_api_secret: str,
                 disk_size: str, disk_name: str,
                 bucket_name: str, version_app: str,
                 version_worker_candle: str, version_worker_balance: str,
                 version_worker_order: str, postgres_public_ip: str = None,
                 firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 workers_timeout: int = 300, replicas: int = 1):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            microservice_password(str): Microservice password.
            bitfinex_api_key (str): Bitfinex API Key.
            bitfinex_api_secret (str): Bitfinex API Secrets.
            disk_size (str): Disk size (ex.: 50Gi, 100Gi)
            disk_name (str): Name of the disk that will be used in postgres
            bucket_name (str): Name of the bucket (Storage)
            version_app (str): Verison of the App image
            version_worker_candle (str): Version of the worker for candle data.
            version_worker_balance (str): Version of the worker for portfolio
                balance data.
            version_worker_order (str): Version of the worker for place
                orders in exchange.
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
        self._bitfinex_api_key = base64.b64encode(
            bitfinex_api_key.encode()).decode()
        self._bitfinex_api_secret = base64.b64encode(
            bitfinex_api_secret.encode()).decode()

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
        self.version_worker_candle = version_worker_candle
        self.version_worker_balance = version_worker_balance
        self.version_worker_order = version_worker_order
        self.replicas = replicas

    def create_deployment_file(self):
        """create_deployment_file."""
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            bitfinex_api_key=self._bitfinex_api_key,
            bitfinex_api_secret=self._bitfinex_api_secret,
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
                workers_timeout=self.workers_timeout,
                replicas=self.replicas)

        worker_candle_deployment_frmted = worker_candle_deployment.format(
            repository=self.repository, version=self.version_worker_candle,
            bucket_name=self.bucket_name)
        worker_balance_deployment_frmted = worker_balance_deployment.format(
            repository=self.repository, version=self.version_worker_balance,
            bucket_name=self.bucket_name)
        worker_order_deployment_frmted = worker_order_deployment.format(
            repository=self.repository, version=self.version_worker_order,
            bucket_name=self.bucket_name)

        list_return = [
            {'type': 'secrets', 'name': 'crawler_criptocurrency__secrets',
             'content': secrets_text_formated, 'sleep': 5},

            {'type': 'volume', 'name': 'crawler_criptocurrency__volume',
             'content': volume_postgres_text_formated, 'sleep': 10},

            {'type': 'deploy', 'name': 'crawler_criptocurrency__postgres',
             'content': deployment_postgres_text_formated, 'sleep': 0},

            {'type': 'deploy', 'name': 'crawler_criptocurrency__deploy',
             'content': deployment_queue_manager_text_frmtd, 'sleep': 0},

            {'type': 'deploy',
             'name': 'crawler_criptocurrency__worker_candle',
             'content': worker_candle_deployment_frmted, 'sleep': 0},

            {'type': 'deploy',
             'name': 'crawler_criptocurrency__worker_balance',
             'content': worker_balance_deployment_frmted, 'sleep': 0},

            {'type': 'deploy',
             'name': 'crawler_criptocurrency__worker_order',
             'content': worker_order_deployment_frmted, 'sleep': 0},
        ]

        if self.firewall_ips is not None and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'crawler_criptocurrency__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})

        return list_return
