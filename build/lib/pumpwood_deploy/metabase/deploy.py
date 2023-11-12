"""PumpWood DataLake Microservice Deploy."""
import os
import base64
import pkg_resources


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'metabase/resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'metabase/resources/deploy__app.yml').read().decode()
config_map = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'metabase/resources/config_map.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'metabase/resources/postgres__test.yml').read().decode()


class MetabaseMicroservice:
    """Deploy Metabase as microservice."""

    def __init__(self, metabase_site_url: str,
                 db_password: str,
                 embedding_secret_key: str,
                 encryption_secret_key: str,
                 db_usename: str = "metabase",
                 db_host: str = "postgres-metabase",
                 db_database: str = "metabase",
                 db_port: str = "5432",
                 app_replicas: int = 1,
                 app_limits_memory: str = "6Gi",
                 app_limits_cpu: str = "2000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
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
            test_db_version (str): Set a test database with version.
            test_db_repository (str): Define a repository for the test
              database.
        Returns:
          MetabaseMicroservice: New Object
        Raises:
          No especific raises.deployment_postgres_text_f
        Example:
          No example yet.
        """
        self._db_usename = base64.b64encode(db_usename.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self.db_host = db_host
        self.db_database = db_database
        self.db_port = db_port
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
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository

    def create_deployment_file(self, **kwargs):
        """create_deployment_file."""
        # General secrets
        secrets_text_formated = secrets.format(
            db_usename=self._db_usename, db_password=self._db_password,
            embedding_secret_key=self.embedding_secret_key,
            encryption_secret_key=self.encryption_secret_key)

        # Deployments
        app_deployment__frmt = app_deployment.format(
            db_host=self.db_host,
            db_database=self.db_database,
            db_port=self.db_port,
            replicas=self.app_replicas,
            limits_memory=self.app_limits_memory,
            limits_cpu=self.app_limits_cpu,
            requests_memory=self.app_requests_memory,
            requests_cpu=self.app_requests_cpu)
        config_map__frmt = config_map.format(
            site_url=self.metabase_site_url)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)

        list_return = [{
            'type': 'secrets', 'name': 'metabase__secrets',
            'content': secrets_text_formated, 'sleep': 5}, {
            'type': 'secrets', 'name': 'metabase__config_map',
            'content': config_map__frmt, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy', 'name': 'metabase__postgres',
                'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append({
            'type': 'deploy', 'name': 'metabase__deploy',
            'content': app_deployment__frmt, 'sleep': 0})
        return list_return
