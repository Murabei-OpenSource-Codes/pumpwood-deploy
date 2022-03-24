"""load_balancer.py."""
import os
from jinja2 import Template
from typing import List
from .resources.resources_yml import (
    kong_postgres_volume, kong_postgres_deployment, kong_deployment,
    external_service, nginx_gateway_deployment)


class ApiGateway:
    """NGINX Gateway and Kong loadbalancer."""

    def __init__(self, gateway_public_ip: str, kong_db_disk_name: str,
                 kong_db_disk_size: str, email_contact: str,
                 nginx_ssl_version: str,
                 health_check_url: str = "health-check/pumpwood-auth-app/",
                 server_name: str = "not_set"):
        """
        Build deployment files for the Kong ApiGateway.

        Args:
            gateway_public_ip(str): Set the IP for the ApiGateway.
            kong_db_disk_name(str): Set the name of the disk for Kong Postgres.
            kong_db_disk_size(str): Set the size claimed from the Kong Postgres
                disk.
            email_contact (str): Contact email for let's encript.
            nginx_ssl_version (str): Version of the Nginx SSL api-gateway.

        Kwargs:
            server_name (str): DNS name for the server.
            health_check_url (str): Url for the health checks.
        """
        self.gateway_public_ip = gateway_public_ip
        self.kong_db_disk_name = kong_db_disk_name
        self.kong_db_disk_size = kong_db_disk_size
        self.server_name = server_name
        self.email_contact = email_contact
        self.nginx_ssl_version = nginx_ssl_version
        self.health_check_url = health_check_url

        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self):
        """Create a deployment file."""
        kong_postgres_volume__formated = kong_postgres_volume.format(
            disk_size=self.kong_db_disk_size, disk_name=self.kong_db_disk_name)
        kong_postgres_deployment__formated = kong_postgres_deployment
        kong_deployment__formated = kong_deployment

        nginx_gateway_deployment__formated = nginx_gateway_deployment.format(
            server_name=self.server_name,
            email_contact=self.email_contact,
            nginx_ssl_version=self.nginx_ssl_version,
            health_check_url=self.health_check_url)
        external_service__formated = external_service.format(
            public_ip=self.gateway_public_ip)

        to_return = [
            {'type': 'volume', 'name': 'kong__volume',
             'content': kong_postgres_volume__formated, 'sleep': 10},
            {'type': 'deploy', 'name': 'kong__postgres',
             'content': kong_postgres_deployment__formated, 'sleep': 0},
            {'type': 'deploy', 'name': 'kong__deploy',
             'content': kong_deployment__formated, 'sleep': 0},
            {'type': 'deploy', 'name': 'nginx-gateway__deploy',
             'content': nginx_gateway_deployment__formated, 'sleep': 0},
            {'type': 'services', 'name': 'nginx-gateway__endpoint',
             'content': external_service__formated, 'sleep': 0}]
        return to_return
