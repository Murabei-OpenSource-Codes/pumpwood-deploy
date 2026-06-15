"""Deploy Postgres and PgBouncer microservices on Kubernetes."""
import base64
from importlib import resources
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from pumpwood_deploy.type import (
    PumpwoodDeploy, PumpwoodDeployDeployment, PumpwoodDeploySecret,
    PumpwoodDeployVolume)
from pumpwood_deploy.abc import BasePumpwoodDeployMicroservice


secrets_postgres = resources.files('pumpwood_deploy')\
    .joinpath('microservices/postgres/resources/secrets.yml')\
    .read_text(encoding='utf-8')
"""@private"""
deployment_postgres = resources.files('pumpwood_deploy')\
    .joinpath('microservices/postgres/resources/deploy__postgres.yml')\
    .read_text(encoding='utf-8')
"""@private"""
pgbouncer_deploy = resources.files('pumpwood_deploy')\
    .joinpath('microservices/postgres/resources/deploy__pgbouncer.yml')\
    .read_text(encoding='utf-8')
"""@private"""


class PostgresDatabase(BasePumpwoodDeployMicroservice):
    """Deploy a standalone Postgres database on the cluster."""

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
                 image: str = 'postgis/postgis:17-master'):
        """Configure a Postgres deployment with optional persistent disk.

        Args:
            db_username (str):
                Database username stored in the generated secret.
            db_password (str):
                Database password stored in the generated secret.
            name (str):
                Service name used to route calls to the database.
            disk_size (str | None):
                Size of the persistent disk to claim. Defaults to None.
            disk_name (str | None):
                Provider disk identifier attached to the cluster.
                Defaults to None.
            postgres_limits_memory (str):
                Memory limit for the Postgres container. Defaults to
                ``60Gi``.
            postgres_limits_cpu (str):
                CPU limit for the Postgres container. Defaults to
                ``12000m``.
            postgres_requests_memory (str):
                Memory request for the Postgres container. Defaults to
                ``20Mi``.
            postgres_requests_cpu (str):
                CPU request for the Postgres container. Defaults to
                ``1m``.
            postgres_public_ip (str | None):
                Optional public IP when exposing Postgres outside the
                cluster; not recommended for production use. Defaults to
                None.
            firewall_ips (list | None):
                Allowed source IPs when exposing Postgres publicly.
                Defaults to None.
            image (str):
                Container image used for the Postgres deployment.
                Defaults to ``postgis/postgis:17-master``.
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

    def create_deployment_file(self) -> list[PumpwoodDeploy]:
        """Build secrets, volume, and deployment manifests for Postgres.

        Returns:
            list[PumpwoodDeploy]:
                Ordered secret, volume, and deployment objects for the
                database instance.
        """
        secrets_text_f = secrets_postgres.format(
            name=self.name, db_username=self._db_username,
            db_password=self._db_password, ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt)

        # Create volume
        volume_claim_name = "{name}-data".format(name=self.name)
        deployment_postgres_text_f = deployment_postgres.format(
            volume_claim_name=volume_claim_name,
            name=self.name,
            requests_memory=self.postgres_requests_memory,
            requests_cpu=self.postgres_requests_cpu,
            limits_memory=self.postgres_limits_memory,
            limits_cpu=self.postgres_limits_cpu,
            image=self.image)

        list_return = [
            PumpwoodDeploySecret(
                name='postgres_sole__{name}__secrets'.format(name=self.name),
                content=secrets_text_f),
            PumpwoodDeployVolume(
                name='postgres_sole__{name}__volume'.format(name=self.name),
                disk_name=self.disk_name, disk_size=self.disk_size,
                volume_claim_name=volume_claim_name),
            PumpwoodDeployDeployment(
                name='postgres_sole__{name}__postgres'.format(name=self.name),
                content=deployment_postgres_text_f)]
        return list_return


class PGBouncerDatabase(BasePumpwoodDeployMicroservice):
    """Deploy a standalone PgBouncer connection pooler."""

    def __init__(self, name: str, postgres_secret: str,
                 postgres_database: str, postgres_host: str,
                 postgres_port: str = "5432",
                 version: str = '1.15.0-1-20251130',
                 pgbouncer_tls_sslmode: str = 'disable',
                 postgres_tls_sslmode: str = 'prefer'):
        """Configure a PgBouncer deployment for a downstream database.

        This deployment is useful when connecting to cloud-managed
        Postgres instances or shared cluster databases.

        Args:
            name (str):
                Deployment, service, and secret name prefix.
            postgres_database (str):
                Downstream Postgres database name to pool.
            postgres_secret (str):
                Name of the secret containing database credentials.
            postgres_host (str):
                Hostname of the downstream Postgres server.
            postgres_port (str):
                Port of the downstream Postgres server. Defaults to
                ``5432``.
            version (str):
                PgBouncer container image tag. Defaults to
                ``1.15.0-1-20251130``.
            pgbouncer_tls_sslmode (str):
                TLS policy for client connections to PgBouncer. Defaults
                to ``disable``.
            postgres_tls_sslmode (str):
                TLS policy for PgBouncer connections to Postgres. Defaults
                to ``prefer``.
        """
        self.name = name
        self.postgres_secret = postgres_secret
        self.postgres_database = postgres_database
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.version = version
        self.pgbouncer_tls_sslmode = pgbouncer_tls_sslmode
        self.postgres_tls_sslmode = postgres_tls_sslmode

    def create_deployment_file(self) -> list[PumpwoodDeploy]:
        """Build the PgBouncer deployment manifest.

        Returns:
            list[PumpwoodDeploy]:
                Single-element list with the PgBouncer deployment object.
        """
        deployment_postgres_text_f = pgbouncer_deploy.format(
            name=self.name, postgres_secret=self.postgres_secret,
            host=self.postgres_host, port=self.postgres_port,
            database=self.postgres_database, version=self.version,
            pgbouncer_tls_sslmode=self.pgbouncer_tls_sslmode,
            postgres_tls_sslmode=self.postgres_tls_sslmode)

        list_return = [
            PumpwoodDeployDeployment(
                name='pgbouncer__{name}'.format(name=self.name),
                content=deployment_postgres_text_f,
                sleep=10)]
        return list_return


class ExternalPostgresDatabaseSecret(BasePumpwoodDeployMicroservice):
    """Create credentials for external Postgres used with PgBouncer."""

    def __init__(self, name: str, db_username: str, db_password: str):
        """Configure a secret for an external Postgres database.

        Args:
            name (str):
                Service name used to identify the secret resource.
            db_username (str):
                Database username stored in the generated secret.
            db_password (str):
                Database password stored in the generated secret.
        """
        self.name = name
        self._db_username = base64.b64encode(db_username.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()

    def create_deployment_file(self) -> list[PumpwoodDeploy]:
        """Build the external Postgres credentials secret.

        Returns:
            list[PumpwoodDeploy]:
                Secret object containing external database credentials.
        """
        secrets_text_f = secrets_postgres.format(
            name=self.name, db_username=self._db_username,
            db_password=self._db_password, ssl_key="",
            ssl_crt="")

        list_return = [
            PumpwoodDeploySecret(
                name='postgres_external__{name}__secrets'
                    .format(name=self.name),
                content=secrets_text_f,
                sleep=5)]
        return list_return
