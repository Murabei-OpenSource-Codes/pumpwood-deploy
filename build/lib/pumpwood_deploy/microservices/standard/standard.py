import os
import base64
from .resources.yml__resorces import (
    rabbitmq_deployment, rabbitmq_secrets, model_secrets, hash_salt,
    kong_postgres_volume, kong_postgres_deployment, kong_deployment)
from .resources.postgres_init_configmap import (postgres_init_configmap)


class StandardMicroservices:
    """
    Create StandardMicroservices.

    Create RabbitMQ deployment and secrets, postgres-init-configmap config map
    for postgres initiation and storage bucket key secret.

    """

    def __init__(self, hash_salt: str, rabbit_username: str,
                 rabbit_password: str, model_user_password: str,
                 bucket_key_path: str, kong_db_disk_name: str,
                 kong_db_disk_size: str):
        """
        __init__.

        Args:
            hash_salt (str): Hash salt.
            rabbit_username (str): rabbit_username for rabbitMQ login.
            rabbit_password (str): rabbit_password for rabbitMQ login.
            beatbox_version (str): Beatbox version.
            beatbox_config_path (str): Path to json configuration of beatbox
                calls.
            bucket_key_path (str): Path to bucket JSON key.
        """
        self._hash_salt = base64.b64encode(
            hash_salt.encode()).decode()
        self._rabbit_username = base64.b64encode(
            rabbit_username.encode()).decode()
        self._rabbit_password = base64.b64encode(
            rabbit_password.encode()).decode()
        self._model_user_password = base64.b64encode(
            model_user_password.encode()).decode()
        self.end_points = []

        self.base_path = os.path.dirname(__file__)

        if not os.path.isfile(bucket_key_path):
            raise Exception("Bucket-Key path does not exist: %s" % (
                bucket_key_path, ))

        self.bucket_key_path = bucket_key_path
        self.kong_db_disk_name = kong_db_disk_name
        self.kong_db_disk_size = kong_db_disk_size

    def create_deployment_file(self):
        """create_deployment_file."""
        ##########
        # RabbitMQ
        secrets_text_formated = rabbitmq_secrets.format(
            username=self._rabbit_username, password=self._rabbit_password)

        ###########
        # Hash Salt
        hash_salt_formated = hash_salt.format(
            hash_salt=self._hash_salt)

        #########################
        # Model microservice user
        microservice_model_secrets_formated = model_secrets.format(
            password=self._model_user_password)

        kong_postgres_volume_formated = kong_postgres_volume.format(
            disk_name=self.kong_db_disk_name,
            disk_size=self.kong_db_disk_size)

        return [
            # RabbitMQ
            {'type': 'secrets', 'name': 'rabbitmq__secrets',
             'content': secrets_text_formated, 'sleep': 5},
            {'type': 'deploy', 'name': 'rabbitmq__deployment',
             'content': rabbitmq_deployment, 'sleep': 0},

            # Postgres
            {'type': 'configmap', 'name': 'postgres-init-configmap',
             'content': postgres_init_configmap,
             'file_name': 'server_init.sh', 'sleep': 5},

            # Hash salt
            {'type': 'secrets', 'name': 'hash_salt__secrets',
             'content': hash_salt_formated, 'sleep': 5},

            # Bucket
            {'type': 'secrets_file', 'name': 'bucket-key',
             'path': self.bucket_key_path, 'sleep': 5},

            # Model microservice
            {'type': 'secrets', 'name': 'microsservice_model__secrets',
             'content': microservice_model_secrets_formated, 'sleep': 5},

            # Kong loadbalancer
            {'type': 'volume', 'name': 'load_balancer__volume',
             'content': kong_postgres_volume_formated, 'sleep': 10},
            {'type': 'deploy', 'name': 'load_balancer__postgres',
             'content': kong_postgres_deployment, 'sleep': 0},
            {'type': 'deploy', 'name': 'load_balancer__app',
             'content': kong_deployment, 'sleep': 0}]
