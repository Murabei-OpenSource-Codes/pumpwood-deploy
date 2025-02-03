"""load_balancer.py."""
import os
import ipaddress
import pkg_resources
from jinja2 import Template
from typing import List


nginx_gateway_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/api_gateway/'
    'resources/deploy__nginx_certbot.yml').read().decode()
nginx_gateway_no_ssl_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/api_gateway/'
    'resources/deploy__nginx_no_ssl.yml').read().decode()
nginx_gateway_secrets_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/api_gateway/'
    'resources/deploy__nginx_secrets.yml').read().decode()
external_service = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/api_gateway/'
    'resources/service__external.yml').read().decode()
internal_service = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/api_gateway/'
    'resources/service__internal.yml').read().decode()


class ApiGatewayCertbot:
    """Build deployment files for the NGINX Api Gateway with Certbot.

    API gateway will set CORS and other security headers for all
    application.

    Api Gateway Certbot will also add a https termination
    to application using Let's encript to generate a certificate
    associated with DNS name.
    """

    def __init__(self, gateway_public_ip: str, email_contact: str,
                 version: str,
                 root_redirect_url: str = "admin/pumpwood-auth-app/gui/",
                 health_check_url: str = "health-check/pumpwood-auth-app/",
                 server_name: str = "not_set",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 souce_ranges: List[str] = ["0.0.0.0/0"]):
        """__init__.

        Args:
            gateway_public_ip (str):
                Set the IP for the ApiGateway, when using
                AWS Elastic IP it must be passed it's id. It must have one
                Elastic IP for each public subnet on VPC used on K8s, values
                must be separated using coma, ex:
                    - "eipalloc-XXXXXX,eipalloc-YYYYY
            root_redirect_url (str):
                Path to redirect call at root.
            email_contact (str):
                E-mail contact for let's encript.
            version (str):
                Version of the API gateway.
            server_name (str):
                DNS name for the server.
            repository (str):
                Repository that will be used to retrieve Docker image.
            health_check_url (str):
                Url for the health checks.
            souce_ranges (List[str]):
                List of the IPs to restrict source
                conections to the ApiGateway. By default is 0.0.0.0/0, no
                restriction.
        """
        self.repository = repository
        self.gateway_public_ip = gateway_public_ip
        self.server_name = server_name
        self.email_contact = email_contact
        self.version = version
        self.health_check_url = health_check_url
        self.souce_ranges = souce_ranges
        self.base_path = os.path.dirname(__file__)
        self.root_redirect_url = root_redirect_url

    def create_deployment_file(self, kube_client, **kwargs):
        """Create_deployment_file.

        Args:
          kube_client:
            Client to communicate with Kubernets cluster.
          **kwargs:
            Copatibility with other versions.
        """
        nginx_gateway_deployment__formated = nginx_gateway_deployment.format(
            repository=self.repository,
            server_name=self.server_name,
            email_contact=self.email_contact,
            nginx_ssl_version=self.version,
            health_check_url=self.health_check_url,
            root_redirect_url=self.root_redirect_url)

        service__formated = None
        if ipaddress.ip_address(self.gateway_public_ip).is_private:
            service__formated = internal_service.format(
                public_ip=self.gateway_public_ip)
        else:
            external_service_template = Template(external_service)
            service__formated = external_service_template.render(
                public_ip=self.gateway_public_ip,
                firewall_ips=self.souce_ranges)

        to_return = [
            {'type': 'deploy', 'name': 'nginx-gateway__deploy',
             'content': nginx_gateway_deployment__formated, 'sleep': 0},
            {'type': 'services', 'name': 'nginx-gateway__endpoint',
             'content': service__formated, 'sleep': 0}]
        return to_return

#
# class ApiGatewaySecretsSSL:
#     """NGINX Gateway and Kong loadbalancer."""
#
#     def __init__(self, gateway_public_ip: str,
#                  version: str, ssl_secret_path: str,
#                  google_project_id: str, secret_id: str,
#                  health_check_url: str = "health-check/pumpwood-auth-app/",
#                  server_name: str = "not_set",
#                  repository: str = "gcr.io/repositorio-geral-170012",
#                  souce_ranges: list = ["0.0.0.0/0"]):
#         """
#         Build deployment files for the Kong ApiGateway.
#
#         Args:
#             gateway_public_ip (str): Set the IP for the ApiGateway.
#             version (str): Version of the API gateway.
#             ssl_secret_path (str): Path for the Google Credential to access
#                 the secret with the SSL credentials.
#             google_project_id (str): Project ID that stores the SSL
#                 credentials.
#             secret_id (str): Name of the secret that stores the SSL
#                 credentials.
#         Kwargs:
#             server_name (str): DNS name for the server.
#             health_check_url (str): Url for the health checks.
#         """
#         self.repository = repository
#         self.gateway_public_ip = gateway_public_ip
#         self.server_name = server_name
#         self.ssl_secret_path = ssl_secret_path
#         self.version = version
#         self.health_check_url = health_check_url
#         self.google_project_id = google_project_id
#         self.secret_id = secret_id
#         self.souce_ranges = souce_ranges
#         self.base_path = os.path.dirname(__file__)
#
#     def create_deployment_file(self):
#         """Create a deployment file."""
#         nginx_gateway_deployment__formated = \
#             nginx_gateway_secrets_deployment.format(
#                 repository=self.repository,
#                 server_name=self.server_name,
#                 nginx_ssl_version=self.version,
#                 health_check_url=self.health_check_url,
#                 google_project_id=self.google_project_id,
#                 secret_id=self.secret_id)
#
#         service__formated = None
#         if ipaddress.ip_address(self.gateway_public_ip).is_private:
#             service__formated = internal_service.format(
#                 public_ip=self.gateway_public_ip)
#         else:
#             external_service_template = Template(external_service)
#             service__formated = external_service_template.render(
#                 public_ip=self.gateway_public_ip,
#                 firewall_ips=self.souce_ranges)
#
#         to_return = [
#             {'type': 'secrets_file', 'name': 'ssl-credentials-key',
#              'path': self.ssl_secret_path, 'sleep': 0},
#             {'type': 'deploy', 'name': 'nginx-gateway__deploy',
#              'content': nginx_gateway_deployment__formated, 'sleep': 0},
#             {'type': 'services', 'name': 'nginx-gateway__endpoint',
#              'content': service__formated, 'sleep': 0}]
#         return to_return


class ApiGatewayCORSTerminaton:
    """Create a NGINX termination to add default CORS headers.

    This API Gateway will only add CORS and security headers to application,
    but it will not add HTTPs termination to aplication.

    To add HTTPs, set a upstrem HTTPs termination using cloud vendor
    loadbalancer.
    """

    def __init__(self, version: str,
                 root_redirect_url: str = "admin/pumpwood-auth-app/gui/",
                 health_check_url: str = "health-check/pumpwood-auth-app/",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 server_name: str = "localhost",
                 target_service: str = "load-balancer:8000",
                 target_health: str = "load-balancer:8001"):
        """Build deployment files for the Kong ApiGateway.

        Args:
            version (str):
                Version of the API gateway.
            root_redirect_url (str):
                To which URL root call "/" should be redirected.
                Default "admin/pumpwood-auth-app/gui/".
            health_check_url (str):
                Health check path for pod. Default for
                "health-check/pumpwood-auth-app/".
            repository (str):
                Reposity that will be used to retrieve docker image
                "gcr.io/repositorio-geral-170012".
            server_name (str):
                Name of the server at NGINX. Defaults "localhost"
            target_service (str):
                Target service on the reverse proxy. Defaults for
                "load-balancer:8000".
            target_health (str):
                Target server heath check path. Defaults for
                "load-balancer:8001".
        """
        self.root_redirect_url = root_redirect_url
        self.repository = repository
        self.version = version
        self.health_check_url = health_check_url
        self.server_name = server_name
        self.target_service = target_service
        self.target_health = target_health
        self.base_path = os.path.dirname(__file__)
        self.root_redirect_url = root_redirect_url

    def create_deployment_file(self, **kwargs):
        """Create_deployment_file.

        Args:,
            **kwargs:
                Backward compatibility.
        """
        nginx_gateway_deployment__formated = \
            nginx_gateway_no_ssl_deployment.format(
                repository=self.repository,
                nginx_ssl_version=self.version,
                health_check_url=self.health_check_url,
                server_name=self.server_name,
                target_service=self.target_service,
                target_health=self.target_health,
                root_redirect_url=self.root_redirect_url)

        to_return = [
            {'type': 'deploy', 'name': 'nginx_gateway_no_ssl__deploy',
             'content': nginx_gateway_deployment__formated, 'sleep': 0}, ]
        return to_return
