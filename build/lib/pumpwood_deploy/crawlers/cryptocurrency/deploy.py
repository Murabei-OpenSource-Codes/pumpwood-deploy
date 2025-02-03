"""Crawler for CryptoCurrency."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from pumpwood_deploy.crawlers.cryptocurrency.resources.yml__resources import (
    app_deployment, worker_candle_deployment,
    worker_balance_deployment, worker_order_deployment,
    deployment_postgres, secrets, services__load_balancer)


class CrawlerCryptoCurrency:
    """CrawlerCryptoCurrency."""

    def __init__(self,
                 db_password: str,
                 microservice_password: str,
                 bitfinex_api_key: str,
                 bitfinex_api_secret: str,
                 disk_size: str,
                 disk_name: str,
                 bucket_name: str,
                 app_version: str,
                 worker_candle_version: str,
                 worker_balance_version: str,
                 worker_order_version: str,
                 postgres_public_ip: str = None,
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_debug: str = "FALSE",
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 candle_limits_memory: str = "60Gi",
                 candle_limits_cpu: str = "12000m",
                 candle_requests_memory: str = "20Mi",
                 candle_requests_cpu: str = "1m",
                 balance_limits_memory: str = "60Gi",
                 balance_limits_cpu: str = "12000m",
                 balance_requests_memory: str = "20Mi",
                 balance_requests_cpu: str = "1m",
                 order_limits_memory: str = "60Gi",
                 order_limits_cpu: str = "12000m",
                 order_requests_memory: str = "20Mi",
                 order_requests_cpu: str = "1m",
                 postgres_limits_memory: str = "60Gi",
                 postgres_limits_cpu: str = "12000m",
                 postgres_requests_memory: str = "20Mi",
                 postgres_requests_cpu: str = "1m",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-crawler-cryptocurrency",
                 db_port: str = "5432",
                 db_database: str = "pumpwood"):
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
            app_version (str): Verison of the App image
            worker_candle_version (str): Version of the worker for candle data.
            worker_balance_version (str): Version of the worker for portfolio
                balance data.
            worker_order_version (str): Version of the worker for place
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
        self.repository = repository

        # App
        self.app_version = app_version
        self.app_replicas = app_replicas
        self.app_debug = app_debug
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Candle worker
        self.worker_candle_version = worker_candle_version
        self.candle_limits_memory = candle_limits_memory
        self.candle_limits_cpu = candle_limits_cpu
        self.candle_requests_memory = candle_requests_memory
        self.candle_requests_cpu = candle_requests_cpu

        # Balance worker
        self.worker_balance_version = worker_balance_version
        self.balance_limits_memory = balance_limits_memory
        self.balance_limits_cpu = balance_limits_cpu
        self.balance_requests_memory = balance_requests_memory
        self.balance_requests_cpu = balance_requests_cpu

        # Order worker
        self.worker_order_version = worker_order_version
        self.order_limits_memory = order_limits_memory
        self.order_limits_cpu = order_limits_cpu
        self.order_requests_memory = order_requests_memory
        self.order_requests_cpu = order_requests_cpu

        # Postgres
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
        """create_deployment_file."""
        # Secrets
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            bitfinex_api_key=self._bitfinex_api_key,
            bitfinex_api_secret=self._bitfinex_api_secret,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt)

        # Postgres
        volume_postgres_text_f = None
        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            # deployment_postgres_text_f = test_postgres.format(
            #     repository=self.test_db_repository,
            #     version=self.test_db_version,
            #     requests_memory=self.postgres_requests_memory,
            #     requests_cpu=self.postgres_requests_cpu,
            #     limits_memory=self.postgres_limits_memory,
            #     limits_cpu=self.postgres_limits_cpu)
            raise Exception("Test database not implemented")
        elif self.disk_size is not None:
            volume_postgres_text_f = kube_client.create_volume_yml(
                disk_name=self.disk_name,
                disk_size=self.disk_size,
                volume_claim_name="postgres-crawler-cryptocurrency")
            deployment_postgres_text_f = deployment_postgres.format(
                requests_memory=self.postgres_requests_memory,
                requests_cpu=self.postgres_requests_cpu,
                limits_memory=self.postgres_limits_memory,
                limits_cpu=self.postgres_limits_cpu)

        deployment_text_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.app_version,
                bucket_name=self.bucket_name,
                workers_timeout=self.app_timeout,
                debug=self.app_debug,
                replicas=self.app_replicas,
                n_workers=self.app_workers,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database,
                requests_memory=self.app_requests_memory,
                requests_cpu=self.app_requests_cpu,
                limits_memory=self.app_limits_memory,
                limits_cpu=self.app_limits_cpu)

        # Worker
        worker_candle_deployment_frmted = worker_candle_deployment.format(
            repository=self.repository,
            version=self.worker_candle_version,
            bucket_name=self.bucket_name,
            requests_memory=self.candle_requests_memory,
            requests_cpu=self.candle_requests_cpu,
            limits_memory=self.candle_limits_memory,
            limits_cpu=self.candle_limits_cpu)
        worker_balance_deployment_frmted = worker_balance_deployment.format(
            repository=self.repository,
            version=self.worker_balance_version,
            bucket_name=self.bucket_name,
            requests_memory=self.balance_requests_memory,
            requests_cpu=self.balance_requests_cpu,
            limits_memory=self.balance_limits_memory,
            limits_cpu=self.balance_limits_cpu)
        worker_order_deployment_frmted = worker_order_deployment.format(
            repository=self.repository,
            version=self.worker_order_version,
            bucket_name=self.bucket_name,
            requests_memory=self.order_requests_memory,
            requests_cpu=self.order_requests_cpu,
            limits_memory=self.order_limits_memory,
            limits_cpu=self.order_limits_cpu)

        list_return = [{
            'type': 'secrets',
            'name': 'crawler_cryptocurrency__secrets',
            'content': secrets_text_formated, 'sleep': 5}]
        if volume_postgres_text_f is not None:
            list_return.append({
                'type': 'volume', 'name': 'crawler_cryptocurrency__volume',
                'content': volume_postgres_text_f, 'sleep': 10})
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy',
                'name': 'crawler_cryptocurrency__postgres',
                'content': deployment_postgres_text_f, 'sleep': 0})

        list_return.append({
            'type': 'deploy', 'name': 'crawler_cryptocurrency__app',
            'content': deployment_text_frmtd, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'crawler_cryptocurrency__worker_candle',
            'content': worker_candle_deployment_frmted, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'crawler_cryptocurrency__worker_balance',
            'content': worker_balance_deployment_frmted, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'crawler_cryptocurrency__worker_order',
            'content': worker_order_deployment_frmted, 'sleep': 0})

        if self.firewall_ips is not None and \
           self.postgres_public_ip is not None:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'crawler_cryptocurrency__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})
        return list_return
