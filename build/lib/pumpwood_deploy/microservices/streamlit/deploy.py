"""Class to deploy Frontend Microservices."""
import pkg_resources
import base64
from typing import List


deployment_yml = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/streamlit/' +
    'resources/deploy__dashboard.yml').read().decode()
deployment_storage_yml = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/streamlit/' +
    'resources/deploy__dashboard_storage.yml').read().decode()
secrets_yml = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/streamlit/' +
    'resources/secrets.yml').read().decode()


class PumpwoodStreamlitMicroservices:
    """Deploy Streamlit Dashboards."""

    def __init__(self,
                 dashboard_images: List[dict],
                 microservice_password: str = "microservice--streamlit", # NOQA
                 repository: str = "gcr.io/repositorio-geral-170012"):
        """Class constructor.

        Args:
            version (str):
                Version of the front-end microservice.
            microservice_password (str):
                Microservice service user password that will be used to log
                at Pumpwood and register routes and services. Service
                user default name is `microservice--frontend`.
            repository (str):
                Repository from which the docker image
                `pumpwood-frontend-react` will be fetched.
            dashboard_images (List[dict]):
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
                {'type': 'deploy', 'name': name,
                 'content': deployment_yml_fmt, 'sleep': 0})
        return list_return


class PumpwoodStreamlitSecret:
    """Deploy Streamlit Secret for dashboard."""

    def __init__(self,
                 microservice_password: str = "microservice--streamlit"): # NOQA
        """Class constructor.

        Args:
            version (str):
                Version of the front-end microservice.
            microservice_password (str):
                Microservice service user password that will be used to log
                at Pumpwood and register routes and services. Service
                user default name is `microservice--frontend`.
            repository (str):
                Repository from which the docker image
                `pumpwood-frontend-react` will be fetched.
            dashboard_images (List[dict]):
                List of dictonary with keys.
                - **image:** Image associated with dashboards to be deployed.
                - **version:** Version of the dashboard,
                - **deployment_name:** Name of the deployment at k8s.
        """
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

    def create_deployment_file(self, **kwargs):
        """Create_deployment_file."""
        secrets_text_f = secrets_yml.format(
            microservice_password=self._microservice_password)

        list_return = [
            {'type': 'secrets', 'name': 'pumpwood_streamlit__secrets',
             'content': secrets_text_f, 'sleep': 5}, ]
        return list_return


class PumpwoodStreamlitDashboard:
    """Deploy Streamlit dashboard."""

    def __init__(self,
                 image: str, version: str,
                 repository: str = "gcr.io/repositorio-geral-170012",):
        """Class constructor.

        It is necessary to deploy streamlit secrets before deploy dashboards.

        Args:
            image (str):
                Name of the image of the dashboard.
            version (str):
                Version of the image of the dashboard.
            repository (str):
                Repository from which the docker image
                `pumpwood-frontend-react` will be fetched.
        """
        self.repository = repository
        self.image = image
        self.version = version
        self.repository = repository

    def create_deployment_file(self, **kwargs):
        """Create_deployment_file."""
        deployment_yml_fmt = deployment_yml.format(
            repository=self.repository, image=self.image,
            version=self.version)
        name = "pumpwood_streamlit__{name}".format(
            name=self.image)
        return [
            {'type': 'deploy', 'name': name,
             'content': deployment_yml_fmt, 'sleep': 0}
        ]


class PumpwoodStreamlitWithStorageDashboard:
    """Deploy Streamlit dashboard with connection to project storage.

    If not necessary do not deploy the dashboard with connection to storage,
    this will lead to a security risks.
    """

    def __init__(self,
                 image: str, version: str, bucket_name: str,
                 repository: str = "gcr.io/repositorio-geral-170012",):
        """Class constructor.

        It is necessary to deploy streamlit secrets before deploy dashboards.

        Args:
            image (str):
                Name of the image of the dashboard.
            version (str):
                Version of the image of the dashboard.
            bucket_name (str):
                Name of the bucket used on dashboard.
            repository (str):
                Repository from which the docker image
                `pumpwood-frontend-react` will be fetched.
        """
        self.repository = repository
        self.image = image
        self.version = version
        self.repository = repository
        self.bucket_name = bucket_name

    def create_deployment_file(self, **kwargs):
        """Create_deployment_file."""
        deployment_yml_fmt = deployment_storage_yml.format(
            repository=self.repository, image=self.image,
            version=self.version, bucket_name=self.bucket_name)
        name = "pumpwood_streamlit__{name}".format(
            name=self.image)
        return [
            {'type': 'deploy', 'name': name,
             'content': deployment_yml_fmt, 'sleep': 0}
        ]
