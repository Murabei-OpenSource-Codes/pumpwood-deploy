"""Class to deploy Frontend Microservices."""
import os
import pkg_resources
import base64
from typing import Union, List, Any


deployment_yml = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/streamlit/' +
    'resources/deploy__frontend.yml').read().decode()
secrets_yml = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/streamlit/' +
    'resources/secrets.yml').read().decode()


class PumpwoodStreamlitMicroservices:
    """Deploy Streamlit Dashboards."""

    def __init__(self,
                 dashboard_images: List[dict],
                 microservice_password: str = "microservice--streamlit",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 ):
        """
        Class constructor.

        Args:
            version [str]:
                Version of the front-end microservice.
            microservice_password [str]:
                Microservice service user password that will be used to log
                at Pumpwood and register routes and services. Service
                user default name is `microservice--frontend`.
            repository [str]:
                Repository from which the docker image
                `pumpwood-frontend-react` will be fetched.
            dashboard_images [List[dict]]:
                List of dictonary with keys.
                - **image:** Image associated with dashboards to be deployed.
                - **version:** Version of the dashboard,
                - **deployment_name:** Name of the deployment at k8s.
        """
        self.repository = repository
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self.dashboard_images = dashboard_images

    def create_deployment_file(self, **kwargs):
        """Create_deployment_file."""
        secrets_text_f = secrets_yml.format(
            microservice_password=self._microservice_password)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_frontend__secrets',
             'content': secrets_text_f, 'sleep': 5}, ]
        for dash in self.dashboard_images:
            deployment_yml_fmt = deployment_yml.format(
                repository=self.repository, image=dash['image'],
                version=dash['version'], name=dash['deployment_name'],)
            name = "pumpwood_streamlit__{name}".format(
                name=dash['deployment_name'])
            list_return.append(
                {'type': 'secrets', 'name': name,
                 'content': deployment_yml_fmt, 'sleep': 0})
        return list_return
