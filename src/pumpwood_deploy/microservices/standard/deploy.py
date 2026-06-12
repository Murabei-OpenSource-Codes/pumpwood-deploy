"""Create standard deploy and secrets."""
import base64
from typing import Literal
from importlib import resources
from pumpwood_deploy.type import (
    PumpwoodDeployStorage, PumpwoodDeployStorageGCP,
    PumpwoodDeployStorageAzure, PumpwoodDeployStorageAWS,
    PumpwoodDeploySecret, PumpwoodDeploySecretFile, PumpwoodDeployDeployment,
    PumpwoodDeployConfigMap)


# Kong deployment
kong_deployment = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/deploy__kong.yml'))
secret__kong = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secret__kong.yml'))

# RabbitMQ Deploy
rabbitmq_deployment = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secrets__rabbitmq.yml'))
rabbitmq_secrets = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secrets__rabbitmq.yml'))

# General secrets
model_secrets = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secrets__model_microservices.yml'))
hash_salt = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secret__salt.yml'))

# Storage config and secrets
storage_config_map = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/config_map__storage.yml'))
azure__storage_key_secrets = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secrets__azure_storage.yml'))
gcp__storage_key_secrets = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secrets__gpc_storage_empty.yml'))
aws__storage_key_secrets = str(
    resources.files('pumpwood_deploy')
    .joinpath(
        'microservices/standard/'
        'resources/secrets__aws_storage.yml'))


class StandardMicroservices:
    """Standard microservices deployment manager.

    Prepares and builds Kubernetes deployment specifications, secrets,
    and configurations for Kong, RabbitMQ, and Cloud Storage.
    """

    def __init__(self,
                 rabbit_password: str,
                 model_user_password: str,
                 storage_type: str,
                 storage_deploy_args: PumpwoodDeployStorage | None,
                 storage_bucket_name: str,
                 hash_salt: str,
                 crypto_pumpwood_key: str,
                 kong_version: str,
                 kong_db_username: str,
                 kong_db_password: str,
                 kong_db_database: str,
                 kong_db_host: str,
                 kong_db_port: str,
                 kong_repository: str = "gcr.io/repositorio-geral-170012"):
        """Initialize StandardMicroservices deployment configuration.

        Args:
            rabbit_password (str):
                Password for RabbitMQ.
            model_user_password (str):
                Password for the model microservice user.
            storage_type (str):
                Storage provider, one of: 'azure_storage', 'google_bucket',
                or 'aws_s3'.
            storage_deploy_args (PumpwoodDeployStorage | None):
                Storage arguments object, or None if configured via K8s
                provider role-based access.
            storage_bucket_name (str):
                Name of the bucket/container used for storage.
            hash_salt (str):
                Salt used for microservice security hash generation.
            crypto_pumpwood_key (str):
                Encryption key for Pumpwood crypto fields.
            kong_version (str):
                Version label/tag for Kong deployment.
            kong_db_username (str):
                Username to authenticate to Kong Postgres DB.
            kong_db_password (str):
                Password to authenticate to Kong Postgres DB.
            kong_db_database (str):
                Name of the Kong Postgres database.
            kong_db_host (str):
                Host address of the Kong Postgres database.
            kong_db_port (str):
                Port of the Kong Postgres database.
            kong_repository (str):
                Docker repository for custom Kong image. Defaults to
                "gcr.io/repositorio-geral-170012".
        """
        self.kong_repository = kong_repository
        self._gcp_credential_file = None

        # Set the storage configuration
        self.set_storage_parameters(
            storage_type=storage_type,
            storage_deploy_args=storage_deploy_args)

        # General secrets
        self._hash_salt = base64.b64encode(
            hash_salt.encode()).decode()
        self._crypto_pumpwood_key = base64.b64encode(
            crypto_pumpwood_key.encode()).decode()
        self._rabbit_password = base64.b64encode(
            rabbit_password.encode()).decode()
        self._model_user_password = base64.b64encode(
            model_user_password.encode()).decode()

        # Storage secrets
        self.storage_type = storage_type
        self.storage_bucket_name = storage_bucket_name

        # Kong disk for postgres deploy
        self.kong_version = kong_version
        self.kong_db_username = kong_db_username
        self.kong_db_database = kong_db_database
        self.kong_db_host = kong_db_host
        self.kong_db_port = kong_db_port
        self._kong_db_password = base64.b64encode(
            kong_db_password.encode()).decode()

    def set_storage_parameters(self,
                               storage_type: Literal["aws_s3", "gcp_bucket",
                                                     "azure_storage"],
                               storage_deploy_args: PumpwoodDeployStorage |
                                                    None
                               ) -> None:
        """Set storage credentials and parameters based on storage type.

        Args:
            storage_type (Literal["aws_s3", "gcp_bucket", "azure_storage"]):
                The storage type used by standard microservices.
            storage_deploy_args (PumpwoodDeployStorage | None):
                Deployment storage configuration arguments.

        Returns:
            None:
                Always returns None.

        Raises:
            ValueError:
                If the storage_deploy_args type does not match storage_type,
                or if credential parameters are invalid.
            NotImplementedError:
                If storage_type is not a supported/implemented provider.
        """
        # Set default values for the storage parameters
        self._azure_storage_connection_string = base64.b64encode(
            "not_configured".encode()).decode()
        self._aws_access_key_id = base64.b64encode(
            "not_configured".encode()).decode()
        self._aws_secret_access_key = base64.b64encode(
            "not_configured".encode()).decode()

        # Using Azure blob storage for flat files
        if storage_deploy_args is None:
            return None

        if storage_type == "azure_storage":
            is_valid = isinstance(
                storage_deploy_args, PumpwoodDeployStorageAzure)
            if not is_valid:
                msg = (
                    "Azure storage_deploy_args must be a "
                    "PumpwoodDeployStorageAzure object.")
                raise ValueError(msg)
            self._azure_storage_connection_string = base64.b64encode(
                storage_deploy_args
                .storage_connection_string
                .encode()).decode()
            return None

        # Using GCP Storage Buckets storage for flat files
        elif storage_type == "google_bucket":
            is_valid = isinstance(
                storage_deploy_args, PumpwoodDeployStorageGCP)
            if not is_valid:
                msg = (
                    "GCP storage_deploy_args must be a "
                    "PumpwoodDeployStorageGCP object.")
                raise ValueError(msg)

            credential_file = storage_deploy_args.credential_file
            if not isinstance(credential_file, str):
                raise ValueError(
                    "GCP storage must have credential_file args.")

            # Deploy at containers will use a file named as
            # key-storage.json using a different name for de the will
            # result on deploy with not found file error.
            is_valid = credential_file.endswith('key-storage.json')
            if not is_valid:
                msg = (
                    "Key storage file must be named 'key-storage.json', "
                    "change file name in order to deploy work.")
                raise ValueError(msg)
            self._gcp_credential_file = credential_file
            return None

        # Using AWS S3 for flat files
        elif storage_type == "aws_s3":
            is_valid = isinstance(
                storage_deploy_args, PumpwoodDeployStorageAWS)
            if not is_valid:
                msg = (
                    "AWS storage_deploy_args must be a "
                    "PumpwoodDeployStorageAWS object.")
                raise ValueError(msg)

            self._aws_access_key_id = base64.b64encode(
                storage_deploy_args.access_key_id.encode()).decode()
            self._aws_secret_access_key = base64.b64encode(
                storage_deploy_args.secret_access_key.encode()).decode()
            return None

        # Raise if another option is passed as arguments
        else:
            msg = "storage_type not implemented: {}".format(storage_type)
            raise NotImplementedError(msg)

    def create_deployment_file(self, kube_client=None):
        """Create and format the lists of Kubernetes manifests.

        Args:
            kube_client (Kubernets | None):
                Kubernetes client helper. Defaults to None.

        Returns:
            list:
                A list of deployment objects (secrets, deployments, and
                config maps) to apply to the Kubernetes cluster.
        """
        # RabbitMQ
        secrets_text_formated = rabbitmq_secrets.format(
            password=self._rabbit_password)

        # Hash Salt
        hash_salt_formated = hash_salt.format(
            hash_salt=self._hash_salt,
            crypto_pumpwood_key=self._crypto_pumpwood_key)

        # Model microservice user
        microservice_model_secrets_formated = model_secrets.format(
            password=self._model_user_password)

        ############
        # Storages #
        storage_config_map_fmt = storage_config_map.format(
            storage_type=self.storage_type,
            bucket_name=self.storage_bucket_name)

        # Azure connection string secrets
        azure__storage_key_secrets_fmt = azure__storage_key_secrets.format(
            azure_storage_connection_string=(
                self._azure_storage_connection_string))

        # AWS
        aws__storage_key_secrets_fmt = aws__storage_key_secrets.format(
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key)

        #####################
        # Kong service mesh #
        kong_deployment_fmt = kong_deployment.format(
            repository=self.kong_repository,
            version=self.kong_version,
            kong_db_host=self.kong_db_host,
            kong_db_port=self.kong_db_port,
            kong_db_username=self.kong_db_username,
            kong_db_database=self.kong_db_database)
        secret_kong_fmt = secret__kong.format(
            kong_db_password=self._kong_db_password)

        # Create the list with the deployment files
        deploy_list = [
            # RabbitMQ
            PumpwoodDeploySecret(
                name='rabbitmq__secrets', content=secrets_text_formated,
                sleep=5),
            PumpwoodDeployDeployment(
                name='rabbitmq__deployment', content=rabbitmq_deployment,
                sleep=0),

            # Hash salt
            PumpwoodDeploySecret(
                name='hash_salt__secrets', content=hash_salt_formated,
                sleep=5),

            # General secret for all models
            PumpwoodDeploySecret(
                name='microsservice_model__secrets',
                content=microservice_model_secrets_formated,
                sleep=5),

            # Kong service mesh
            PumpwoodDeploySecret(
                name='kong__secrets', content=secret_kong_fmt,
                sleep=5),
            PumpwoodDeployDeployment(
                name='kong__deployment', content=kong_deployment_fmt,
                sleep=0),

            # Storage secrets and config
            PumpwoodDeployConfigMap(
                name='storage-config', content=storage_config_map_fmt,
                sleep=5),
            PumpwoodDeploySecret(
                name='azure__storage_key',
                content=azure__storage_key_secrets_fmt,
                sleep=5),
            PumpwoodDeploySecret(
                name='aws__storage_key',
                content=aws__storage_key_secrets_fmt,
                sleep=5)
        ]

        # Add deploy of the google credential file if set
        if self._gcp_credential_file is not None:
            deploy_list.append(
                PumpwoodDeploySecretFile(
                    name='gcp--storage-key', path=self._gcp_credential_file,
                    sleep=5))
        return deploy_list
