"""Login tests."""
import unittest
from pumpwood_deploy.microservices.pumpwood_complex_datalake.deploy import (
    PumpWoodComplexDatalakeMicroservice)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestPumpWoodComplexDatalakeMicroservice(unittest.TestCase):
    """Test user login."""

    def test__create_files(self):
        deploy_obj = PumpWoodComplexDatalakeMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_datalake_dataloader_version="xxxx",
            worker_simple_dataloader_version="xxxx",
            worker_complex_dataloader_version="xxxx",)
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 5)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-complex-datalake")

    def test__create_files_with_test_database(self):
        deploy_obj = PumpWoodComplexDatalakeMicroservice(
            microservice_password="xxxx",
            bucket_name="xxxx",
            app_version="xxxx",
            worker_datalake_dataloader_version="xxxx",
            worker_simple_dataloader_version="xxxx",
            worker_complex_dataloader_version="xxxx",
            test_db_version='xxx')

        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 6)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-complex-datalake")
