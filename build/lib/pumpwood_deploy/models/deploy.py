"""Google Trends data crawler module."""
import os
from .resources_yml.yml_resources import (
    app_yml, estimation_yml, prediction_yml)


class PumpwoodModels:
    """
    Class to help deployment of StatsmodelsGLMModels.
    """

    def __init__(self, model_type: str, version: str,
                 bucket_name: str,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 workers_timeout: int = 300):
        """
        __init__.

        Args:
            model_type (str): Model type.
            bucket_name (str): Name of the bucket to be used.
            version (str): Version of the model.
        Kwargs:
            repository (str): Repository path.
            workers_timeout (int): time in seconds to guinicorn wait for
                worker response.
        """
        self.base_path = os.path.dirname(__file__)
        self.model_type = model_type
        self.bucket_name = bucket_name
        self.repository = repository
        self.workers_timeout = workers_timeout
        self.version = version

    def create_deployment_file(self):
        """Create Google Trends deployment files."""
        deployment_app = app_yml.format(
            model_type=self.model_type,
            bucket_name=self.bucket_name,
            repository=self.repository,
            version=self.version,
            workers_timeout=self.workers_timeout)

        deployment_estimation = estimation_yml.format(
            model_type=self.model_type,
            bucket_name=self.bucket_name,
            repository=self.repository,
            version=self.version)

        deployment_prediction = prediction_yml.format(
            model_type=self.model_type,
            bucket_name=self.bucket_name,
            repository=self.repository,
            version=self.version)

        return [
            {
                'type': 'deploy',
                'name': 'models__{}__app'.format(self.model_type),
                'content': deployment_app, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'models__{}__estimation'.format(self.model_type),
                'content': deployment_estimation, 'sleep': 0},
            {
                'type': 'deploy',
                'name': 'models__{}__prediction'.format(self.model_type),
                'content': deployment_prediction, 'sleep': 0}, ]

    def end_points(self):
        """Return microservices end-points."""
        return self.end_points
