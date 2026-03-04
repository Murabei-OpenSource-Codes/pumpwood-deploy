"""Login tests."""
import unittest
from pumpwood_deploy.microservices.pumpwood_auth.deploy import (
    PumpWoodAuthMicroservice)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestPumpWoodAuthMicroservice(unittest.TestCase):
    """Test user login."""

    def test__create_files(self):
        deploy_obj = PumpWoodAuthMicroservice(
            secret_key="8540",
            db_username="pumpwood",
            db_password="test-password",
            db_host="postgres-single",
            db_port="5432",
            db_database="pumpwood_auth",
            microservice_password="microservice--auth",
            email_host_user="teste1",
            email_host_password="teste2",
            bucket_name="test-pumpwood",
            app_version="0.90",
            static_version="0.5")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 3)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-auth")

    def test__create_files_with_test_database(self):
        deploy_obj = PumpWoodAuthMicroservice(
            secret_key="8540",
            db_username="pumpwood",
            db_password="test-password",
            db_host="postgres-single",
            db_port="5432",
            db_database="pumpwood_auth",
            microservice_password="microservice--auth",
            email_host_user="teste1",
            email_host_password="teste2",
            bucket_name="test-pumpwood",
            app_version="0.90",
            static_version="0.5",
            test_db_version="0.0")

        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 4)
        for x in results:
            validate_k8s_yml(
                x["content"],
                microservice_name="pumpwood-auth")
