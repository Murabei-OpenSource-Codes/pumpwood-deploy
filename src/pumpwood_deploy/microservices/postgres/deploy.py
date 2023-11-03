"""Deploy Postgres."""
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from pumpwood_deploy.microservices.postgres.resources.yml__resources import (
    deployment_postgres, secrets)


class PostgresDatabase:
    """PumpWoodAuthMicroservice."""

    def __init__(self,
                 db_password: str,
                 name: str,
                 disk_size: str = None,
                 disk_name: str = None,
                 postgres_limits_memory: str = "60Gi",
                 postgres_limits_cpu: str = "12000m",
                 postgres_requests_memory: str = "20Mi",
                 postgres_requests_cpu: str = "1m",
                 postgres_public_ip: str = None,
                 firewall_ips: list = None):
        """
        Deploy a postgres server not associated with other microservices.

        Username is "pumpwood" and password is set as parameter.

        Args:
            db_password [str]: Database password.
            disk_size [str]: Size of the disk to be claimed.
            disk_name [str]: Disk name.
            name [str]: Service name to route calls to database.
        Kwargs:
            postgres_limits_memory [str] = "60Gi": Postgres container memory
                limit.
            postgres_limits_cpu [str] = "12000m": Postgres cotainer CPU
                limit.
            postgres_requests_memory [str] = "20Mi":
            postgres_requests_cpu [str] = "1m":
            postgres_public_ip [str] = None:
            firewall_ips [lis]t = None):
        """
        postgres_certificates = create_ssl_key_ssl_crt()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()

        self.name = name
        self.postgres_public_ip = postgres_public_ip
        self.firewall_ips = firewall_ips
        self.disk_size = disk_size
        self.disk_name = disk_name

        # App
        # Postgres
        self.postgres_limits_memory = postgres_limits_memory
        self.postgres_limits_cpu = postgres_limits_cpu
        self.postgres_requests_memory = postgres_requests_memory
        self.postgres_requests_cpu = postgres_requests_cpu

    def create_deployment_file(self, kube_client):
        """
        Create_deployment_file.

        Args:
          kube_client: Client to communicate with Kubernets cluster.
        """
        secrets_text_f = secrets.format(
            name=self.name, db_password=self._db_password,
            ssl_key=self._ssl_key, ssl_crt=self._ssl_crt)

        volume_claim_name = "postgres-sole-{name}-data".format(name=self.name)
        volume_postgres_text_f = kube_client.create_volume_yml(
            disk_name=self.disk_name, disk_size=self.disk_size,
            volume_claim_name=volume_claim_name)
        deployment_postgres_text_f = deployment_postgres.format(
            volume_claim_name=volume_claim_name,
            name=self.name,
            requests_memory=self.postgres_requests_memory,
            requests_cpu=self.postgres_requests_cpu,
            limits_memory=self.postgres_limits_memory,
            limits_cpu=self.postgres_limits_cpu)

        list_return = [
            {'type': 'secrets',
             'name': 'postgres_sole__{name}__secrets'.format(name=self.name),
             'content': secrets_text_f, 'sleep': 5},
            {'type': 'volume',
             'name': 'postgres_sole__{name}__volume'.format(name=self.name),
             'content': volume_postgres_text_f, 'sleep': 10},
            {'type': 'deploy',
             'name': 'postgres_sole__{name}__postgres'.format(name=self.name),
             'content': deployment_postgres_text_f, 'sleep': 20}]
        return list_return
