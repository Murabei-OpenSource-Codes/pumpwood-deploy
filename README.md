# PumpWood Deploy
This package helps deploy of Pumpwood like components in Kubernets clusters.
It uses jinja templates to generate yml files to be apply using kubectrl.
This package was developed by Murabei Data Science and is under BSD-3-Clause
license.

Deployment is structured as objects that are added to deploy using
`add_microservice` function of DeployPumpWood object.

<p align="center" width="60%">
  <img src="static_doc/sitelogo-horizontal.png" /> <br>

  <a href="https://en.wikipedia.org/wiki/Cecropia">
    Pumpwood is a native brasilian tree
  </a> which has a symbiotic relation with ants (Murabei)
</p>

# Documentation page
Documentation page is [here](https://murabei-opensource-codes.github.io/pumpwood-deploy/).

## Usage
It is usually a good patter to put versions of the containers as enviroment
variables set at `.env` file. Secrets could be stored on a json file, with a
.gitignore entry to avoid uploading them to repository.

It is not necessary to comment deployments when updating containers, if
not change if found between the yml file and configuration present at cluster
apply will results on no changes at the cluster.

## Example
```python
import os
import simplejson as json
from dotenv import load_dotenv
from pumpwood_deploy.deploy import DeployPumpWood
from pumpwood_deploy.microservices.api_gateway.deploy import CORSTerminaton
from pumpwood_deploy.ingress.aws.deploy import IngressALB

# Postgres
from pumpwood_deploy.microservices.postgres.deploy import (
    PostgresDatabase, PGBouncerDatabase)

# Base
from pumpwood_deploy.microservices.pumpwood_auth.deploy import (
    PumpWoodAuthMicroservice)
from pumpwood_deploy.microservices.pumpwood_datalake.deploy import (
    PumpWoodDatalakeMicroservice)


################
# Read secrets #
with open("secret-place-for-a-secret/secret-file.unreachable", "r") as file:
    secrets = json.loads(file.read())
load_dotenv()


#########################
# Create deploy objects #
# Create a base
deploy = DeployPumpWood(
    model_user_password=secrets["microservices--model"],
    rabbitmq_secret=secrets["rabbitmq_secret"],
    hash_salt=secrets["hash_salt"],

    kong_db_disk_name="nice-disk-for-kong",
    # Size of the disk that will be used to deploy postgres por
    # Postgres associated with Kong Service Mesh
    kong_db_disk_size="10Gi",

    # Provider for flat file storage
    k8_provider="aws",
    k8_deploy_args={
        "region": "nice-zone",
        "cluster_name": "nice-cluster",
    },
    k8_namespace="nice-namespace",

    storage_type="aws_s3",
    storage_deploy_args={
        "storage_bucket_name": "nice-bucket",
        "access_key_id": "very-secret-id-access-bucket-aws",
        "secret_access_key": "very-secret-key-access-bucket-aws"
    })

# It os possible to add the services that will be
# deployed, here a Postgres DaataBase will be deployed
# using a pre-created disk at AWS
deploy.add_microservice(
    PostgresDatabase(
        # Database credentials
        db_username="pumpwood",
        db_password="nice-password-for-postgres",
        name="nice-name-for-postgres",
        disk_size="150Gi",
        disk_name="name-of-the-nice-disk",

        # Limits the memory consumption, this is particulary important
        # for database that will consume most of the memory if pemited to
        # do so.
        postgres_limits_memory="4Gi",
        postgres_limits_cpu="4000m"))

# Add a CORS NGINX termination to Pumpwood at an API Gateway
deploy.add_microservice(
    CORSTerminaton(
        repository="nice-aws-project.dkr.ecr.nice-zone.amazonaws.com",
        version=os.getenv('API_GATEWAY'),
        health_check_url="health-check/pumpwood-auth-app/"))

# Using deploy on AWS it is possible to use Aplication Load Balancer to
# redirect requests using sub-domains.
deploy.add_microservice(
    IngressALB(
        alb_name="name-of-the-nice-alb",
        group_name="nice-alb-group",

        # Set an URL to be used as health check for the application
        # it is a good choice to use auth health check end-point
        health_check_url="/health-check/pumpwood-auth-app/",

        # Certificate to add HTTPs at ALB requests
        certificate_arn="arn:aws:acm:nice-zone:nice-aws-project:certificate/nice-certificate-arn",
        host="nice.hostname.cool",

        # Set service name that will redirect calls to containers
        service_name="apigateway-nginx",
        service_port=80
    ))

# Adding a PgBouncer to reduce connections with database
# Image associated with pgbouncer will automatically create
# database if necessary.
deploy.add_microservice(
    PGBouncerDatabase(
        name="pgbouncer-hive-metastore",
        postgres_database="hive_metastore",

        # Use Postgres deployed as unique database to reduce memory and
        # CPU consumption at cluster, it is possible to split each
        # Microserice on a different database if necessary
        postgres_secret="nice-name-for-postgres",
        postgres_host="nice-name-for-postgres"))

########
# Auth #
deploy.add_microservice(
    PGBouncerDatabase(
        name="pgbouncer-pumpwood-auth",
        postgres_database="pumpwood_auth",

        # Use Postgres deployed as unique database to reduce memory and
        # CPU consumption at cluster, it is possible to split each
        # Microserice on a different database if necessary
        postgres_secret="nice-name-for-postgres",
        postgres_host="nice-name-for-postgres"))

deploy.add_microservice(
    PumpWoodAuthMicroservice(
        repository="nice-aws-project.dkr.ecr.nice-zone.amazonaws.com",
        static_repository="nice-aws-project.dkr.ecr.nice-zone.amazonaws.com",
        db_username="nice-username-for-postgres",,
        db_password="nice-password-for-postgres",
        db_host="pgbouncer-pumpwood-auth",
        db_port="5432",
        db_database="pumpwood_auth",
        microservice_password="nice-password-for-microservice",
        secret_key="nice-secret-key-for-django",
        email_host_user="nice-email-user",
        email_host_password="nice-email-password",
        bucket_name="nice-bucket-name",
        app_version="1.0",
        static_version="1.0",
        worker_log_version="3.0",

        # Regulate the number of replicas that will be applied at
        # deploment
        app_replicas=1,
        app_debug="FALSE",
        worker_log_disk_name="nice-volume-to-store-staged-logs",
        worker_log_disk_size="20Gi",
        worker_trino_catalog="aws",

        mfa_application_name="This is a nice App",
        mfa_twilio_sender_phone_number='9999999',
        mfa_twilio_account_sid="nice-twilo-account",
        mfa_twilio_auth_token='nice-twilo-token'))


############
# Datalake #
deploy.add_microservice(
    PGBouncerDatabase(
        name="pgbouncer-pumpwood-datalake",
        postgres_database="pumpwood_datalake",

        # Use Postgres deployed as unique database to reduce memory and
        # CPU consumption at cluster, it is possible to split each
        # Microserice on a different database if necessary
        postgres_secret="nice-name-for-postgres",
        postgres_host="nice-name-for-postgres"))

deploy.add_microservice(
    PumpWoodDatalakeMicroservice(
        repository="nice-aws-project.dkr.ecr.nice-zone.amazonaws.com",
        db_username="nice-username-for-postgres",,
        db_password="nice-password-for-postgres",
        db_host="pgbouncer-pumpwood-datalake",
        db_port="5432",
        db_database="pumpwood_datalake",
        microservice_password='nice-password-for-datalake-microservice-user',
        bucket_name="nice-bucket-name",
        app_version='1,0',
        worker_version='2.0',

        # App
        app_debug='FALSE',
        app_replicas=1,

        # Limits APP memory and CPU consumption
        app_limits_memory="6Gi",
        app_limits_cpu="4000m",
        app_requests_memory="10Mi",
        app_requests_cpu="1m",

        # Limits Worker memory and CPU consumption
        worker_replicas=1,
        worker_limits_memory="6Gi",
        worker_limits_cpu="2000m",
        worker_requests_memory="10Mi",
        worker_requests_cpu="1m"))


###############################################
# Create deployment yml and  apply to cluster #
# This function will generate all yml and sh scripts to deploy
# the services, deployments and other K8s components, but will not
# apply them.
results = deploy.create_deploy_files()

# This will create all file, and apply them in the sequence that were added to
# deploy object, some apply of yml have a delay to let components be corretly
# created before move on with the deploy
deploy.deploy_microservices()
