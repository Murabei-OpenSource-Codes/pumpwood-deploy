"""Deploy Postgres."""
import base64
import pkg_resources
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt


pgbouncer_deploy = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/postgres/'
    'resources/deploy__pgbouncer.yml').read().decode()
deployment_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/postgres/'
    'resources/deploy__postgres.yml').read().decode()
secrets_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/postgres/'
    'resources/secrets.yml').read().decode()


class PostgresDatabase:
    """Class to help deployment of Postgres database on cluster."""

    def __init__(self,
                 db_username: str,
                 db_password: str,
                 name: str,
                 disk_size: str = None,
                 disk_name: str = None,
                 postgres_limits_memory: str = "60Gi",
                 postgres_limits_cpu: str = "12000m",
                 postgres_requests_memory: str = "20Mi",
                 postgres_requests_cpu: str = "1m",
                 postgres_public_ip: str = None,
                 firewall_ips: list = None,
                 image: str = 'postgis/postgis:15-3.3-alpine'):
        """Deploy a postgres server not associated with other microservices.

        Username is "pumpwood" and password is set as parameter.

        Args:
            db_username (str):
                Database username.
            db_password (str):
                Database password.
            disk_size (str):
                Size of the disk to be claimed.
            disk_name (str):
                Disk name.
            name (str):
                Service name to route calls to database.
            postgres_limits_memory (str):
                Postgres container memory limit.
            postgres_limits_cpu (str):
                Postgres cotainer CPU limit.
            postgres_requests_memory (str):
                Request of memory by container.
            postgres_requests_cpu (str):
                Request of CPU by container.
            postgres_public_ip (str):
                Postgres public IP (in case of exposing the database)
                to outside of the cluster, not recomended.
            firewall_ips (list):
                List of the IPs that will be used to restric incoming calls
                to database.
            image (str):
                Image used on deploy.
        """
        postgres_certificates = create_ssl_key_ssl_crt()
        self._db_username = base64.b64encode(db_username.encode()).decode()
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
        self.image = image

    def create_deployment_file(self, kube_client):
        """Create_deployment_file.

        Args:
          kube_client:
            Client to communicate with Kubernets cluster.
        """
        secrets_text_f = secrets_postgres.format(
            name=self.name, db_username=self._db_username,
            db_password=self._db_password, ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt)

        volume_claim_name = "{name}-data".format(name=self.name)
        volume_postgres_text_f = kube_client.create_volume_yml(
            disk_name=self.disk_name, disk_size=self.disk_size,
            volume_claim_name=volume_claim_name)
        deployment_postgres_text_f = deployment_postgres.format(
            volume_claim_name=volume_claim_name,
            name=self.name,
            requests_memory=self.postgres_requests_memory,
            requests_cpu=self.postgres_requests_cpu,
            limits_memory=self.postgres_limits_memory,
            limits_cpu=self.postgres_limits_cpu,
            image=self.image)

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


class PGBouncerDatabase:
    """PumpWoodAuthMicroservice."""

    def __init__(self, name: str, postgres_secret: str,
                 postgres_database: str, postgres_host: str,
                 postgres_port: str = "5432",
                 version: str = '1.15.0-1-20251130'):
        """Deploy a stand alone PGBouncer container.

        This may be used when using cloud managed Postgres database.

        Args:
            name (str):
                Name of the deploy, it will be used same name for the
                service and secrets.
            postgres_database (str):
                Database at Postgres server that will be bounced.
            postgres_secret (str):
                Name of the postgres secret.
            postgres_host (str):
                Host to connect to downstream postgres.
            postgres_port (str):
                Port to connect to downstream postgres.
            version (str):
                Version associated with PGBouncer image.
        Kwargs:
            No kwargs.
        """
        self.name = name
        self.postgres_secret = postgres_secret
        self.postgres_database = postgres_database
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.version = version

    def create_deployment_file(self, kube_client):
        """Create_deployment_file.

        Args:
          kube_client:
            Client to communicate with Kubernets cluster.
        """
        deployment_postgres_text_f = pgbouncer_deploy.format(
            name=self.name, postgres_secret=self.postgres_secret,
            host=self.postgres_host, port=self.postgres_port,
            database=self.postgres_database, version=self.version)

        list_return = [
            {'type': 'deploy',
             'name': 'pgbouncer__{name}'.format(name=self.name),
             'content': deployment_postgres_text_f, 'sleep': 10}]
        return list_return


class ExternalPostgresDatabaseSecret:
    """Class to help deployment of Postgres database on cluster."""

    def __init__(self, name: str, db_username: str, db_password: str):
        """Create secret to use PgBouncer with external databases.

        Args:
            name (str):
                Service name to route calls to database.
            db_username (str):
                Database username.
            db_password (str):
                Database password.
        """
        self.name = name
        self._db_username = base64.b64encode(db_username.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()

    def create_deployment_file(self, kube_client):
        """Create_deployment_file.

        Args:
          kube_client:
            Client to communicate with Kubernets cluster.
        """
        secrets_text_f = secrets_postgres.format(
            name=self.name, db_username=self._db_username,
            db_password=self._db_password)

        list_return = [
            {'type': 'secrets',
             'name': 'postgres_external__{name}__secrets'
                .format(name=self.name),
             'content': secrets_text_f, 'sleep': 5},]
        return list_return
