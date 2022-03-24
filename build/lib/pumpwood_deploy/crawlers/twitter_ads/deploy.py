"""Twitter Ads Crawler deployment module."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template


class TwitterAdsCrawler:
    """Class to help deployment of Twitter Ads Crawler."""

    def __init__(self, db_username, db_password, micro_username,
                 micro_password, app_consumer_key, app_consumer_secret,
                 user_access_token, user_access_token_secret, bucket_name,
                 disk_size, disk_name, postgres_public_ip, repository,
                 firewall_ips, workers_timeout, version_queue_manager,
                 version_puller, version_pusher):
        """
        __init__.

        Args:
            db_username (str): database username.
            db_password (str): database password.
            micro_username (str): microservice username.
            micro_password (str): microservice password.
            app_consumer_key (str): Twitter APP consumer key.
            app_consumer_secret (str): Twitter APP consumer secret.
            user_access_token (str): Twitter user token.
            user_access_token_secret (str): Twitter token secret.
            bucket_name (str): Name of the bucket on Cloud.
            disk_size (str): Disk size for postgres.
            disk_name (str): Disk name for postgres.
            postgres_public_ip (str): Public postres IP to use on load
                                      balancer.
            repository (str): Repository path.
            version_queue_manager (str): Version of the queue manager.
            version_puller (str): Version of the puller.
            version_pusher (str): Version of the pusher.
        """
        postgres_certificates = create_ssl_key_ssl_crt()

        self._db_username = base64.b64encode(db_username.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._micro_username = base64.b64encode(
            micro_username.encode()).decode()
        self._micro_password = base64.b64encode(
            micro_password.encode()).decode()

        self._app_consumer_key = base64.b64encode(
            app_consumer_key.encode()).decode()
        self._app_consumer_secret = base64.b64encode(
            app_consumer_secret.encode()).decode()

        self._user_access_token = base64.b64encode(
            user_access_token.encode()).decode()
        self._user_access_token_secret = base64.b64encode(
            user_access_token_secret.encode()).decode()

        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()

        self.postgres_public_ip = postgres_public_ip
        self.bucket_name = bucket_name
        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)

        self.repository = repository

        self.workers_timeout = workers_timeout
        self.firewall_ips = firewall_ips

        self.version_queue_manager = version_queue_manager
        self.version_puller = version_puller
        self.version_pusher = version_pusher

    def create_deployment_file(self):
        """Create Twitter Ads deployment files."""
        with open(os.path.join(self.base_path, 'resources_yml/secrets.yml'),
                  'r') as file:
            secrets_text = file.read()
        secrets_text_formated = secrets_text.format(
            db_username=self._db_username,
            db_password=self._db_password,
            micro_username=self._micro_username,
            micro_password=self._micro_password,
            app_consumer_key=self._app_consumer_key,
            app_consumer_secret=self._app_consumer_secret,
            user_access_token=self._user_access_token,
            user_access_token_secret=self._user_access_token_secret,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt,)

        with open(os.path.join(self.base_path, 'resources_yml/volume_postgres.yml'),
                  'r') as file:
            volume_postgres_text = file.read()
        volume_postgres_text_formated = volume_postgres_text.format(
            disk_size=self.disk_size,
            disk_name=self.disk_name)

        with open(os.path.join(self.base_path,
                               'resources_yml/deployment_postgres.yml'),
                  'r') as file:
            deployment_postgres_text = file.read()

        with open(os.path.join(self.base_path,
                               'resources_yml/deployment_queue_manager.yml'),
                  'r') as file:
            deployment_queue_manager_text = file.read()
        deployment_queue_manager_text_formated = \
            deployment_queue_manager_text.format(
                repository=self.repository,
                bucket_name=self.bucket_name,
                version=self.version_queue_manager,
                workers_timeout=self.workers_timeout)

        with open(os.path.join(self.base_path, 'resources_yml/deployment_puller.yml'),
                  'r') as file:
            deployment_puller_text = file.read()
        deployment_puller_text_formated = deployment_puller_text.format(
            repository=self.repository, bucket_name=self.bucket_name,
            version=self.version_puller)

        with open(os.path.join(self.base_path, 'resources_yml/deployment_pusher.yml'),
                  'r') as file:
            deployment_pusher_text = file.read()
        deployment_pusher_text_formated = deployment_pusher_text.format(
            repository=self.repository, bucket_name=self.bucket_name,
            version=self.version_pusher)

        with open(os.path.join(self.base_path, 'resources_yml/services.yml'),
                  'r') as file:
            services_text_formated = file.read()

        list_return = [{
                'type': 'services',
                'name': 'crawler__twitter_ads__services',
                'content': services_text_formated, 'sleep': 0},
            {
                'type': 'secrets',
                'name': 'crawler__twitter_ads__secrets',
                'content': secrets_text_formated, 'sleep': 5},
            {
                'type': 'volume', 'name': 'crawler__twitter_ads__volume',
                'content': volume_postgres_text_formated, 'sleep': 10},
            {
                'type': 'deploy',
                'name': 'crawler__twitter_ads__postgres',
                'content': deployment_postgres_text, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__twitter_ads__queue_manager',
                'content': deployment_queue_manager_text_formated, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__twitter_ads__puller',
                'content': deployment_puller_text_formated, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__twitter_ads__pusher',
                'content': deployment_pusher_text_formated, 'sleep': 0},
            ]

        if self.firewall_ips and self.postgres_public_ip:
            with open(os.path.join(self.base_path,
                                   'resources_yml/services__load_balancer.jinja2'),
                      'r') as file:
                services__load_balancer_template = Template(file.read())
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)

            list_return.append({
                'type': 'services',
                'name': 'crawler__twitter_ads__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0})
        return list_return

    def end_points(self):
        """Return microservices end-points."""
        return self.end_points
