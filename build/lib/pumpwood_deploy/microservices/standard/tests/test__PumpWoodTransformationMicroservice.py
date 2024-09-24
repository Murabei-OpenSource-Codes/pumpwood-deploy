"""Login tests."""
import unittest
from pumpwood_deploy.microservices.standard.deploy import (
    StandardMicroservices)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestStandardMicroservices(unittest.TestCase):
    """Test user login."""

    def test__create_files(self):
        deploy_obj = StandardMicroservices(
            hash_salt="xxx",
            rabbit_password="xxx",
            model_user_password="xxx",
            storage_type="google_bucket",
            storage_deploy_args={"credential_file": "credential.json"})
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 10)
        for x in results:
            if x["type"] != "secrets_file":
                validate_k8s_yml(x["content"])
