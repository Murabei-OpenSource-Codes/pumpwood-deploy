"""Login tests."""
import unittest
from pumpwood_deploy.metabase.deploy import (MetabaseMicroservice)
from pumpwood_deploy.test_aux.kubenets import validate_k8s_yml


class TestMetabaseMicroservice(unittest.TestCase):
    """Test user login."""

    load_balancer_address = "http://0.0.0.0:8080/"
    'Ip of the load balancer'
    apps_to_regenerate = ['pumpwood-auth-app']
    'Name of the apps to be regenerated after the test is over'

    def test__create_files(self):
        deploy_obj = MetabaseMicroservice(
            metabase_site_url="xxx",
            db_password="xxxx",
            embedding_secret_key="xxx",
            encryption_secret_key="xxx",
            db_usename="xxx",
            db_host="xxx",
            db_database="xxx",
            db_port="xxx",
            app_replicas="xxx",
            app_limits_memory="xxx",
            app_limits_cpu="xxx",
            app_requests_memory="xxx",
            app_requests_cpu="xxx")

        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 3)
        for x in results:
            validate_k8s_yml(x["content"])

    def test__create_files_with_test_database(self):
        deploy_obj = MetabaseMicroservice(
        metabase_site_url="xxx",
            db_password="xxxx",
            embedding_secret_key="xxx",
            encryption_secret_key="xxx",
            db_usename="xxx",
            db_host="xxx",
            db_database="xxx",
            db_port="xxx",
            app_replicas="xxx",
            app_limits_memory="xxx",
            app_limits_cpu="xxx",
            app_requests_memory="xxx",
            app_requests_cpu="xxx",
            test_db_version="xxx",
            test_db_repository="xxx")

        results = deploy_obj.create_deployment_file()
        self.assertEqual(len(results), 4)
        for x in results:
            validate_k8s_yml(x["content"])
