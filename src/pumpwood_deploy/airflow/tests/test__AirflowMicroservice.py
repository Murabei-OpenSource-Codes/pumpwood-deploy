"""Login tests."""
import unittest
from pumpwood_deploy.airflow.deploy import AirflowMicroservice
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestAirflowMicroservice(unittest.TestCase):
    """Test user login."""

    load_balancer_address = "http://0.0.0.0:8080/"
    'Ip of the load balancer'
    apps_to_regenerate = ['pumpwood-auth-app']
    'Name of the apps to be regenerated after the test is over'

    def test__create_files(self):
        deploy_obj = AirflowMicroservice(
             db_password="xxxx",
             microservice_password="xxxx",
             secret_key="xxxx",
             fernet_key="xxxx",
             k8s_pods_namespace="xxxx",
             bucket_name="xxxx",
             disk_name="xxxx",
             disk_size="xxxx",
             git_ssh_private_key_path="xxxx",
             git_ssh_public_key_path="xxxx",
             git_server="xxxx",
             git_repository="xxxx",
             git_branch="xxx")
        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 6)
        for x in results:
            if x["type"] != "secrets_file":
                validate_k8s_yml(
                    x["content"],
                    microservice_name="airflow")
