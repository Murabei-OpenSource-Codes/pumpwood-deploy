"""PumpWood Frontend Module."""

import os
# import base64
# from jinja2 import Template


class FrontEndMicroservice:
    """Create Angular front-end deploy filess."""

    def __init__(self, repository, version, gateway_public_ip):
        """__init__."""
        self.repository = repository
        self.version = version
        self.gateway_public_ip = gateway_public_ip

        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self):
        """create_deployment_file."""
        with open(os.path.join(self.base_path,
                  'resources_yml/frontend_deployment.yml'), 'r') as file:
            frontend_deployment_text = file.read()
        frontend_deployment_text_f = frontend_deployment_text.format(
            repository=self.repository,
            version=self.version,
            gateway_public_ip=self.gateway_public_ip)

        list_return = [
            {'type': 'deploy', 'name': 'pumpwood_frontend__deploy',
             'content': frontend_deployment_text_f, 'sleep': 10}]

        return list_return

    def end_points(self):
        """
        end_points.

        .
        """
        return self.end_points
