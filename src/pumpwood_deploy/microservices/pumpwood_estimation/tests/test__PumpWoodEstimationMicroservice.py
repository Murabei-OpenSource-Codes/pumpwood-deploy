"""Login tests."""
import unittest
from pumpwood_deploy.microservices.pumpwood_estimation.deploy import (
    PumpWoodEstimationMicroservice)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestPumpWoodEstimationMicroservice(unittest.TestCase):
    """Test user login."""

    def test__create_files(self):
        deploy_obj = PumpWoodEstimationMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_version="xxx")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 3)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-estimation")

    def test__create_files_with_test_database(self):
        deploy_obj = PumpWoodEstimationMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_version="xxx",
            test_db_version='xxx')

        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 4)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-estimation")
