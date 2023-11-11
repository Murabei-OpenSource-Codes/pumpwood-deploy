"""Login tests."""
import unittest
from pumpwood_deploy.microservices.pumpwood_prediction.deploy import (
    PumpWoodPredictionMicroservice)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestPumpWoodPredictionMicroservice(unittest.TestCase):
    """Test user login."""

    def test__create_files(self):
        deploy_obj = PumpWoodPredictionMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_rawdata_version="xxxx",
            worker_dataloader_version="xxxx")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 4)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-prediction")

    def test__create_files_with_test_database(self):
        deploy_obj = PumpWoodPredictionMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_rawdata_version="xxxx",
            worker_dataloader_version="xxxx",
            test_db_version='xxx')

        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 5)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-prediction")
