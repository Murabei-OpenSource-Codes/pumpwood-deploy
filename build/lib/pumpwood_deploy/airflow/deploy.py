"""PumpWood DataLake Microservice Deploy."""
import os
import base64
import pkg_resources


app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'airflow/resources/deploy__webserver.yml').read().decode()
scheduler_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'airflow/resources/deploy__scheduler.yml').read().decode()
worker_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'airflow/resources/deploy__worker.yml').read().decode()
secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'airflow/resources/secrets.yml').read().decode()
service_account = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'airflow/resources/service_account.yml').read().decode()


class AirflowMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self,
                 db_password: str,
                 microservice_password: str,
                 secret_key: str,
                 fernet_key: str,
                 k8s_pods_namespace: str,
                 bucket_name: str,
                 disk_name: str,
                 disk_size: str,
                 git_ssh_private_key_path: str,
                 git_ssh_public_key_path: str,
                 git_server: str,
                 git_repository: str,
                 git_branch: str,
                 db_username: str = "pumpwood",
                 db_database: str = "pumpwood",
                 db_host: str = "postgres-simple-airflow",
                 db_port: str = "5432",
                 remote_base_log_folder: str = "",
                 remote_logging: bool = False,
                 remote_log_conn_id: str = "",
                 postgres_public_ip: str = None,
                 repository: str = "",
                 app_replicas: int = 1,
                 worker_replicas: int = 3):
        """__init__: Class constructor."""
        self.db_username = db_username
        self.db_database = db_database
        self.db_host = db_host
        self.db_port = db_port
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self._fernet_key = base64.b64encode(
            fernet_key.encode()).decode()
        self._secret_key = base64.b64encode(
            secret_key.encode()).decode()
        self.git_ssh_private_key_path = git_ssh_private_key_path
        self.git_ssh_public_key_path = git_ssh_public_key_path

        self.postgres_public_ip = postgres_public_ip
        self.k8s_pods_namespace = k8s_pods_namespace
        self.remote_base_log_folder = remote_base_log_folder
        self.remote_logging = remote_logging
        self.remote_log_conn_id = remote_log_conn_id

        # Git config
        self.git_server = git_server
        self.git_repository = git_repository
        self.git_branch = git_branch

        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)

        self.repository = repository
        self.app_replicas = app_replicas
        self.worker_replicas = worker_replicas

    def create_deployment_file(self, **kwargs):
        """create_deployment_file."""
        # General secrets
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            secret_key=self._secret_key, fernet_key=self._fernet_key)

        service_account__frmt = service_account.format(
            namespace=self.k8s_pods_namespace)

        # Deployments
        app_deployment__frmt = app_deployment.format(
                db_username=self.db_username,
                db_database=self.db_database,
                db_host=self.db_host,
                db_port=self.db_port,
                repository=self.repository,
                bucket_name=self.bucket_name,
                replicas=self.app_replicas,
                git_server=self.git_server,
                git_repository=self.git_repository,
                git_branch=self.git_branch,
                k8s_pods_namespace=self.k8s_pods_namespace,
                remote_base_log_folder=self.remote_base_log_folder,
                remote_logging=self.remote_logging,
                remote_log_conn_id=self.remote_log_conn_id)
        scheduler_deployment__frmt = scheduler_deployment.format(
                db_username=self.db_username,
                db_database=self.db_database,
                db_host=self.db_host,
                db_port=self.db_port,
                repository=self.repository,
                bucket_name=self.bucket_name,
                git_server=self.git_server,
                git_repository=self.git_repository,
                git_branch=self.git_branch,
                k8s_pods_namespace=self.k8s_pods_namespace,
                remote_base_log_folder=self.remote_base_log_folder,
                remote_logging=self.remote_logging,
                remote_log_conn_id=self.remote_log_conn_id)
        worker_deployment__frmt = worker_deployment.format(
                db_username=self.db_username,
                db_database=self.db_database,
                db_host=self.db_host,
                db_port=self.db_port,
                repository=self.repository,
                bucket_name=self.bucket_name,
                replicas=self.worker_replicas,
                git_server=self.git_server,
                git_repository=self.git_repository,
                git_branch=self.git_branch,
                k8s_pods_namespace=self.k8s_pods_namespace,
                remote_base_log_folder=self.remote_base_log_folder,
                remote_logging=self.remote_logging,
                remote_log_conn_id=self.remote_log_conn_id)

        ssh_keys = [
            "id_rsa=" + self.git_ssh_private_key_path,
            "id_rsa.pub=" + self.git_ssh_public_key_path]
        list_return = [
            # Secrets
            {'type': 'secrets', 'name': 'airflow__secrets',
             'content': secrets_text_formated, 'sleep': 5},
            {'type': 'secrets_file', 'name': 'airflow--gitkey',
             'path': ssh_keys, 'sleep': 5},
            {'type': 'deploy', 'name': 'airflow__serviceaccount',
             'content': service_account__frmt, 'sleep': 5},

            # Deployments
            {'type': 'deploy', 'name': 'airflow_app__deploy',
             'content': app_deployment__frmt, 'sleep': 0},
            {'type': 'deploy', 'name': 'airflow_scheduler__deploy',
             'content': scheduler_deployment__frmt, 'sleep': 0},
            {'type': 'deploy', 'name': 'airflow_worker__deploy',
             'content': worker_deployment__frmt, 'sleep': 0},
        ]
        return list_return
