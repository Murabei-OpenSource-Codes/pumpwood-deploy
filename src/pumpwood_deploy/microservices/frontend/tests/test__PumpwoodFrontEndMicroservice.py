"""Login tests."""
import unittest
from pumpwood_deploy.microservices.frontend.deploy import (
    PumpwoodFrontEndMicroservice)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestPumpwoodFrontEndMicroservice(unittest.TestCase):
    """Test user login."""

    def test__create_files(self):
        deploy_obj = PumpwoodFrontEndMicroservice(
            version="xxx", gateway_public_ip="xxx",
            microservice_password="xxx",)
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 2)
        for x in results:
            validate_k8s_yml(
                x["content"], microservice_name="pumpwood-frontend")
