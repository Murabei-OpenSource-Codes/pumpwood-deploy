"""PumpWood Auth Module."""
import pkg_resources
import os
import base64
from typing import Union, List, Any


secrets = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/secrets.yml').read().decode()
app_deployment = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/deploy__app.yml').read().decode()
auth_admin_static = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/deploy__static.yml').read().decode()
auth_log_worker = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/deploy__log_worker.yml').read().decode()
test_postgres = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'microservices/pumpwood_auth/'
    'resources/postgres__test.yml').read().decode()


class PumpWoodAuthMicroservice:
    """Deploy PumpWood Auth Microservice.

    Pumpwood Auth Microservice is reponsible for make avaiable autorization
    end-points for Pumpwood based Systems.

    If also make avaiable routes for registering Kong services and routes
    which can be used to add new microservice to Pumpwood stack.

    It is possible to use a test database for deploying or a connection with
    postgres database.

    Deploy example with test database:
    ```python
    PumpWoodAuthMicroservice(
    secret_key="8540",
    email_host_user="teste1",
    email_host_password="teste2",
    bucket_name="qualidadecompradev",

    # App
    repository="qualidadedecompra.azurecr.io",
    app_replicas=1,
    app_version=os.getenv('PUMPWOOD_AUTH_APP'),
    app_debug="TRUE",

    # Static
    static_repository="qualidadedecompra.azurecr.io",
    static_version=os.getenv('PUMPWOOD_AUTH_STATIC'),

    # Test Database
    test_db_repository="qualidadedecompra.azurecr.io",
    test_db_version=os.getenv('TEST_DB_PUMPWOOD_AUTH'),
    test_db_limits_memory="2Gi",
    test_db_limits_cpu="2000m"))
    ```
    """

    def __init__(self,
                 secret_key: str,
                 email_host_user: str,
                 email_host_password: str,
                 bucket_name: str,
                 app_version: str,
                 static_version: str,
                 microservice_password: str = "microservice--auth", # NOQA
                 db_username: str = "pumpwood",
                 db_password: str = "pumpwood", # NOQA
                 db_database: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-auth",
                 db_port: str = "5432",
                 app_csrf_trusted_origins: str = '[]',
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 worker_debug: str = "FALSE",
                 worker_log_version: str = None,
                 worker_log_disk_name: str = None,
                 worker_log_disk_size: str = None,
                 worker_trino_catalog: str = None,
                 repository: str = "gcr.io/repositorio-geral-170012",
                 static_repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_version: str = None,
                 test_db_repository: str = "gcr.io/repositorio-geral-170012",
                 test_db_limits_memory: str = "1Gi",
                 test_db_limits_cpu: str = "1000m",
                 mfa_application_name: str = "Pumpwood",
                 mfa_token_expiration_interval: str = "60",  # NOQA
                 mfa_twilio_sender_phone_number: str = "",
                 mfa_twilio_account_sid: str = "",
                 mfa_twilio_auth_token: str = "",
                 sso__redirect_url: str = "",
                 sso__provider: str = "",
                 sso__authorization_url: str = "",
                 sso__token_url: str = "",
                 sso__client_id: str = "",
                 sso__secret: str = ""):
        """Deploy PumpWood Auth Microservice.

        Args:
            app_csrf_trusted_origins (str):
                List of CSRF trusted origins, if is passed as a JSON list
                of allowed trusted origins. Most of the case, it is
                just the domain associated with the deploy.
            secret_key (str):
                Hash salt used to generate password hash saved on database.
            microservice_password (str):
                Password associated with service user `microservice--auth`.
            db_username (str):
                Database connection username.
            db_password (str):
                Auth DB password.
            db_host (str):
                Database connection host.
            db_port (str):
                Database connection port.
            db_database (str):
                Database connection database.

            bucket_name (str):
                Name of the bucket, s3 or storage that will be associated with
                pumpwood auth. The same bucket can be used by different
                microservice, each one will save data.
            email_host_user (str):
                Auth email conection username for Django send emails.
            email_host_password (str):
                Auth email conection password for Django send emails.
            repository (str):
                Repository to pull auth images from. It will be pulled
                application (pumpwood-auth-app), logs worker
                (pumpwood-auth-log-worker).

            app_debug (str):
                Flag if application will be setted as debug mode.
            app_version (str):
                Version of the auth microservice application.
            app_timeout (int):
                Timeout limit set in seconds for auth application.
            app_workers (int):
                Number of workers spanned at gunicorn for Auth Application.
            app_limits_memory (str):
                Auth application memory consumption limit.
            app_limits_cpu (str):
                Auth application CPU consumption limit.
            app_requests_memory (str):
                Auth application memory request.
            app_requests_cpu (str):
                Auth application CPU request.
            app_replicas (int):
                Number of replicas for application deployment.

            static_version (str):
                Version of the image with static file for service javascript,
                logos, fonts and other statics data.
            static_repository (str):
                Repository to pull static image (pumpwood-auth-static) from.

            worker_log_version (str):
                Version of the loging worker. If log worker is not set,
                it will not be deployed and log information will be printed on
                auth stdout.
            worker_debug (str):
                If log worker is set on debug mode. Accepts 'FALSE' and 'TRUE'
                options.
            worker_log_disk_name (str):
                Name of the disk that will be attached to log worker to save
                unprocessed log data.
            worker_log_disk_size (str):
                Size of the disk that will be attached to log worker.
            worker_trino_catalog (str):
                Trino catalog that will be used to map log data information.

            test_db_version (str):
                Set a test database with version. If not set test database
                will not be deployed.
            test_db_repository (str):
                Define a repository for the test database.
            test_db_limits_memory (str):
                Limits for test database resources. Default 1Gi.
            test_db_limits_cpu (str):
                Limits for test databas resources. Default 1000m.

            worker_log_version (str):
                Version of the log worker to deploy. If not set worker will
                not be deployed.
            worker_log_disk_name (str):
                Name of the disk to be used on worker deploy.
            worker_log_disk_size (str):
                Size of the disk allocated to worker
                log container.
            worker_trino_catalog (str):
                Trino catalog to query for logs on
                storage.

            mfa_application_name (str):
                Name of the application at SMS MFA message. If not set MFA
                authentication using SMS will not be avaiable at Pumpwood.
            mfa_token_expiration_interval (str):
                MFA token expiration interval in seconds. Default 300 seconds
                (5 minutes).
            mfa_twilio_sender_phone_number (str):
                Phone that Twillio will use to send SMS. If None,
                MFA using Twillio SMS will be disable.
            mfa_twilio_account_sid (str):
                Twillio account id used to send SMS. If None, MFA using
                Twillio SMS will be disable.
            mfa_twilio_auth_token (str):
                Twillio auth token id used to sendo SMS. If None, MFA using
                Twillio SMS will be disable.

            sso__redirect_url (str):
                URL that will be used for redirecting the oauth2 after login.
            sso__provider (str):
                Provides associated with oauth2, so far only `microsoft-entra`
                have been implemented.
            sso__authorization_url (str):
                URL associated with autorization for oauth2.
            sso__token_url (str):
                URL to fetch token data after authentication.
            sso__client_id (str):
                Secret associated with SSO client_id.
            sso__secret (str):
                Secret associated with SSO sso__secret.
        """
        self._secret_key = base64.b64encode(secret_key.encode()).decode()
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()
        self._email_host_user = base64.b64encode(
            email_host_user.encode()).decode()
        self._email_host_password = base64.b64encode(
            email_host_password.encode()).decode()
        self.bucket_name = bucket_name
        self.base_path = os.path.dirname(__file__)

        # Database
        self.db_username = db_username
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database

        # App
        self.repository = (
            repository + "/"
            if repository is not None else "")
        self.static_repository = (
            static_repository + "/"
            if static_repository is not None else "")
        self.app_version = app_version
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu
        self.app_csrf_trusted_origins = app_csrf_trusted_origins

        # Static
        self.static_version = static_version

        # Postgres
        self.test_db_version = test_db_version
        self.test_db_repository = (
            test_db_repository + "/"
            if test_db_repository is not None else "")
        self.test_db_limits_memory = test_db_limits_memory
        self.test_db_limits_cpu = test_db_limits_cpu

        # Log Worker
        self.worker_trino_catalog = worker_trino_catalog
        self.worker_debug = worker_debug
        self.worker_log_version = worker_log_version
        self.worker_log_disk_name = worker_log_disk_name
        self.worker_log_disk_size = worker_log_disk_size

        # MFA
        self.mfa_application_name = mfa_application_name
        self.mfa_token_expiration_interval = mfa_token_expiration_interval
        self.mfa_twilio_sender_phone_number = mfa_twilio_sender_phone_number
        self._mfa_twilio_account_sid = \
            base64.b64encode(mfa_twilio_account_sid.encode()).decode()
        self._mfa_twilio_auth_token = \
            base64.b64encode(mfa_twilio_auth_token.encode()).decode()

        # SSO
        self.sso__redirect_url = sso__redirect_url
        self.sso__provider = sso__provider
        self.sso__authorization_url = sso__authorization_url
        self.sso__token_url = sso__token_url
        self._sso__client_id = \
            base64.b64encode(sso__client_id.encode()).decode()
        self._sso__secret = \
            base64.b64encode(sso__secret.encode()).decode()

    def create_deployment_file(self, kube_client=None, **kwargs) -> List[dict]:
        """
        Create_deployment_file.

        Args:
            kube_client [Kubernets]:
                Instance of `kubernets.kubernets.Kubernets` object to help
                attacing disks to pods and other Kubernets operations.
        """
        rabbitmq_log = "FALSE" if self.worker_log_version is None else "TRUE"
        secrets_text_f = secrets.format(
            db_password=self._db_password,
            microservice_password=self._microservice_password,
            email_host_user=self._email_host_user,
            email_host_password=self._email_host_password,
            secret_key=self._secret_key,
            mfa_twilio_account_sid=self._mfa_twilio_account_sid,
            mfa_twilio_auth_token=self._mfa_twilio_auth_token,
            sso__client_id=self._sso__client_id,
            sso__secret=self._sso__secret)

        deployment_auth_app_text_f = app_deployment.format(
            repository=self.repository,
            version=self.app_version,
            bucket_name=self.bucket_name,
            replicas=self.app_replicas,
            debug=self.app_debug,
            n_workers=self.app_workers,
            workers_timeout=self.app_timeout,
            csrf_trusted_origins=self.app_csrf_trusted_origins,

            # DB Config
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,

            # Resources
            requests_memory=self.app_requests_memory,
            requests_cpu=self.app_requests_cpu,
            limits_memory=self.app_limits_memory,
            limits_cpu=self.app_limits_cpu,

            # Logger
            rabbitmq_log=rabbitmq_log,

            # MFA
            mfa_application_name=self.mfa_application_name,
            mfa_token_expiration_interval=(
                self.mfa_token_expiration_interval),
            mfa_twilio_sender_phone_number=(
                self.mfa_twilio_sender_phone_number),

            # SSO
            sso__redirect_url=self.sso__redirect_url,
            sso__provider=self.sso__provider,
            sso__authorization_url=self.sso__authorization_url,
            sso__token_url=self.sso__token_url)

        deployment_auth_admin_static_f = \
            auth_admin_static.format(
                repository=self.static_repository,
                version=self.static_version)

        # If rabbitmq_log is set TRUE (deploying worker log pod), a disk
        # claim will be created to attach the disk to the pod.
        deployment_auth_admin_log_worker = None
        deployment_auth_admin_log_volume = None
        if rabbitmq_log == "TRUE":
            volume_claim_name = "pumpwood-auth-log-data"
            deployment_auth_admin_log_volume = kube_client.create_volume_yml(
                disk_name=self.worker_log_disk_name,
                disk_size=self.worker_log_disk_size,
                volume_claim_name=volume_claim_name)
            deployment_auth_admin_log_worker = auth_log_worker.format(
                repository=self.repository,
                version=self.worker_log_version,
                bucket_name=self.bucket_name,
                volume_claim_name=volume_claim_name,
                trino_catalog=self.worker_trino_catalog,
                debug=self.worker_debug)

        deployment_postgres_text_f = None
        if self.test_db_version is not None:
            self.test_db_limits_memory
            self.test_db_limits_cpu
            deployment_postgres_text_f = test_postgres.format(
                repository=self.test_db_repository,
                version=self.test_db_version,
                limits_memory=self.test_db_limits_memory,
                limits_cpu=self.test_db_limits_cpu)

        list_return = [{
            'type': 'secrets', 'name': 'pumpwood_auth__secrets',
            'content': secrets_text_f, 'sleep': 5}]
        if deployment_postgres_text_f is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_auth__postgres',
                'content': deployment_postgres_text_f, 'sleep': 20})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_auth_app__deploy',
            'content': deployment_auth_app_text_f, 'sleep': 10})
        list_return.append({
            'type': 'deploy', 'name': 'pumpwood_auth_admin_static__deploy',
            'content': deployment_auth_admin_static_f, 'sleep': 0})

        if deployment_auth_admin_log_volume is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_auth__volume_logs',
                'content': deployment_auth_admin_log_volume, 'sleep': 0})
        if deployment_auth_admin_log_worker is not None:
            list_return.append({
                'type': 'deploy', 'name': 'pumpwood_auth__worker_logs',
                'content': deployment_auth_admin_log_worker, 'sleep': 0})
        return list_return
