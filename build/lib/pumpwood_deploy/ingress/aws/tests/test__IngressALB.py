"""Login tests."""
import unittest
from pumpwood_deploy.ingress.aws.deploy import (IngressALB)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestIngressALB(unittest.TestCase):
    """Test user login."""

    load_balancer_address = "http://0.0.0.0:8080/"
    'Ip of the load balancer'
    apps_to_regenerate = ['pumpwood-auth-app']
    'Name of the apps to be regenerated after the test is over'

    def test__create_files(self):
        deploy_obj = IngressALB(
            alb_name="xxxxx", group_name="xxxxx",
            certificate_arn="xxxxx", service_name="apigateway-nginx",
            service_port=80, host=None, path="/")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 3)
        for x in results:
            validate_k8s_yml(x["content"])
