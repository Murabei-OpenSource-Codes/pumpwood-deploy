"""Login tests."""
import unittest
from pumpwood_deploy.microservices.api_gateway.deploy import (
    ApiGateway, CORSTerminaton)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestPumpwoodFrontEndMicroservice(unittest.TestCase):
    """Test user login."""

    def test__create_files_ApiGateway(self):
        deploy_obj = ApiGateway(
            gateway_public_ip="179.98.71.190",
            email_contact="teste@teste.com",
            version="0.0")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 2)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="apigateway-nginx")

    # def test__create_files_ApiGatewaySecretsSSL(self):
    #     deploy_obj = ApiGateway(
    #         gateway_public_ip="20.000.000",
    #         email_contact="teste@teste.com",
    #         version="0.0"
    #         google_project_id: str, secret_id)
    #     results = deploy_obj.create_deployment_file()
    #     self.assertEqual(len(results), 2)
    #     for x in results:
    #         validate_k8s_yml(
    #             x["content"],
    #             microservice_name="apigateway-nginx")

    def test__create_files_CORSTerminaton(self):
        deploy_obj = CORSTerminaton(version="0.0")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 1)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="apigateway-nginx")
