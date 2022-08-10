"""Create standard deploy and secrets."""
import os
import base64
from pumpwood_deploy.microservices.standard.resources.yml__resorces import (
    rabbitmq_deployment, rabbitmq_secrets, model_secrets, hash_salt,
    kong_postgres_deployment, kong_deployment,
    azure__storage_key_secrets, gcp__storage_key_secrets,
    aws__storage_key_secrets, storage_config_map)


class StandardMicroservices:
    """
    Create StandardMicroservices.

    Create RabbitMQ deployment and secrets, postgres-init-configmap config map
    for postgres initiation and storage bucket key secret.

    """

    def __init__(self, hash_salt: str, rabbit_password: str,
                 model_user_password: str, storage_type: str,
                 storage_deploy_args: str, kong_db_disk_name: str,
                 kong_db_disk_size: str,
                 kong_repository: str = "gcr.io/repositorio-geral-170012"):
        """
        __init__.

        Args:
          hash_salt (str): Hash salt of hash identification at the
              microservices.
          rabbit_password (str): rabbit_password for rabbitMQ login.
          bucket_key_path (str): Path to bucket JSON key.
          storage_type (str): Storage provider must be in [
            'azure', 'gcp', 'aws'], correpond to the provider os the flat
            file storage system.
          storage_deploy_args (str): Args used to access storage at the
            pods. Each provider must have diferent arguments:
            # azure_storage:
            - azure_storage_connection_string: Set conenction string to
                a blob storage.
            # google_bucket:
            - credential_file: Set a path to a credetial file of a service
                user with access to the bucket that will be used at the
                deployment.
            # aws_s3:
            - aws_access_key_id: Access key of the service user with
                access to the s3 used in deployment.
            - aws_secret_access_key: Access secret of the service user with
                access to the s3 used in deployment.
        """
        self.kong_repository = kong_repository
        if storage_type == "azure_storage":
            azure_deploy = storage_deploy_args.get("azure_storage", {})
            if "azure_storage_connection_string" not in azure_deploy.keys():
                raise Exception(
                    "Azure storage must have azure_storage_connection_string "
                    "args.")

            storage_deploy_args["google_bucket"] = {
                "credential_file": None}
            storage_deploy_args["aws_s3"] = {
                "aws_access_key_id": "not_configured",
                "aws_secret_access_key": "not_configured"}

        elif storage_type == "google_bucket":
            gcp_deploy = storage_deploy_args.get("google_bucket", {})
            if "credential_file" not in gcp_deploy.keys():
                raise Exception(
                    "GCP storage must have credential_file args.")

            storage_deploy_args["azure_storage"] = {
                "azure_storage_connection_string": "not_configured"}
            storage_deploy_args["aws_s3"] = {
                "aws_access_key_id": "not_configured",
                "aws_secret_access_key": "not_configured"}

        elif storage_type == "aws_s3":
            aws_deploy = storage_deploy_args.get("aws_s3", {})
            if_clause = ("aws_access_key_id" not in aws_deploy.keys()) or (
                "aws_secret_access_key" not in aws_deploy.keys())
            if if_clause:
                raise Exception(
                    "AWS storage must have aws_access_key_id and "
                    "aws_secret_access_key args.")

            storage_deploy_args["google_bucket"] = {
                "credential_file": None}
            storage_deploy_args["azure_storage"] = {
                "azure_storage_connection_string": "not_configured"}

        else:
            raise Exception(
                "storage_type not implemented:", storage_type)

        # General secrets
        self._hash_salt = base64.b64encode(
            hash_salt.encode()).decode()
        self._rabbit_password = base64.b64encode(
            rabbit_password.encode()).decode()
        self._model_user_password = base64.b64encode(
            model_user_password.encode()).decode()

        # Storage secrets
        self.storage_type = storage_type

        # Azure
        self._azure_storage_connection_string = base64.b64encode(
            storage_deploy_args["azure_storage"][
                "azure_storage_connection_string"].encode()).decode()

        # AWS
        self._aws_access_key_id = base64.b64encode(
            storage_deploy_args["aws_s3"][
                "aws_access_key_id"].encode()).decode()
        self._aws_secret_access_key = base64.b64encode(
            storage_deploy_args["aws_s3"][
                "aws_secret_access_key"].encode()).decode()

        # GCP
        self._gcp_credential_file = None
        if storage_deploy_args["google_bucket"]["credential_file"] is not None:
            self._gcp_credential_file = storage_deploy_args[
                "google_bucket"]["credential_file"]

        # Path and configs
        self.kong_db_disk_name = kong_db_disk_name
        self.kong_db_disk_size = kong_db_disk_size

    def create_deployment_file(self, kube_client):
        """
        Create deployment file.

        Args:
            kube_client: Client to communicate with Kubernets cluster.
        """
        # RabbitMQ
        secrets_text_formated = rabbitmq_secrets.format(
            password=self._rabbit_password)

        # Hash Salt
        hash_salt_formated = hash_salt.format(
            hash_salt=self._hash_salt)

        # Model microservice user
        microservice_model_secrets_formated = model_secrets.format(
            password=self._model_user_password)

        kong_postgres_volume_formated = kube_client.create_volume_yml(
            disk_name=self.kong_db_disk_name,
            disk_size=self.kong_db_disk_size,
            volume_claim_name="postgres-kong-database")

        ############
        # Storages #
        storage_config_map_fmt = storage_config_map.format(
            storage_type=self.storage_type)

        # Azure connection string secrets
        azure__storage_key_secrets_fmt = azure__storage_key_secrets.format(
            azure_storage_connection_string=self._azure_storage_connection_string)

        # GCP
        gcp_bucket_secrets = {
            'type': 'secrets', 'name': 'gcp--storage-key',
            'content': gcp__storage_key_secrets, 'sleep': 5}
        if self._gcp_credential_file is not None:
            gcp_bucket_secrets = {
                'type': 'secrets_file', 'name': 'gcp--storage-key',
                'path': self._gcp_credential_file, 'sleep': 5
            }

        # AWS
        aws__storage_key_secrets_fmt = aws__storage_key_secrets.format(
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key)
        ############

        # Kong loadbalancer
        kong_deployment_fmt = kong_deployment.format(
            repository=self.kong_repository)

        return [
            # RabbitMQ
            {'type': 'secrets', 'name': 'rabbitmq__secrets',
             'content': secrets_text_formated, 'sleep': 5},
            {'type': 'deploy', 'name': 'rabbitmq__deployment',
             'content': rabbitmq_deployment, 'sleep': 0},

            # Hash salt
            {'type': 'secrets', 'name': 'hash_salt__secrets',
             'content': hash_salt_formated, 'sleep': 5},

            #################
            # Storage secrets
            {'type': 'configmap', 'name': 'storage-config',
             'content': storage_config_map_fmt, 'sleep': 5},

            # Azure
            {'type': 'secrets', 'name': 'azure__storage_key',
             'content': azure__storage_key_secrets_fmt, 'sleep': 5},

            # GCP
            gcp_bucket_secrets,

            {'type': 'secrets', 'name': 'aws__storage_key',
             'content': aws__storage_key_secrets_fmt, 'sleep': 5},
            #################

            # Model microservice
            {'type': 'secrets', 'name': 'microsservice_model__secrets',
             'content': microservice_model_secrets_formated, 'sleep': 5},

            # Kong loadbalancer
            {'type': 'volume', 'name': 'load_balancer__volume',
             'content': kong_postgres_volume_formated, 'sleep': 10},
            {'type': 'deploy', 'name': 'load_balancer__postgres',
             'content': kong_postgres_deployment, 'sleep': 0},
            {'type': 'deploy', 'name': 'load_balancer__app',
             'content': kong_deployment_fmt, 'sleep': 0}]
