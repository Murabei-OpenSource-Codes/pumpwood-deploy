"""PumpWood DataLake Microservice Deploy."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from pumpwood_deploy.metabase.resources.yml__resources import (
    app_deployment, secrets, services__load_balancer, deployment_postgres,
    test_postgres, config_map)


class MetabaseMicroservice:
    """Deploy Metabase as microservice."""

    def __init__(self, metabase_site_url: str, db_password: str,
                 embedding_secret_key: str, encryption_secret_key: str,
                 db_host: str = "postgres-pumpwood-metabase",
                 disk_name: str = None,
                 disk_size: str = None,
                 app_replicas: int = 1,
                 app_limits_memory: str = "6Gi",
                 app_limits_cpu: str = "2000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 postgres_limits_memory: str = "6Gi",
                 postgres_limits_cpu: str = "2000m",
                 postgres_requests_memory: str = "20Mi",
                 postgres_requests_cpu: str = "1m",
                 postgres_public_ip: str = None,
                 firewall_ips: list = None,
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012"):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            metabase_site_url (str): Site url to be used in dashboard
                embedding.
            embedding_secret_key (str): Secret to be used to embedding
                graphs using metabase.
            encryption_secret_key (str): Secret key for Metabase internal
                encription.
        Kwargs:
            db_host (str): Host to connect to postgres database for metabase.
            disk_name (str): Disk name to store metabase information,
            disk_size (str): Disk size to store metabase information,
            postgres_limits_memory (str): Memory limit for postgres.
            postgres_limits_cpu (str): CPU limit for postgres.
            postgres_requests_memory (str): Memory request for postgres.
            postgres_requests_cpu (str): CPU request for postgres.
            postgres_public_ip (str): Public Ip associated with Postgres.
            firewall_ips (list): Firewall used to limit IPs to connect to
                database.
            test_db_version (str): Set a test database with version.
            test_db_repository (str): Define a repository for the test
              database.
        Returns:
          MetabaseMicroservice: New Object
        Raises:
          No especific raises.
        Example:
          No example yet.
        """
        postgres_certificates = create_ssl_key_ssl_crt()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()
        self.base_path = os.path.dirname(__file__)

        # Metabase App
        self.app_replicas = app_replicas
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu
        self.metabase_site_url = metabase_site_url
        self.embedding_secret_key = base64.b64encode(
            embedding_secret_key.encode()).decode()
        self.encryption_secret_key = base64.b64encode(
            encryption_secret_key.encode()).decode()

        # Postgres information
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.postgres_public_ip = postgres_public_ip
        self.postgres_limits_memory = postgres_limits_memory
        self.postgres_limits_cpu = postgres_limits_cpu
        self.postgres_requests_memory = postgres_requests_memory
        self.postgres_requests_cpu = postgres_requests_cpu
        self.postgres_public_ip = postgres_public_ip
        self.firewall_ips = firewall_ips
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self, kube_client):
        """create_deployment_file."""
        # General secrets
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            embedding_secret_key=self.embedding_secret_key,
            encryption_secret_key=self.encryption_secret_key,
            ssl_key=self._ssl_key, ssl_crt=self._ssl_crt)

        # Deployments
        app_deployment__frmt = app_deployment.format(
            replicas=self.app_replicas,
            limits_memory=self.app_limits_memory,
            limits_cpu=self.app_limits_cpu,
            requests_memory=self.app_requests_memory,
            requests_cpu=self.app_requests_cpu)
        config_map__frmt = config_map.format(
            site_url=self.metabase_site_url)

        # Postgres
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
                disk_name=self.disk_name, disk_size=self.disk_size,
                volume_claim_name="postgres-metabase")
            deployment_postgres_text_f = deployment_postgres.format(
                requests_memory=self.postgres_requests_memory,
                requests_cpu=self.postgres_requests_cpu,
                limits_memory=self.postgres_limits_memory,
                limits_cpu=self.postgres_limits_cpu)

        list_return = [{
            'type': 'secrets', 'name': 'metabase__secrets',
            'content': secrets_text_formated, 'sleep': 5}, {
            'type': 'secrets', 'name': 'metabase__config_map',
            'content': config_map__frmt, 'sleep': 5}]
        if volume_postgres_text_f is not None:
            list_return.append({
                'type': 'volume', 'name': 'metabase__volume',
                'content': volume_postgres_text_f, 'sleep': 10})
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy', 'name': 'metabase__postgres',
                'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'metabase__deploy',
            'content': app_deployment__frmt, 'sleep': 0})

        if self.firewall_ips is not None and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'metabase__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})

        return list_return
