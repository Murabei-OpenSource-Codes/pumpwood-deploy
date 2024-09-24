"""
PumpWood Graph DataLake Microservice Deploy.

Graph Datalake Microservice is reposible for storing data that associate
two different modeling units with edge attributes.

It also can be used for recursive queries.
"""
import os
import base64
import pkg_resources


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_graph_datalake/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_graph_datalake/'
    'resources/deploy__app.yml').read().decode()
worker_num_edges = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_graph_datalake/'
    'resources/deploy__worker_num_edges.yml').read().decode()
worker_text_edges = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_graph_datalake/'
    'resources/deploy__worker_text_edges.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_graph_datalake/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodGraphDatalakeMicroservice:
    """PumpWoodGraphDatalakeMicroservice."""

    def __init__(self,
                 bucket_name: str,
                 app_version: str,
                 worker_num_version: str,
                 worker_text_version: str,
                 microservice_password: str = "microservice--graph-datalake",
                 db_username: str = "pumpwood",
                 db_password: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-graph-datalake",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_limits_memory: str = "1Gi",
                 test_db_limits_cpu: str = "1000m",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 worker_num_debug: str = "FALSE",
                 worker_num_replicas: int = 1,
                 worker_num_n_parallel: int = 4,
                 worker_num_chunk_size: int = 1000,
                 worker_num_query_limit: int = 1000000,
                 worker_num_limits_memory: str = "60Gi",
                 worker_num_limits_cpu: str = "12000m",
                 worker_num_requests_memory: str = "20Mi",
                 worker_num_requests_cpu: str = "1m",
                 worker_text_debug: str = "FALSE",
                 worker_text_replicas: int = 1,
                 worker_text_n_parallel: int = 4,
                 worker_text_chunk_size: int = 1000,
                 worker_text_query_limit: int = 1000000,
                 worker_text_limits_memory: str = "60Gi",
                 worker_text_limits_cpu: str = "12000m",
                 worker_text_requests_memory: str = "20Mi",
                 worker_text_requests_cpu: str = "1m"):
        """
        __init__.

        Args:
            microservice_password [str]:
                Password associated with microservice service user
                `microservice--graph-datalake`. Service user login will be
                avaiable only inside the cluster.
            bucket_name [str]:
                Name of the bucket that will be used at the Graph Datalake
                microservices.
            app_version [str]:
                Version of the application associated with Graph Datalake.
            worker_num_version [str]:
                Version of the worker for numerical edges for Graph Datalake
                microservices.
            worker_text_version [str]:
                Version of the worker for text edges for Graph Datalake
                microservices.
            db_username [str]:
                Username that will be used to connect with Postgres database.
                Defaul value `pumpwood`.
            db_password [str]:
                Password that will be used to connect with Postgres database.
                Defaul value `pumpwood`.
            db_host [str]:
                Host that will be used to connect with Postgres database.
                Defaul value `pumpwood`.
            db_port [str]:
                Port that will be used to connect with Postgres database.
                Defaul value `pumpwood`.
            db_database [str]:
                Database that will be used to connect with Postgres database.
                Defaul value `pumpwood`.
            repository [str]:
                Repository that will be used to fetch docker imagens for
                Pumpwood Graph Datalake.
            test_db_version [str]:
                Version associated with test database for Pumpwood Graph
                Datalake.
            test_db_repository [str]:
                Repository associated with test database for Pumpwood Graph
                Datalake.
            test_db_limits_memory [str]:
                Set a maximum memory consumption for test database. Values
                should be set using Gi (Gigabytes), Mi (Megabytes) and
                Ki (Kilobytes) notation.
            test_db_limits_cpu [str]:
                Set a maximum CPU consumption for test database. It is better
                to set maximum resources using 'm' mili CPUs as default.
                Ex.: limit consumption to 1 CPU `1000m`; limit consumption to
                1.5 CPU `1500m`; limit consumption to 0.5 CPU `500m`.
            app_debug [bool]:
                Set debug for application container.
            app_replicas [int]:
                Number of replicas associated with application.
            app_timeout [int]:
                Set in seconds timeout associated with application.
            app_workers [int]:
                Number of workers at gunicorn associated with application.
            app_limits_memory [str]:
                Set a maximum CPU consumption for application. Values
                should be set using Gi (Gigabytes), Mi (Megabytes) and
                Ki (Kilobytes) notation.
            app_limits_cpu [str]:
                Set a maximum CPU consumption for application. It is better
                to set maximum resources using 'm' mili CPUs as default.
                Ex.: limit consumption to 1 CPU `1000m`; limit consumption to
                1.5 CPU `1500m`; limit consumption to 0.5 CPU `500m`.
            app_requests_memory [str]:
                Set memory requested associated with each pod for applcation.
                Values should be set using Gi (Gigabytes), Mi (Megabytes) and
                Ki (Kilobytes) notation.
            app_requests_cpu [str]:
                Set CPU requested associated with each pod for applcation.
                It is better to set maximum resources using 'm' mili CPUs
                as default. Ex.: limit consumption to 1 CPU `1000m`; limit
                consumption to 1.5 CPU `1500m`; limit consumption to
                0.5 CPU `500m`.
            worker_num_debug [str]:
                Set debug for worker dataloader for numerical edges container.
            worker_num_replicas [str]:
                Number of replicas associated with worker for numerical edges
                container.
            worker_num_n_parallel [str]:
                Number of parallel requests when uploading data to database.
            worker_num_chunk_size [int]:
                Chunk size associated with payload sent to database. It limits
                number of rows that will be saved at a requests.
            worker_num_query_limit [int]:
                Limits the numbers of rows that will be fetched from database
                when uploading data to backend.
            worker_num_limits_memory [str]:
                Set a maximum Memory consumption for dataloader worker for
                numerical edges. Values should be set using Gi (Gigabytes),
                Mi (Megabytes) and Ki (Kilobytes) notation.
            worker_num_limits_cpu [str]:
                Set a maximum CPU consumption for dataloader worker for
                numerical edges. It is better
                to set maximum resources using 'm' mili CPUs as default.
                Ex.: limit consumption to 1 CPU `1000m`; limit consumption to
                1.5 CPU `1500m`; limit consumption to 0.5 CPU `500m`.
            worker_num_requests_memory [str]:
                Set memory requested associated with each pod for applcation.
                Values should be set using Gi (Gigabytes), Mi (Megabytes) and
                Ki (Kilobytes) notation.
            worker_num_requests_cpu [str]:
                Set CPU requested associated with each pod for applcation.
                It is better to set maximum resources using 'm' mili CPUs
                as default. Ex.: limit consumption to 1 CPU `1000m`; limit
                consumption to 1.5 CPU `1500m`; limit consumption to
                0.5 CPU `500m`.
            worker_text_debug [str]:
                Set debug for worker dataloader for text edges container.
            worker_text_replicas [str]:
                Number of replicas associated with worker for text edges
                container.
            worker_text_n_parallel [str]:
                Number of parallel requests when uploading data to database.
            worker_text_chunk_size [int]:
                Chunk size associated with payload sent to database. It limits
                number of rows that will be saved at a requests.
            worker_text_query_limit [int]:
                Limits the numbers of rows that will be fetched from database
                when uploading data to backend.
            worker_text_limits_memory [str]:
                Set a maximum Memory consumption for dataloader worker for
                text edges. Values should be set using Gi (Gigabytes),
                Mi (Megabytes) and Ki (Kilobytes) notation.
            worker_text_limits_cpu [str]:
                Set a maximum CPU consumption for dataloader worker for
                text edges. It is better
                to set maximum resources using 'm' mili CPUs as default.
                Ex.: limit consumption to 1 CPU `1000m`; limit consumption to
                1.5 CPU `1500m`; limit consumption to 0.5 CPU `500m`.
            worker_text_requests_memory [str]:
                Set memory requested associated with each pod for applcation.
                Values should be set using Gi (Gigabytes), Mi (Megabytes) and
                Ki (Kilobytes) notation.
            worker_text_requests_cpu [str]:
                Set CPU requested associated with each pod for applcation.
                It is better to set maximum resources using 'm' mili CPUs
                as default. Ex.: limit consumption to 1 CPU `1000m`; limit
                consumption to 1.5 CPU `1500m`; limit consumption to
                0.5 CPU `500m`.
        """
        self._db_password = base64.b64encode(
            db_password.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)

        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database

        self.repository = repository.rstrip("/")
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_version = app_version

        # App
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Worker numerical
        self.worker_num_version = worker_num_version
        self.worker_num_debug = worker_num_debug
        self.worker_num_replicas = worker_num_replicas
        self.worker_num_n_parallel = worker_num_n_parallel
        self.worker_num_chunk_size = worker_num_chunk_size
        self.worker_num_query_limit = worker_num_query_limit
        self.worker_num_limits_memory = worker_num_limits_memory
        self.worker_num_limits_cpu = worker_num_limits_cpu
        self.worker_num_requests_memory = worker_num_requests_memory
        self.worker_num_requests_cpu = worker_num_requests_cpu

        # Worker numerical
        self.worker_text_version = worker_text_version
        self.worker_text_debug = worker_text_debug
        self.worker_text_replicas = worker_text_replicas
        self.worker_text_n_parallel = worker_text_n_parallel
        self.worker_text_chunk_size = worker_text_chunk_size
        self.worker_text_query_limit = worker_text_query_limit
        self.worker_text_limits_memory = worker_text_limits_memory
        self.worker_text_limits_cpu = worker_text_limits_cpu
        self.worker_text_requests_memory = worker_text_requests_memory
        self.worker_text_requests_cpu = worker_text_requests_cpu

        # Database
        self.test_db_version = test_db_version
        self.test_db_repository = test_db_repository.rstrip("/")
        self.test_db_limits_memory = test_db_limits_memory
        self.test_db_limits_cpu = test_db_limits_cpu

    def create_deployment_file(self, kube_client, **kwargs):
        """
        Create deployment file.

        Args:
            kube_client:
                Client to communicate with Kubernets cluster.
        """
        secrets_text_formated = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version,
                limits_memory=self.test_db_limits_memory,
                limits_cpu=self.test_db_limits_cpu)

        # App deployment
        app_deployment_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.app_version,
                bucket_name=self.bucket_name,
                replicas=self.app_replicas,
                requests_memory=self.app_requests_memory,
                requests_cpu=self.app_requests_cpu,
                limits_cpu=self.app_limits_cpu,
                limits_memory=self.app_limits_memory,
                workers_timeout=self.app_timeout,
                n_workers=self.app_workers,
                debug=self.app_debug,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database)

        # Dataloader text edges
        worker_deployment_num_frmted = worker_num_edges.format(
            repository=self.repository,
            version=self.worker_num_version,
            bucket_name=self.bucket_name,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            n_parallel=self.worker_text_n_parallel,
            chunk_size=self.worker_text_chunk_size,
            query_limit=self.worker_text_query_limit,
            replicas=self.worker_text_replicas,
            requests_memory=self.worker_text_requests_memory,
            requests_cpu=self.worker_text_requests_cpu,
            limits_cpu=self.worker_text_limits_cpu,
            limits_memory=self.worker_text_limits_memory,
            debug=self.worker_text_debug)

        # Dataloader numerical edges
        worker_deployment_text_frmted = worker_text_edges.format(
            repository=self.repository,
            version=self.worker_text_version,
            bucket_name=self.bucket_name,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            n_parallel=self.worker_num_n_parallel,
            chunk_size=self.worker_num_chunk_size,
            query_limit=self.worker_num_query_limit,
            replicas=self.worker_num_replicas,
            requests_memory=self.worker_num_requests_memory,
            requests_cpu=self.worker_num_requests_cpu,
            limits_cpu=self.worker_num_limits_cpu,
            limits_memory=self.worker_num_limits_memory,
            debug=self.worker_num_debug)

        list_return = [{
            'type': 'secrets',
            'name': 'pumpwood_graph_datalake__secrets',
            'content': secrets_text_formated, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy',
                'name': 'pumpwood_graph_datalake__postgres',
                'content': deployment_postgres_text_f, 'sleep': 0})
        list_return.append({
            'type': 'deploy',
            'name': 'pumpwood_graph_datalake__deploy',
            'content': app_deployment_frmtd, 'sleep': 0})
        list_return.append({
            'type': 'deploy',
            'name': 'pumpwood_graph_datalake_num_dataloader__worker',
            'content': worker_deployment_num_frmted, 'sleep': 0})
        list_return.append({
            'type': 'deploy',
            'name': 'pumpwood_graph_datalake_text_dataloader__worker',
            'content': worker_deployment_text_frmted, 'sleep': 0})
        return list_return
