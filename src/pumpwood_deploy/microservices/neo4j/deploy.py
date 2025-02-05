"""Deploy Neo4J database."""
import base64
import pkg_resources


deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/neo4j/'
    'resources/deploy.yml').read().decode()
secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/neo4j/'
    'resources/secrets.yml').read().decode()


class Neo4jDatabase:
    """Class to deploy Neo4J Database."""

    def __init__(self,
                 db_password: str,
                 disk_size: str,
                 disk_name: str,
                 db_username: str = 'neo4j',
                 version: str = "4.4.23",
                 limits_memory: str = "60Gi",
                 limits_cpu: str = "12000m",
                 requests_memory: str = "20Mi",
                 requests_cpu: str = "1m"):
        """Deploy Neo4j database.

        Args:
            version (str):
                Version of the Neo4J database.
            db_username (str):
                Username that will be used at Neo4J admin.
            db_password (str):
                Password that will be used at Neo4J admin..
            disk_size (str):
                Size of the disk to be claimed.
            disk_name (str):
                Disk name.
            limits_memory (str):
                Neo4J container memory limit.
            limits_cpu (str):
                Neo4J cotainer CPU limit.
            requests_memory (str):
                Neo4J container memory request.
            requests_cpu (str):
                Neo4J cotainer CPU request.
        """
        # Database username and password are passed as a single string
        neo4j_admin_credentials = '{username}/{password}'.format(
            username=db_username, password=db_password)
        self.db_auth = base64.b64encode(
            neo4j_admin_credentials.encode()).decode()

        self.disk_size = disk_size
        self.disk_name = disk_name

        self.version = version
        self.limits_memory = limits_memory
        self.limits_cpu = limits_cpu
        self.requests_memory = requests_memory
        self.requests_cpu = requests_cpu

    def create_deployment_file(self, kube_client):
        """Create_deployment_file.

        Args:
          kube_client:
            Client to communicate with Kubernets cluster.
        """
        volume_text_f = kube_client.create_volume_yml(
            disk_name=self.disk_name, disk_size=self.disk_size,
            volume_claim_name="neo4j-data")
        deployment_f = deployment.format(
            volume_claim_name="neo4j-data",
            version=self.version,
            requests_memory=self.requests_memory,
            requests_cpu=self.requests_cpu,
            limits_memory=self.limits_memory,
            limits_cpu=self.limits_cpu)
        secrets_text_f = secrets.format(db_auth=self.db_auth)

        list_return = [
            {'type': 'secrets', 'name': 'neo4j__secrets',
             'content': secrets_text_f, 'sleep': 5},
            {'type': 'volume', 'name': 'neo4j__volume',
             'content': volume_text_f, 'sleep': 10},
            {'type': 'deploy', 'name': 'neo4j__database',
             'content': deployment_f, 'sleep': 20}]
        return list_return
