"""Create standard deploy and secrets."""
import base64
import pkg_resources


kong_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/deploy__kong.yml').read().decode()
rabbitmq_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/deploy__rabbitmq.yml').read().decode()
rabbitmq_secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/secrets__rabbitmq.yml').read().decode()
model_secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/secrets__model_microservices.yml').read().decode()
rabbitmq_secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/secrets__rabbitmq.yml').read().decode()
hash_salt = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/secret__salt.yml').read().decode()
kong_postgres_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/postgres__kong.yml').read().decode()
azure__storage_key_secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/secrets__azure_storage.yml').read().decode()
gcp__storage_key_secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/secrets__gpc_storage_empty.yml').read().decode()
aws__storage_key_secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/secrets__aws_storage.yml').read().decode()
storage_config_map = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/standard/'
    'resources/config_map__storage.yml').read().decode()


class StandardMicroservices:
    """Create StandardMicroservices.

    Create RabbitMQ deployment and secrets, storage bucket key secret.

    """

    def __init__(self, hash_salt: str, rabbit_password: str,
                 model_user_password: str, storage_type: str,
                 storage_deploy_args: str, kong_db_disk_name: str = None,
                 kong_db_disk_size: str = None,
                 kong_repository: str = "gcr.io/repositorio-geral-170012"):
        """__init__.

        Args:
            model_user_password (str):
                User associated with models password.
            hash_salt (str):
                Hash salt of hash identification at the
                microservices.
            rabbit_password (str):
                rabbit_password for rabbitMQ login.
            bucket_key_path (str):
                Path to bucket JSON key.
            storage_type (str):
                Storage provider must be in [
                'azure_storage', 'google_bucket', 'aws_s3'], correpond to the
                provider os the flat file storage system.
            storage_deploy_args (str):
                Args used to access storage at the
                pods. Each provider must have diferent arguments:
                    - azure_storage:
                        - `azure_storage_connection_string`: Set conenction
                        string to a blob storage.
                    - google_bucket:
                        - `credential_file`: Set a path to a credetial file
                        of a service user with access to the bucket that will
                        be used at the deployment.
                    # aws_s3:
                        - `aws_access_key_id`: Access key of the service user
                        with access to the s3 used in deployment.
                        - `aws_secret_access_key`: Access secret of the
                        service user with access to the s3 used in deployment.
            kong_repository (str):
                Docker image repository for custom Kong docker Image.
            kong_db_disk_name (str):
                Kong postgres disk name, usually not set for test purposes.
            kong_db_disk_size (str):
                Kong postgres disk size, usually not set for test purposes.
        """
        self.kong_repository = kong_repository
        self._gcp_credential_file = None
        self._azure_storage_connection_string = base64.b64encode(
            "not_configured".encode()).decode()
        self._aws_access_key_id = base64.b64encode(
            "not_configured".encode()).decode()
        self._aws_secret_access_key = base64.b64encode(
            "not_configured".encode()).decode()
        # Using Azure blob storage for flat files
        if storage_type == "azure_storage":
            is_valid = (
                "storage_connection_string" not in storage_deploy_args.keys())
            if is_valid:
                raise Exception(
                    "Azure storage must have storage_connection_string " +
                    "args.")
            self._azure_storage_connection_string = base64.b64encode(
                storage_deploy_args[
                    "storage_connection_string"].encode()).decode()

        # Using GCP Storage Buckets storage for flat files
        elif storage_type == "google_bucket":
            credential_file = storage_deploy_args.get("credential_file")
            if type(credential_file) is not str:
                raise Exception(
                    "GCP storage must have credential_file args.")

            # Deploy at containers will use a file named as key-storage.json
            # using a different name for de the will result on deploy with
            # not found file error.
            is_valid = credential_file.endswith('key-storage.json')
            if not is_valid:
                msg = (
                    "Key storage file must be named 'key-storage.json', "
                    "change file name in order to deploy work.")
                raise Exception(msg)
            self._gcp_credential_file = credential_file

        # Using AWS S3 for flat files
        elif storage_type == "aws_s3":
            if_clause = (
                "access_key_id" not in storage_deploy_args.keys()) or (
                "secret_access_key" not in storage_deploy_args.keys())
            if if_clause:
                raise Exception(
                    "AWS storage must have aws_access_key_id and "
                    "aws_secret_access_key args.")
            self._aws_access_key_id = base64.b64encode(
                storage_deploy_args["access_key_id"].encode()).decode()
            self._aws_secret_access_key = base64.b64encode(
                storage_deploy_args["secret_access_key"].encode()).decode()

        # if other... not implemented
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

        # Kong disk for postgres deploy
        self.kong_db_disk_name = kong_db_disk_name
        self.kong_db_disk_size = kong_db_disk_size

    def create_deployment_file(self, kube_client=None):
        """Create deployment file.

        Args:
            kube_client:
                Client to communicate with Kubernets cluster.
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

        kong_postgres_volume_formated = None
        if kube_client is not None:
            kong_postgres_volume_formated = kube_client.create_volume_yml(
                disk_name=self.kong_db_disk_name,
                disk_size=self.kong_db_disk_size,
                volume_claim_name="postgres-kong-database")
        else:
            print("!! kube_client is None skiping kong disk creation !!")

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

        # Kong load-balancer
        kong_deployment_fmt = kong_deployment.format(
            repository=self.kong_repository)

        deploy_list = [
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
             'content': microservice_model_secrets_formated, 'sleep': 5}]

        if kong_postgres_volume_formated is not None:
            deploy_list.append(
                {'type': 'volume', 'name': 'load_balancer__volume',
                 'content': kong_postgres_volume_formated, 'sleep': 10})
        deploy_list.extend([
            {'type': 'deploy', 'name': 'load_balancer__postgres',
             'content': kong_postgres_deployment, 'sleep': 0},
            {'type': 'deploy', 'name': 'load_balancer__app',
             'content': kong_deployment_fmt, 'sleep': 0}])
        return deploy_list
