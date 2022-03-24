"""Facebook Ads Crawler."""
import os
import base64
from pumpwood_deploy.microservices.postgres.postgres import \
    create_ssl_key_ssl_crt
from jinja2 import Template


class FacebookAdsCrawler:
    """Deploy Facebook Ads Crawler."""

    def __init__(self, db_username, db_password, micro_username,
                 micro_password, facebook_app_id, facebook_app_secret,
                 facebook_app_token, bucket_name, disk_size, disk_name,
                 postgres_public_ip, firewall_ips, workers_timeout, repository,
                 version_queue_manager, version_puller, version_pusher):
        """
        Create new deploy FacebookAdsCrawler object.

        Args:
            db_username (str): Database username.
            db_password (str): Database password.
            micro_username (str): Microservice username.
            micro_password (str): Microservice password.
            facebook_app_id (str): Facebook app id.
            facebook_app_secret (str): Facebook app secret.
            facebook_app_token (str): Facebook app usertoken.
            disk_size (str) : Disk size to claim.
            disk_name (str) : Disk name to claim.
            postgres_public_ip (str): IP that will be used in postgres
                                      loadbalancer
            workers_timeout (str): Timeout for wokers in guinicorn.
            repository (str): Repository from which pull images.
            version_queue_manager (str): Version of the queue manager app.
            version_puller (str): Version of the puller worker.
            version_pusher (str): Version of the pusher worker.

        """
        postgres_certificates = create_ssl_key_ssl_crt()

        self._db_username = base64.b64encode(db_username.encode()).decode()
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self._micro_username = base64.b64encode(
            micro_username.encode()).decode()
        self._micro_password = base64.b64encode(
            micro_password.encode()).decode()
        self._bucket_name = bucket_name

        self._facebook_app_id = base64.b64encode(
            facebook_app_id.encode()).decode()
        self._facebook_app_secret = base64.b64encode(
            facebook_app_secret.encode()).decode()
        self._facebook_app_token = base64.b64encode(
            facebook_app_token.encode()).decode()

        self._ssl_crt = base64.b64encode(
            postgres_certificates['ssl_crt'].encode()).decode()
        self._ssl_key = base64.b64encode(
            postgres_certificates['ssl_key'].encode()).decode()

        self.postgres_public_ip = postgres_public_ip
        self.firewall_ips = firewall_ips

        self.disk_size = disk_size
        self.disk_name = disk_name
        self.base_path = os.path.dirname(__file__)

        self.workers_timeout = workers_timeout

        self.repository = repository
        self.version_queue_manager = version_queue_manager
        self.version_puller = version_puller
        self.version_pusher = version_pusher

    def create_deployment_file(self):
        """Create deployment file."""
        with open(self.base_path + '/resources_yml/secrets.yml', 'r') as file:
            secrets_text = file.read()
        secrets_text_formated = secrets_text.format(
            db_username=self._db_username,
            db_password=self._db_password,
            micro_username=self._micro_username,
            micro_password=self._micro_password,
            facebook_app_id=self._facebook_app_id,
            facebook_app_secret=self._facebook_app_secret,
            facebook_app_token=self._facebook_app_token,
            ssl_key=self._ssl_key,
            ssl_crt=self._ssl_crt,)

        with open(os.path.join(
                self.base_path, 'resources_yml/volume_postgres.yml'), 'r') as file:
            volume_postgres_text = file.read()
        volume_postgres_text_formated = volume_postgres_text.format(
            disk_size=self.disk_size,
            disk_name=self.disk_name)

        with open(os.path.join(
                self.base_path, 'resources_yml/deployment_postgres.yml'),
                'r') as file:
            deployment_postgres_text = file.read()

        with open(os.path.join(
                self.base_path, 'resources_yml/deployment_queue_manager.yml'),
                'r') as file:
            deployment_queue_manager_text = file.read()
        deployment_queue_manager_text_formated = \
            deployment_queue_manager_text.format(
                repository=self.repository,
                bucket_name=self._bucket_name,
                version=self.version_queue_manager,
                workers_timeout=self.workers_timeout)

        with open(os.path.join(
                self.base_path, 'resources_yml/deployment_puller.yml'), 'r') as file:
            deployment_puller_text = file.read()
        deployment_puller_text_formated = deployment_puller_text.format(
                bucket_name=self._bucket_name,
                repository=self.repository,
                version=self.version_puller)

        with open(os.path.join(
                  self.base_path, 'resources_yml/deployment_pusher.yml'),
                  'r') as file:
            deployment_pusher_text = file.read()
        deployment_pusher_text_formated = deployment_pusher_text.format(
            bucket_name=self._bucket_name,
            repository=self.repository,
            version=self.version_pusher,)

        with open(os.path.join(
                self.base_path, 'resources_yml/services.yml'), 'r') as file:
            services_text = file.read()
        services_text_formated = services_text.format(
            postgres_public_ip=self.postgres_public_ip)

        list_return = [{
                'type': 'services',
                'name': 'crawler__facebook_ads__services',
                'content': services_text_formated, 'sleep': 0},
            {
                'type': 'secrets',
                'name': 'crawler__facebook_ads__secrets',
                'content': secrets_text_formated, 'sleep': 5},
            {
                'type': 'volume', 'name': 'crawler__facebook_ads__volume',
                'content': volume_postgres_text_formated, 'sleep': 10},
            {
                'type': 'deploy',
                'name': 'crawler__facebook_ads__postgres',
                'content': deployment_postgres_text, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__facebook_ads__queue_manager',
                'content': deployment_queue_manager_text_formated, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__facebook_ads__puller',
                'content': deployment_puller_text_formated, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'crawler__facebook_ads__pusher',
                'content': deployment_pusher_text_formated, 'sleep': 0},
            ]

        if self.firewall_ips and self.postgres_public_ip:
            with open(os.path.join(
                    self.base_path, 'resources_yml/services__load_balancer.jinja2'),
                        'r') as file:
                services__load_balancer_template = Template(file.read())
            svcs__load_balancer_text = services__load_balancer_template.render(
                postgres_public_ip=self.postgres_public_ip,
                firewall_ips=self.firewall_ips)

            list_return.append({
                'type': 'services',
                'name': 'crawler__facebook_ads__services_loadbalancer',
                'content': svcs__load_balancer_text, 'sleep': 0
            })

        return list_return

    def end_points(self):
        """Return microservices end-points."""
        return self.end_points
