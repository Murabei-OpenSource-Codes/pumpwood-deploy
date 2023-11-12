"""PumpWood Auth Module."""
import pkg_resources
import os
import base64


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/deploy__app.yml').read().decode()
auth_admin_static = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/deploy__static.yml').read().decode()
auth_log_worker = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/deploy__log_worker.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/deploy__test_postgres.yml').read().decode()


class PumpWoodAuthMicroservice:
    """PumpWoodAuthMicroservice."""

    def __init__(self,
                 secret_key: str,
                 microservice_password: str,
                 email_host_user: str,
                 email_host_password: str,
                 bucket_name: str,
                 app_version: str,
                 static_version: str,
                 db_username: str = "pumpwood",
                 db_password: str = "pumpwood",
                 db_database: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-auth",
                 db_port: str = "5432",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 worker_log_version: str = None,
                 worker_log_disk_name: str = None,
                 worker_log_disk_size: str = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012"):
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
            worker_log_version (str): Version of the log worker to deploy.
            worker_log_disk_name (str): Name of the disk to be used on worker
                deploy.
            worker_log_disk_size (str): Size of the disk allocated to worker
                log container.
        """
        self._secret_key = base64.b64encode(secret_key.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self._email_host_user = base64.b64encode(
            email_host_user.encode()).decode()
        self._email_host_password = base64.b64encode(
            email_host_password.encode()).decode()
        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)
        self.db_username = db_username
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database

        # App
        self.repository = (
            repository + "/"
            if repository is not None else "")
        self.app_version = app_version
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Static
        self.static_version = static_version

        # Postgres
        self.test_db_version = test_db_version
        self.test_db_repository = (
            test_db_repository + "/"
            if test_db_repository is not None else "")

        # Log Worker
        self.worker_log_version = worker_log_version
        self.worker_log_disk_name = worker_log_disk_name
        self.worker_log_disk_size = worker_log_disk_size

    def create_deployment_file(self, kube_client=None, **kwargs):
        """Create_deployment_file."""
        rabbitmq_log = "FALSE" if self.worker_log_version is None else "TRUE"
        secrets_text_f = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            email_host_user=self._email_host_user,
            email_host_password=self._email_host_password,
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

            # Loger
            rabbitmq_log=rabbitmq_log)

        deployment_auth_admin_static_f = \
            auth_admin_static.format(
                repository=self.repository,
                version=self.static_version)

        deployment_auth_admin_log_worker = None
        deployment_auth_admin_log_volume = None
        if rabbitmq_log == "TRUE":
            volume_claim_name = "pumpwood-auth-log-data"
            deployment_auth_admin_log_volume = kube_client.create_volume_yml(
                disk_name=self.worker_log_disk_name,
                disk_size=self.worker_log_disk_size,
                volume_claim_name=volume_claim_name)
            deployment_auth_admin_log_worker = auth_log_worker.format(
                repository=self.repository,
                version=self.worker_log_version,
                bucket_name=self.bucket_name,
                volume_claim_name=volume_claim_name)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version)

        list_return = [{
            'type': 'secrets', 'name': 'pumpwood_auth__secrets',
            'content': secrets_text_f, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_auth__postgres',
                'content': deployment_postgres_text_f, 'sleep': 20})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_auth_app__deploy',
            'content': deployment_auth_app_text_f, 'sleep': 10})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_auth_admin_static__deploy',
            'content': deployment_auth_admin_static_f, 'sleep': 0})

        if deployment_auth_admin_log_volume is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_auth__volume_logs',
                'content': deployment_auth_admin_log_volume, 'sleep': 0})
        if deployment_auth_admin_log_worker is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_auth__worker_logs',
                'content': deployment_auth_admin_log_worker, 'sleep': 0})
        return list_return
