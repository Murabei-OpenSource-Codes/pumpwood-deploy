"""Google Trends data crawler module."""
import os
from .resources_yml.yml_resources import (
    decision_model_yml)


class PumpwoodDecisionModel:
    """Class to help deployment of Decision models."""

    def __init__(self, decision_model_name: str, version: str,
                 repository: str):
        """
        __init__.

        Args:
            decision_model_name (str): Name of the decision model.
            version (str): Model version.
            version (str): Version of the model.
            repository (str): Repository path.
        """
        self.base_path = os.path.dirname(__file__)
        self.decision_model_name = decision_model_name
        self.repository = repository
        self.version = version

    def create_deployment_file(self):
        """Create Google Trends deployment files."""
        decision_model_frmted = decision_model_yml.format(
            decision_model_name=self.decision_model_name,
            repository=self.repository,
            version=self.version)

        return [{
                'type': 'deploy',
                'name': 'decision_model__{}__worker'.format(
                    self.decision_model_name),
                'content': decision_model_frmted, 'sleep': 0}]

    def end_points(self):
        """Return microservices end-points."""
        return self.end_points
