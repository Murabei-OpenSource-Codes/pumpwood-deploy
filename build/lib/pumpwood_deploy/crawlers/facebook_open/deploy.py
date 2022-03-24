import os
import base64
from microservices.postgres.postgres import create_ssl_key_ssl_crt

class FacebookOpenMicroservice:
    def __init__(self, db_username, db_password, micro_username
        ,  micro_password, facebook_app_id, facebook_app_secret
        , disk_size, disk_name, postgres_public_ip, repository
        , version_queue_manager, version_worker, version_pusher):

        postgres_certificates = create_ssl_key_ssl_crt()
        
        self._db_username = base64.b64encode(db_username.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._micro_username = base64.b64encode(micro_username.encode()).decode()
        self._micro_password = base64.b64encode(micro_password.encode()).decode()
        
        self._facebook_app_id = base64.b64encode(facebook_app_id.encode()).decode()
        self._facebook_app_secret = base64.b64encode(facebook_app_secret.encode()).decode()

        self._ssl_crt = base64.b64encode(postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(postgres_certificates['ssl_key'].encode()).decode()
        self.postgres_public_ip = postgres_public_ip
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.getcwd() + '/microservices/facebook_open/'

        self.repository = repository
        self.version_queue_manager = version_queue_manager
        self.version_worker = version_worker
        self.version_pusher = version_pusher

        
    def create_deployment_file(self):
        with open(self.base_path + 'resources_yml/secrets.yml', 'r') as file:
            secrets_text = file.read()
        secrets_text_formated = secrets_text.format(
              db_username=self._db_username
            , db_password=self._db_password
            , micro_username=self._micro_username
            , micro_password=self._micro_password
            , facebook_app_id=self._facebook_app_id
            , facebook_app_secret=self._facebook_app_secret
            , ssl_key=self._ssl_crt
            , ssl_crt=self._ssl_key)

        with open(self.base_path + 'resources_yml/deployment_postgres.yml', 'r') as file:
            deployment_postgres_text = file.read()
        deployment_postgres_text_formated = deployment_postgres_text.format(
              disk_size=self.disk_size
            , disk_name=self.disk_name)

        with open(self.base_path + 'resources_yml/deployment_queue_manager.yml', 'r') as file:
            deployment_queue_manager_text = file.read()
        deployment_queue_manager_text_formated = deployment_queue_manager_text.format(
                repository=self.repository
              , version=self.version_queue_manager)

        with open(self.base_path + 'resources_yml/deployment_worker.yml', 'r') as file:
            deployment_worker_text = file.read()
        deployment_worker_text_formated = deployment_worker_text.format(
                repository=self.repository
              , version=self.version_worker)

        with open(self.base_path + 'resources_yml/deployment_pusher.yml', 'r') as file:
            deployment_pusher_text = file.read()
        deployment_pusher_text_formated = deployment_pusher_text.format(
                repository=self.repository
              , version=self.version_pusher)

        with open(self.base_path + 'resources_yml/resources/pusher_datalake_integration.py', 'r') as file:
            pusher_datalake_integration_config = file.read()

        with open(self.base_path + 'resources_yml/services.yml', 'r') as file:
            services_text = file.read()
        services_text_formated = services_text.format(postgres_public_ip=self.postgres_public_ip)

        return [{'type': 'services', 'name': 'facebook_open__services', 'content': services_text_formated, 'sleep': 0}
              , {'type': 'secrets', 'name': 'facebook_open__secrets', 'content': secrets_text_formated, 'sleep': 5}
              , {'type': 'configmap', 'name': 'facebook-open-datalake-integration', 'content': pusher_datalake_integration_config, 'file_name': 'facebook-open-datalake-integration.py', 'sleep': 5, 'keyname': 'datalake_integration.py'}
              , {'type': 'deploy' , 'name': 'facebook_open__postgres', 'content': deployment_postgres_text_formated, 'sleep': 20}
              , {'type': 'deploy' , 'name': 'facebook_open__queue_manager', 'content': deployment_queue_manager_text_formated, 'sleep': 0}
              , {'type': 'deploy' , 'name': 'facebook_open__worker', 'content': deployment_worker_text_formated, 'sleep': 0}
              , {'type': 'deploy' , 'name': 'facebook_open__pusher', 'content': deployment_pusher_text_formated, 'sleep': 0}
        ]

    def end_points(self):
        return self.end_points

