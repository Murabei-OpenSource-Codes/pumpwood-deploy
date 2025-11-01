"""Login tests."""
import unittest
from pumpwood_deploy.microservices.pumpwood_datalake.deploy import (
    PumpWoodDatalakeMicroservice)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestPumpWoodDatalakeMicroservice(unittest.TestCase):
    """Test user login."""

    def test__create_files(self):
        deploy_obj = PumpWoodDatalakeMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_version="xxxx")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 3)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-datalake")

    def test__create_files_with_test_database(self):
        deploy_obj = PumpWoodDatalakeMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_version="xxxx",
            test_db_version='xxx')

        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 4)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-datalake")
