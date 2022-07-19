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

    def __init__(self, secret_key: str, db_password: str,
                 microservice_password: str,
                 email_host_user: str, email_host_password: str,
                 bucket_name: str, version_app: str,  version_static: str,
                 disk_size: str = None, disk_name: str = None,
                 postgres_public_ip: str = None, firewall_ips: list = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 replicas: int = 1, test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 debug: str = "FALSE"):
        """Deploy PumpWood Auth Microservice.

        Args:
            secret_key (str): Hash salt.
            db_password (str): Auth DB password.
            email_host_user (str): Auth email conection username.
            email_host_password (str): Auth email conection password.
            disk_size (str): Disk size for auth database.
            disk_name (str): Disk name for auth database.
            postgres_public_ip (str): Postgres database external IP.
            version_app (str): Version of the auth microservice.
            version_static (str): Version of the static image.
        Kwargs:
            firewall_ips (str): Firewall alowed conection ips for database.
            repository (str): Repository to pull image from.
            replicas (int): Number of replicas in App deployment.
            test_db_version (str): Set a test database with version.
            test_db_repository (str): Define a repository for the test
              database.
            debug (str): Set app in debug mode.
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
        self.debug = debug

        self.disk_size = disk_size
        self.disk_name = disk_name
        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)

        self.repository = repository
        self.version_app = version_app
        self.version_static = version_static
        self.replicas = replicas

        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

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
              version=self.version_app,
              bucket_name=self.bucket_name,
              replicas=self.replicas,
              debug=self.debug)
        deployment_auth_admin_static_f = \
            auth_admin_static.format(
                repository=self.repository,
                version=self.version_static)

        volume_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)
        else:
            volume_postgres_text_f = kube_client.create_volume_yml(
                disk_name=self.disk_size,
                disk_size=self.disk_name,
                volume_claim_name="postgres-pumpwood-auth")
            deployment_postgres_text_f = deployment_postgres

        if volume_postgres_text_f is not None:
            list_return = [
                {'type': 'volume', 'name': 'pumpwood_auth__volume',
                 'content': volume_postgres_text_f, 'sleep': 10}]
        else:
            list_return = []

        list_return.extend([
            {'type': 'secrets', 'name': 'pumpwood_auth__secrets',
             'content': secrets_text_f, 'sleep': 5},

            {'type': 'deploy', 'name': 'pumpwood_auth__postgres',
             'content': deployment_postgres_text_f, 'sleep': 20},
            {'type': 'deploy', 'name': 'pumpwood_auth_app__deploy',
             'content': deployment_auth_app_text_f, 'sleep': 10},
            {'type': 'deploy', 'name': 'pumpwood_auth_admin_static__deploy',
             'content': deployment_auth_admin_static_f, 'sleep': 10}])

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
