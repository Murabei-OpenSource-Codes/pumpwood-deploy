"""PumpWood DataLake Microservice Deploy."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template
from pumpwood_deploy.airflow.resources.yml__resources import (
    app_deployment, scheduler_deployment, worker_deployment,
    secrets, services__load_balancer, deployment_postgres, service_account)


class AirflowMicroservice:
    """PumpWoodDatalakeMicroservice."""

    def __init__(self, db_password: str, microservice_password: str,
                 secret_key: str, fernet_key: str,
                 k8s_pods_namespace: str, version: str, bucket_name: str,
                 disk_name: str, disk_size: str,
                 git_ssh_private_key_path: str, git_ssh_public_key_path: str,
                 git_server: str, git_repository: str, git_branch: str,
                 remote_base_log_folder: str = "",
                 remote_logging: bool = False,
                 remote_log_conn_id: str = "",
                 postgres_public_ip: str = None,
                 firewall_ips: list = None, repository: str = "",
                 app_replicas: int = 1, worker_replicas: int = 3):
        """
        __init__: Class constructor.

        Args:
            db_password (str): Password for database.
            microservice_password (str): Microservice password.
            secret_key (str): Secret key for Airflow App.
            fernet_key (str): Fernet Key to criptograph secrets.
            k8s_pods_namespace (str): K8s namespace to deploy Kubernets
                Operator Pods.
            version (str): Verison of the image.
            bucket_name (str): Name of the bucket (Storage).
            disk_size (str): Disk size (ex.: 50Gi, 100Gi).
            disk_name (str): Name of the disk that will be used in postgres.
            git_ssh_private_key_path (str): Path to ssh private key to access
                the git repository.
            git_ssh_public_key_path (str): Path to ssh public key to access
                the git repository.
            git_server (str): Git server, ex.: 'bitbucket.org'
            git_repository (str): Must be ssh repository starting with
                git@.
            git_branch (str): Brach to pull Dag codes.

        Kwargs:
            remote_base_log_folder (str) = "": Airflow
                AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER variable.
            remote_logging (str) = False: Airflow
                AIRFLOW__LOGGING__REMOTE_LOGGING variable.
            remote_log_conn_id (str) = "": Airflow
                AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID variable
            postgres_public_ip (str): Postgres public IP.
            firewall_ips (list) = None: List the IPs allowed to connect to
                datalake.
            repository (str) = "": Repository to pull Image, default "" which
                is docker hub.
            app_replicas (int) = 1: Number of replicas in app deployment.
            worker_replicas (int) = 3: Number of replicas in worker deployment.
        Returns:
          AirflowMicroservice: New Object
        Raises:
          No especific raises.
        Example:
          No example yet.
        """
        disk_deploy = (disk_name is not None and disk_size is not None)
        if not disk_deploy:
            raise Exception(
                "Airflow deployment must have a disk associated.")

        postgres_certificates = create_ssl_key_ssl_crt()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self._fernet_key = base64.b64encode(
            fernet_key.encode()).decode()
        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()
        self._secret_key = base64.b64encode(
            secret_key.encode()).decode()
        self.git_ssh_private_key_path = git_ssh_private_key_path
        self.git_ssh_public_key_path = git_ssh_public_key_path

        self.postgres_public_ip = postgres_public_ip
        self.firewall_ips = firewall_ips
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
        self.version = version
        self.app_replicas = app_replicas
        self.worker_replicas = worker_replicas

    def create_deployment_file(self, kube_client):
        """create_deployment_file."""
        # General secrets
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            ssl_key=self._ssl_key, ssl_crt=self._ssl_crt,
            secret_key=self._secret_key, fernet_key=self._fernet_key)

        service_account__frmt = service_account.format(
            namespace=self.k8s_pods_namespace)

        # Postgres
        volume_postgres__frmt = kube_client.create_volume_yml(
            disk_name=self.disk_name, disk_size=self.disk_size,
            volume_claim_name="postgres-simple-airflow")
        deployment_postgres__frmt = deployment_postgres

        # Deployments
        app_deployment__frmt = app_deployment.format(
                repository=self.repository, version=self.version,
                bucket_name=self.bucket_name, replicas=self.app_replicas,
                git_server=self.git_server, git_repository=self.git_repository,
                git_branch=self.git_branch,
                k8s_pods_namespace=self.k8s_pods_namespace,
                remote_base_log_folder=self.remote_base_log_folder,
                remote_logging=self.remote_logging,
                remote_log_conn_id=self.remote_log_conn_id)
        scheduler_deployment__frmt = scheduler_deployment.format(
                repository=self.repository, version=self.version,
                bucket_name=self.bucket_name, git_server=self.git_server,
                git_repository=self.git_repository, git_branch=self.git_branch,
                k8s_pods_namespace=self.k8s_pods_namespace,
                remote_base_log_folder=self.remote_base_log_folder,
                remote_logging=self.remote_logging,
                remote_log_conn_id=self.remote_log_conn_id)
        worker_deployment__frmt = worker_deployment.format(
                repository=self.repository, version=self.version,
                bucket_name=self.bucket_name, replicas=self.worker_replicas,
                git_server=self.git_server, git_repository=self.git_repository,
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

            # Postgres
            {'type': 'volume', 'name': 'airflow__volume',
             'content': volume_postgres__frmt, 'sleep': 10},
            {'type': 'volume', 'name': 'airflow__postgres',
             'content': deployment_postgres__frmt, 'sleep': 0},

            # Deployments
            {'type': 'deploy', 'name': 'airflow_app__deploy',
             'content': app_deployment__frmt, 'sleep': 0},
            {'type': 'deploy', 'name': 'airflow_scheduler__deploy',
             'content': scheduler_deployment__frmt, 'sleep': 0},
            {'type': 'deploy', 'name': 'airflow_worker__deploy',
             'content': worker_deployment__frmt, 'sleep': 0},
        ]

        if self.firewall_ips is not None and self.postgres_public_ip:
            services__load_balancer_template = Template(
                services__load_balancer)
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)
            list_return.append({
                'type': 'services',
                'name': 'airflow__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})
        return list_return
