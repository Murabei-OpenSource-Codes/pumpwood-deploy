"""PumpWood Auth Module."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from .resources.yml__resources import (
    auth_admin_static, app_deployment, deployment_postgres, secrets,
    services__load_balancer, test_postgres)


class PumpWoodAuthMicroservice:
    """PumpWoodAuthMicroservice."""

    def __init__(self,
                 secret_key: str,
                 db_password: str,
                 microservice_password: str,
                 email_host_user: str,
                 email_host_password: str,
                 bucket_name: str,
                 app_version: str,
                 static_version: str,
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 disk_size: str = None,
                 disk_name: str = None,
                 postgres_limits_memory: str = "60Gi",
                 postgres_limits_cpu: str = "12000m",
                 postgres_requests_memory: str = "20Mi",
                 postgres_requests_cpu: str = "1m",
                 postgres_public_ip: str = None,
                 firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 db_username: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-auth",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 app_image: str = "pumpwood-auth-app",
                 static_image: str = "pumpwood-auth-static"):
        """Deploy PumpWood Auth Microservice.

        Args:
            secret_key (str): Hash salt.
            db_password (str): Auth DB password.
            email_host_user (str): Auth email conection username.
            email_host_password (str): Auth email conection password.
            app_version (str): Version of the auth microservice.
            static_version (str): Version of the static image.

        Kwargs:
            app_limits_memory (str): str = "60Gi"
            app_limits_cpu (str): str = "12000m"
            app_requests_memory (str): str = "20Mi"
            app_requests_cpu (str): str = "1m"
            disk_size (str): Disk size for auth database.
            disk_name (str): Disk name for auth database.
            postgres_limits_memory: str = "60Gi"
            postgres_limits_cpu: str = "12000m"
            postgres_requests_memory: str = "20Mi"
            postgres_requests_cpu: str = "1m"
            firewall_ips (str): Firewall alowed conection ips for database.
            repository (str): Repository to pull image from.
            replicas (int): Number of replicas in App deployment.
            test_db_version (str): Set a test database with version.
            test_db_repository (str): Define a repository for the test
              database.
            debug (str): Set app in debug mode.
            db_username (str): Database connection username.
            db_host (str): Database connection host.
            db_port (str): Database connection port.
            db_database (str): Database connection database.
            postgres_public_ip (str): Postgres database external IP.
        """
        disk_deploy = (disk_name is not None and disk_size is not None)
        if disk_deploy and test_db_version is not None:
            raise Exception(
                "When working with test database, disk is not used.")

        postgres_certificates = create_ssl_key_ssl_crt()
        self._secret_key = base64.b64encode(secret_key.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        self._email_host_user = base64.b64encode(
            email_host_user.encode()).decode()
        self._email_host_password = base64.b64encode(
            email_host_password.encode()).decode()

        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()

        self.postgres_public_ip = postgres_public_ip
        self.firewall_ips = firewall_ips

        self.disk_size = disk_size
        self.disk_name = disk_name
        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)

        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database

        # App
        self.repository = (
            repository + "/"
            if repository is not None else "")
        self.app_image = app_image
        self.app_version = app_version

        self.static_image = static_image
        self.static_version = static_version

        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Postgres
        self.postgres_limits_memory = postgres_limits_memory
        self.postgres_limits_cpu = postgres_limits_cpu
        self.postgres_requests_memory = postgres_requests_memory
        self.postgres_requests_cpu = postgres_requests_cpu
        self.test_db_version = test_db_version
        self.test_db_repository = (
            test_db_repository + "/"
            if test_db_repository is not None else "")

    def create_deployment_file(self, kube_client):
        """
        Create_deployment_file.

        Args:
          kube_client: Client to communicate with Kubernets cluster.
        """
        secrets_text_f = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            email_host_user=self._email_host_user,
            email_host_password=self._email_host_password,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt,
            secret_key=self._secret_key)

        deployment_auth_app_text_f = app_deployment.format(
            repository=self.repository,
            version=self.app_version,
            bucket_name=self.bucket_name,
            replicas=self.app_replicas,
            debug=self.app_debug,
            n_workers=self.app_workers,
            workers_timeout=self.app_timeout,

            # DB Config
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,

            # Resources
            requests_memory=self.app_requests_memory,
            requests_cpu=self.app_requests_cpu,
            limits_memory=self.app_limits_memory,
            limits_cpu=self.app_limits_cpu,
            app_image=self.app_image)

        deployment_auth_admin_static_f = \
            auth_admin_static.format(
                repository=self.repository,
                version=self.static_version,
                static_image=self.static_image)

        volume_postgres_text_f = None
        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version,
                # Resources
                requests_memory=self.postgres_requests_memory,
                requests_cpu=self.postgres_requests_cpu,
                limits_memory=self.postgres_limits_memory,
                limits_cpu=self.postgres_limits_cpu)
        elif self.disk_size is not None:
            volume_postgres_text_f = kube_client.create_volume_yml(
                disk_name=self.disk_name, disk_size=self.disk_size,
                volume_claim_name="postgres-pumpwood-auth")
            deployment_postgres_text_f = deployment_postgres.format(
                requests_memory=self.postgres_requests_memory,
                requests_cpu=self.postgres_requests_cpu,
                limits_memory=self.postgres_limits_memory,
                limits_cpu=self.postgres_limits_cpu)

        list_return = [{
            'type': 'secrets', 'name': 'pumpwood_auth__secrets',
            'content': secrets_text_f, 'sleep': 5}]
        if volume_postgres_text_f is not None:
            list_return.append({
                'type': 'volume', 'name': 'pumpwood_auth__volume',
                'content': volume_postgres_text_f, 'sleep': 10})
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_auth__postgres',
                'content': deployment_postgres_text_f, 'sleep': 20})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_auth_app__deploy',
            'content': deployment_auth_app_text_f, 'sleep': 10})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_auth_admin_static__deploy',
            'content': deployment_auth_admin_static_f, 'sleep': 10})

        if self.firewall_ips is not None and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)

            list_return.append({
                'type': 'services',
                'name': 'pumpwood_auth__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})

        return list_return

    def end_points(self):
        """end_points."""
        return self.end_points
