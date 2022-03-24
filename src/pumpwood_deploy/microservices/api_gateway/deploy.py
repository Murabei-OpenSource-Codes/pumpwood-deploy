"""load_balancer.py."""
import os
import ipaddress
from jinja2 import Template
from typing import List
from pumpwood_deploy.microservices.api_gateway.resources.yml_resources import (
    external_service, internal_service,
    nginx_gateway_deployment, nginx_gateway_secrets_deployment)


class ApiGateway:
    """NGINX Gateway and Kong loadbalancer."""

    def __init__(self, gateway_public_ip: str, email_contact: str,
                 version: str,
                 health_check_url: str = "health-check/pumpwood-auth-app/",
                 server_name: str = "not_set"):
        """
        Build deployment files for the Kong ApiGateway.

        Args:
            gateway_public_ip(str): Set the IP for the ApiGateway.
            email_contact(str): E-mail contact for let's encript.
            version (str): Version of the API gateway.

        Kwargs:
            server_name (str): DNS name for the server.
            health_check_url (str): Url for the health checks.
        """
        self.gateway_public_ip = gateway_public_ip
        self.server_name = server_name
        self.email_contact = email_contact
        self.version = version
        self.health_check_url = health_check_url

        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self):
        """Create a deployment file."""
        nginx_gateway_deployment__formated = nginx_gateway_deployment.format(
            server_name=self.server_name,
            email_contact=self.email_contact,
            nginx_ssl_version=self.version,
            health_check_url=self.health_check_url)

        service__formated = None
        if ipaddress.ip_address(self.gateway_public_ip).is_private:
            service__formated = internal_service.format(
                public_ip=self.gateway_public_ip)
        else:
            service__formated = external_service.format(
                public_ip=self.gateway_public_ip)

        to_return = [
            {'type': 'deploy', 'name': 'nginx-gateway__deploy',
             'content': nginx_gateway_deployment__formated, 'sleep': 0},
            {'type': 'services', 'name': 'nginx-gateway__endpoint',
             'content': service__formated, 'sleep': 0}]
        return to_return


class ApiGatewaySecretsSSL:
    """NGINX Gateway and Kong loadbalancer."""

    def __init__(self, gateway_public_ip: str,
                 version: str, ssl_secret_path: str,
                 google_project_id: str, secret_id: str,
                 health_check_url: str = "health-check/pumpwood-auth-app/",
                 server_name: str = "not_set"):
        """
        Build deployment files for the Kong ApiGateway.

        Args:
            gateway_public_ip (str): Set the IP for the ApiGateway.
            version (str): Version of the API gateway.
            ssl_secret_path (str): Path for the Google Credential to access
                the secret with the SSL credentials.
            google_project_id (str): Project ID that stores the SSL
                credentials.
            secret_id (str): Name of the secret that stores the SSL
                credentials.
        Kwargs:
            server_name (str): DNS name for the server.
            health_check_url (str): Url for the health checks.
        """
        self.gateway_public_ip = gateway_public_ip
        self.server_name = server_name
        self.ssl_secret_path = ssl_secret_path
        self.version = version
        self.health_check_url = health_check_url
        self.google_project_id = google_project_id
        self.secret_id = secret_id
        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self):
        """Create a deployment file."""
        nginx_gateway_deployment__formated = \
            nginx_gateway_secrets_deployment.format(
                server_name=self.server_name,
                nginx_ssl_version=self.version,
                health_check_url=self.health_check_url,
                google_project_id=self.google_project_id,
                secret_id=self.secret_id)

        service__formated = None
        if ipaddress.ip_address(self.gateway_public_ip).is_private:
            service__formated = internal_service.format(
                public_ip=self.gateway_public_ip)
        else:
            service__formated = external_service.format(
                public_ip=self.gateway_public_ip)

        to_return = [
            {'type': 'secrets_file', 'name': 'ssl-credentials-key',
             'path': self.ssl_secret_path, 'sleep': 0},
            {'type': 'deploy', 'name': 'nginx-gateway__deploy',
             'content': nginx_gateway_deployment__formated, 'sleep': 0},
            {'type': 'services', 'name': 'nginx-gateway__endpoint',
             'content': service__formated, 'sleep': 0}]
        return to_return
