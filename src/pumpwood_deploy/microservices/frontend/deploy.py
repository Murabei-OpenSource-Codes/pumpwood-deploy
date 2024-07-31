"""Class to deploy Frontend Microservices."""
import os
import pkg_resources
import base64


deployment_yml = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/frontend/'
    'resources/deploy__frontend.yml').read().decode()

secrets_yml = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/frontend/'
    'resources/secrets.yml').read().decode()


class PumpwoodFrontEndMicroservice:
    """Deploy Pumpwood Main front-end microservices."""

    def __init__(self,
                 version: str,
                 gateway_public_ip: str,
                 microservice_password: str = "microservice--frontend",
                 debug: str = 'FALSE',
                 repository: str = "gcr.io/repositorio-geral-170012"):
        """
        Class constructor.

        Args:
            version [str]:
                Version of the front-end microservice.
            gateway_public_ip [str]:
                Address for the API gateway. It should be the IP or
                the DNS name for the application, it will be used to correct
                redirect request to end-point.
            microservice_password [str]:
                Microservice service user password that will be used to log
                at Pumpwood and register routes and services. Service
                user default name is `microservice--frontend`.
            debug [str]:
                Set if frontend is in debug mode or not. User 'TRUE'/'FALSE'
                strings to set this option.
            repository [str]:
                Repository from which the docker image
                `pumpwood-frontend-react` will be fetched.
        """
        self.repository = repository
        self.version = version
        self.gateway_public_ip = gateway_public_ip
        self.debug = debug
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self, **kwargs):
        """Create_deployment_file."""
        deployment_text_f = deployment_yml.format(
            repository=self.repository,
            gateway_public_ip=self.gateway_public_ip,
            debug=self.debug,
            version=self.version)

        secrets_text_f = secrets_yml.format(
            microservice_password=self._microservice_password)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_frontend__secrets',
             'content': secrets_text_f, 'sleep': 5},
            {'type': 'deploy', 'name': 'pumpwood_frontend__deploy',
             'content': deployment_text_f, 'sleep': 10},
        ]

        return list_return
