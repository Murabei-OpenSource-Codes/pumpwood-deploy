"""Tests for standard microservice deployment manifests."""
import unittest
from pumpwood_deploy.microservices.standard.deploy import (
    StandardMicroservices)
from pumpwood_deploy.type import (
    PumpwoodDeploySecretFile, PumpwoodDeployStorageGCP)


class TestStandardMicroservices(unittest.TestCase):
    """Validate generated standard microservice Kubernetes manifests."""

    def test__create_files(self):
        """Ensure generated manifests include expected deploy objects."""
        deploy_obj = StandardMicroservices(
            rabbitmq_password="xxx",
            rabbitmq_version="3.12",
            model_user_password="xxx",
            storage_type="google_bucket",
            storage_deploy_args=PumpwoodDeployStorageGCP(
                credential_file="key-storage.json"),
            storage_bucket_name="test-bucket",
            hash_salt="xxx",
            crypto_fernet_key="xxx",
            kong_version="3.4",
            kong_db_username="kong",
            kong_db_password="kong",
            kong_db_database="kong",
            kong_db_host="postgres-kong",
            kong_db_port="5432")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 10)
        for item in results:
            self.assertTrue(hasattr(item, 'name'))
            if isinstance(item, PumpwoodDeploySecretFile):
                continue
            self.assertTrue(hasattr(item, 'content'))
            self.assertTrue(len(item.content) > 0)
