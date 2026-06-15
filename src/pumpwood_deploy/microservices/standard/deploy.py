"""Create standard deploy and secrets."""
import base64
from typing import Literal
from importlib import resources
from pumpwood_deploy.type import (
    PumpwoodDeployStorage, PumpwoodDeployStorageGCP,
    PumpwoodDeployStorageAzure, PumpwoodDeployStorageAWS,
    PumpwoodDeploySecret, PumpwoodDeploySecretFile, PumpwoodDeployDeployment,
    PumpwoodDeployConfigMap, PumpwoodDeploy)
from pumpwood_deploy.abc import BasePumpwoodDeployMicroservice


# Kong deployment
kong_deployment = resources.files('pumpwood_deploy')\
    .joinpath('microservices/standard/resources/kong__deploy.yml')\
    .read_text(encoding='utf-8')
secret__kong = resources.files('pumpwood_deploy')\
    .joinpath('microservices/standard/resources/kong__secrets.yml')\
    .read_text(encoding='utf-8')

# RabbitMQ Deploy
rabbitmq_deployment = resources.files('pumpwood_deploy')\
    .joinpath('microservices/standard/resources/rabbitmq__deploy.yml')\
    .read_text(encoding='utf-8')
rabbitmq_secrets = resources.files('pumpwood_deploy')\
    .joinpath('microservices/standard/resources/rabbitmq__secrets.yml')\
    .read_text(encoding='utf-8')

# General secrets
model_secrets = resources.files('pumpwood_deploy')\
    .joinpath(
        'microservices/standard/'
        'resources/model_microservices__secrets.yml')\
    .read_text(encoding='utf-8')
secret__general = resources.files('pumpwood_deploy')\
    .joinpath(
        'microservices/standard/'
        'resources/general__secrets.yml')\
    .read_text(encoding='utf-8')

# Storage config and secrets
storage_config_map = resources.files('pumpwood_deploy')\
    .joinpath(
        'microservices/standard/'
        'resources/storage__config_map.yml')\
    .read_text(encoding='utf-8')
azure__storage_key_secrets = resources.files('pumpwood_deploy')\
    .joinpath(
        'microservices/standard/'
        'resources/storage__azure_secrets.yml')\
    .read_text(encoding='utf-8')
gcp__storage_key_secrets = resources.files('pumpwood_deploy')\
    .joinpath(
        'microservices/standard/'
        'resources/storage__gcp_empty_secrets.yml')\
    .read_text(encoding='utf-8')
aws__storage_key_secrets = resources.files('pumpwood_deploy')\
    .joinpath('microservices/standard/resources/storage__aws_secrets.yml')\
    .read_text(encoding='utf-8')


class StandardMicroservices(BasePumpwoodDeployMicroservice):
    """Deploy Kong, RabbitMQ, and shared storage resources."""

    def __init__(self,
                 rabbitmq_password: str,
                 rabbitmq_version: str,
                 model_user_password: str,
                 storage_bucket_name: str,
                 storage_deploy_args: PumpwoodDeployStorage | None,
                 hash_salt: str,
                 crypto_fernet_key: str,
                 kong_version: str,
                 kong_db_username: str,
                 kong_db_password: str,
                 kong_db_database: str,
                 kong_db_host: str,
                 kong_db_port: str,
                 rabbitmq_repository: str = 'docker.io/library',
                 kong_repository: str = 'andrebaceti'):
        """Initialize StandardMicroservices deployment configuration.

        Args:
            rabbitmq_password (str):
                Password for RabbitMQ.
            rabbitmq_version (str):
                Container image tag for RabbitMQ.
            model_user_password (str):
                Password for the model microservice user.
            storage_deploy_args (PumpwoodDeployStorage | None):
                Storage arguments object, or ``None`` when credentials
                are supplied by the Kubernetes provider role.
            storage_bucket_name (str):
                Bucket or container name used for flat file storage.
            hash_salt (str):
                Salt used for microservice security hash generation.
            crypto_fernet_key (str):
                Encryption key for Pumpwood crypto fields.
            kong_version (str):
                Container image tag for Kong.
            kong_db_username (str):
                Username for the Kong Postgres database.
            kong_db_password (str):
                Password for the Kong Postgres database.
            kong_db_database (str):
                Database name used by Kong.
            kong_db_host (str):
                Hostname of the Kong Postgres database.
            kong_db_port (str):
                Port of the Kong Postgres database.
            rabbitmq_repository (str):
                Docker repository for the RabbitMQ image. Defaults to
                ``docker.io/library``.
            kong_repository (str):
                Docker repository for the custom Kong image. Defaults to
                ``docker.io/library/andrebaceti``.
        """
        self.kong_repository = kong_repository
        self._gcp_credential_file = None

        # Set the storage configuration
        storage_type = self.set_storage_parameters(
            storage_deploy_args=storage_deploy_args)

        # General secrets
        self._hash_salt = base64.b64encode(
            hash_salt.encode()).decode()
        self._crypto_fernet_key = base64.b64encode(
            crypto_fernet_key.encode()).decode()
        self._model_user_password = base64.b64encode(
            model_user_password.encode()).decode()

        # RabbitMQ
        self.rabbitmq_repository = rabbitmq_repository
        self.rabbitmq_version = rabbitmq_version
        self._rabbitmq_password = base64.b64encode(
            rabbitmq_password.encode()).decode()

        # Storage secrets
        self.storage_type = storage_type
        self.storage_bucket_name = storage_bucket_name

        # Kong disk for postgres deploy
        self.kong_repository = kong_repository
        self.kong_version = kong_version
        self.kong_db_username = kong_db_username
        self.kong_db_database = kong_db_database
        self.kong_db_host = kong_db_host
        self.kong_db_port = kong_db_port
        self._kong_db_password = base64.b64encode(
            kong_db_password.encode()).decode()

    def set_storage_parameters(
                self, storage_deploy_args: PumpwoodDeployStorage | None
                ) -> Literal["aws_s3", "google_bucket", "azure_storage"] | None: # NOQA
        """Set storage credentials and parameters based on storage type.

        Args:
            storage_deploy_args (PumpwoodDeployStorage | None):
                Deployment storage configuration arguments.

        Returns:
            Literal["aws_s3", "google_bucket", "azure_storage"] | None:
                The storage type used by standard microservices.

        Raises:
            NotImplementedError:
                If storage_deploy_args is not a supported/implemented provider.
        """
        # Set default values for the storage parameters
        self._azure_storage_connection_string = base64.b64encode(
            "not_configured".encode()).decode()
        self._aws_access_key_id = base64.b64encode(
            "not_configured".encode()).decode()
        self._aws_secret_access_key = base64.b64encode(
            "not_configured".encode()).decode()

        if storage_deploy_args is None:
            return None

        if isinstance(storage_deploy_args, PumpwoodDeployStorageAzure):
            # It is possible to pass the credentials by the Kubernetes
            # provider role. In this case, the credentials are not encoded.
            storage_connection_string = storage_deploy_args\
                .storage_connection_string
            if storage_connection_string is None:
                return "azure_storage"

            # If passed, set the credentials and return the storage type.
            storage_connection_string = storage_connection_string.encode()
            self._azure_storage_connection_string = base64.b64encode(
                storage_connection_string).decode()
            return "azure_storage"

        if isinstance(storage_deploy_args, PumpwoodDeployStorageGCP):
            credential_file = storage_deploy_args.credential_file
            self._gcp_credential_file = credential_file
            return "google_bucket"

        if isinstance(storage_deploy_args, PumpwoodDeployStorageAWS):
            # It is possible to pass the credentials by the Kubernetes
            # provider role. In this case, the credentials are not encoded.
            access_key_id = storage_deploy_args.access_key_id
            secret_access_key = storage_deploy_args.secret_access_key
            if access_key_id is None or secret_access_key is None:
                return "aws_s3"

            # If passed, set the credentials and return the storage type.
            access_key_id = access_key_id.encode()
            secret_access_key = secret_access_key.encode()
            self._aws_access_key_id = base64.b64encode(
                access_key_id).decode()
            self._aws_secret_access_key = base64.b64encode(
                secret_access_key).decode()
            return "aws_s3"

        # Raise if another option is passed as arguments
        storage_type_name = storage_deploy_args.__class__.__name__
        msg = "storage_deploy_args not implemented: {storage_type_name}"\
            .format(storage_type_name=storage_type_name)
        raise NotImplementedError(msg)

    def create_deployment_file(self) -> list[PumpwoodDeploy]:
        """Create and format the lists of Kubernetes manifests.

        Returns:
            list[PumpwoodDeploy]:
                A list of deployment objects (secrets, deployments, and
                config maps) to apply to the Kubernetes cluster.
        """
        # RabbitMQ
        rabbitmq_deployment_formated = rabbitmq_deployment.format(
            repository=self.rabbitmq_repository, version=self.rabbitmq_version)
        secrets_text_formated = rabbitmq_secrets.format(
            password=self._rabbitmq_password)

        # Hash Salt
        secret_general_formated = secret__general.format(
            hash_salt=self._hash_salt,
            crypto_fernet_key=self._crypto_fernet_key)

        # Model microservice user
        microservice_model_secrets_formated = model_secrets.format(
            password=self._model_user_password)

        ############
        # Storages #
        storage_config_map_fmt = storage_config_map.format(
            storage_type=self.storage_type,
            storage_bucket_name=self.storage_bucket_name)

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
                name='rabbitmq__deployment',
                content=rabbitmq_deployment_formated,
                sleep=0),

            # General secrets
            PumpwoodDeploySecret(
                name='general__secrets', content=secret_general_formated,
                sleep=0),

            # General secret for all models
            PumpwoodDeploySecret(
                name='microsservice_model__secrets',
                content=microservice_model_secrets_formated,
                sleep=0),

            # Kong service mesh
            PumpwoodDeploySecret(
                name='kong__secrets', content=secret_kong_fmt,
                sleep=0),
            PumpwoodDeployDeployment(
                name='kong__deployment', content=kong_deployment_fmt,
                sleep=5),

            # Storage secrets and config
            PumpwoodDeployConfigMap(
                name='storage-config', content=storage_config_map_fmt,
                sleep=0),
            PumpwoodDeploySecret(
                name='azure__storage_key',
                content=azure__storage_key_secrets_fmt,
                sleep=0),
            PumpwoodDeploySecret(
                name='aws__storage_key',
                content=aws__storage_key_secrets_fmt,
                sleep=0)
        ]

        # Add deploy of the google credential file if set
        if self._gcp_credential_file is not None:
            deploy_list.append(
                PumpwoodDeploySecretFile(
                    name='gcp--storage-key', path=self._gcp_credential_file,
                    sleep=5))
        return deploy_list
