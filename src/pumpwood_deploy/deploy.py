"""Pumpwood Deploy."""
import os
import stat
import shutil
from pumpwood_deploy.microservices.standard.deploy import (
    StandardMicroservices)
from pumpwood_deploy.kubernets.kubernets import Kubernets
from jinja2 import Template


# Template to create secrets from files
secret_file_template = Template("""
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
kubectl delete secret --namespace={{namespace}} {{name}};
kubectl create secret generic {{name}} --namespace={{namespace}}{%- for path in paths %} --from-file='{{path}}'{%- endfor %}""")


class DeployPumpWood():
    """Class to perform PumpWood Deploy."""

    create_kube_cmd = (
        'SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"\n'
        'kubectl apply -f $SCRIPTPATH/{file} --namespace={namespace}')

    def __init__(self, model_user_password: str,
                 rabbitmq_secret: str, hash_salt: str, kong_db_disk_name: str,
                 kong_db_disk_size: str, k8_provider: str,
                 k8_deploy_args: dict, storage_type: str,
                 storage_deploy_args: str, k8_namespace="pumpwood",
                 gateway_health_url: str = "health-check/pumpwood-auth-app/",
                 kong_repository: str = "gcr.io/repositorio-geral-170012"):
        """
        __init__.

        Args:
          model_password (str): Password of models microservice.
          beatbox_conf_path (str): Path to beatbox configuration file.
          beatbox_version (str): Version of beatbox image.
          hash_salt (str): Salt for hashs in deployment.
          cluster_zone (str): Kubernets cluster zone.
          cluster_project (str): Kubernets project name.
          k8_provider (str): Kubernets provider, so far must be
            in ['gcp', 'azure'].
          k8_deploy_args (dict): Arguments to deploy k8s cluster it may
            vary depending on the provider. Check classes KubernetsGCP,
            KubernetsAzure.
          storage_type (str): Storage provider must be in [
            'azure', 'gcp', 'aws'], correpond to the provider os the flat
            file storage system.
          storage_deploy_args (str): Args used to access storage at the
            pods. Each provider must have diferent arguments:
                # Azure:
                - azure_storage_connection_string: Set conenction string to
                    a blob storage.
                # GCP:
                - credential_file: Set a path to a credetial file of a service
                    user with access to the bucket that will be used at the
                    deployment.
                # AWS:
                - aws_access_key_id: Access key of the service user with
                    access to the s3 used in deployment.
                - aws_secret_access_key: Access secret of the service user with
                    access to the s3 used in deployment.
        Kwargs:
            k8_namespace [str]: Which namespace to deploy the system.
        """
        self.deploy = []
        self.kube_client = Kubernets(
            k8_namespace=k8_namespace, k8_provider=k8_provider,
            k8_deploy_args=k8_deploy_args)
        self.namespace = k8_namespace

        standard_microservices = StandardMicroservices(
            hash_salt=hash_salt,
            rabbit_password=rabbitmq_secret,
            kong_db_disk_name=kong_db_disk_name,
            kong_db_disk_size=kong_db_disk_size,
            kong_repository=kong_repository,
            model_user_password=model_user_password,
            storage_type=storage_type,
            storage_deploy_args=storage_deploy_args)

        self.microsservices_to_deploy = [
            standard_microservices]
        self.base_path = os.getcwd()

    def add_microservice(self, microservice):
        """
        add_microservice.

        .
        """
        self.microsservices_to_deploy.append(microservice)

    def create_deploy_files(self):
        """create_deploy_files."""
        sevice_cmds = []
        deploy_cmds = []

        counter = 0
        service_counter = 0

        ###################################################################
        # Limpa o deploy anterior e cria as pastas para receber os arquivos
        # do novo deploy
        if os.path.exists('outputs/deploy_output'):
            shutil.rmtree('outputs/deploy_output')
        os.makedirs('outputs/deploy_output')
        os.makedirs('outputs/deploy_output/resources/')

        if os.path.exists('outputs/services_output'):
            shutil.rmtree('outputs/services_output')
        os.makedirs('outputs/services_output')
        os.makedirs('outputs/services_output/resources/')
        ###################################################################

        #####################################################################
        # Usa os arqivos de template e subistitui com as variáveis para criar
        # os templates de deploy
        print('### Creating microservices files:')
        # m = self.microsservices_to_deploy[-1]
        for m in self.microsservices_to_deploy:
            print('\nProcessing: ' + str(m))
            temp_deployments = m.create_deployment_file(
                kube_client=self.kube_client)
            for d in temp_deployments:
                # Create a counter to order the files in the deploy
                str_counter = "%03d" % (counter, )
                str_service_counter = "%03d" % (service_counter, )

                # Create Kubernets deploy files using yml string content
                if d['type'] in ['secrets', 'deploy', 'volume', 'configmap']:
                    file_name_temp = 'resources/{counter}__{name}.yml'
                    file_name = file_name_temp.format(
                        counter=str_counter, name=d['name'])

                    print('Creating deploy: ' + file_name)
                    with open('outputs/deploy_output/' +
                              file_name, 'w') as file:
                        file.write(d['content'])

                    file_name_sh_temp = (
                        'outputs/deploy_output/{counter}__{name}.sh')
                    file_name_sh = file_name_sh_temp.format(
                        counter=str_counter, name=d['name'])

                    with open(file_name_sh, 'w') as file:
                        content = self.create_kube_cmd.format(
                            file=file_name, namespace=self.namespace)
                        file.write(content)
                    os.chmod(file_name_sh, stat.S_IRWXU)

                    deploy_cmds.append({
                        'command': 'run', 'file': file_name_sh,
                        'sleep': d.get('sleep')})
                    counter = counter + 1

                # Create a secret from a file
                elif d['type'] == 'secrets_file':
                    # Legacy path set as string
                    if type(d["path"]) == str:
                        d["path"] = [str]
                    command_formated = secret_file_template.render(
                        name=d["name"], paths=d["path"],
                        namespace=self.namespace)
                    file_name_temp = (
                        'outputs/deploy_output/{counter}__{name}.sh')
                    file_name = file_name_temp.format(
                        counter=str_counter, name=d['name'])

                    print('Creating secrets_file: ' + file_name)
                    with open(file_name, 'w') as file:
                        file.write(command_formated)
                    os.chmod(file_name, stat.S_IRWXU)
                    deploy_cmds.append({
                        'command': 'run', 'file': file_name,
                        'sleep': d.get('sleep')})
                    counter = counter + 1

                # Create ConfigMap from a file
                elif d['type'] == 'configmap_file':
                    file_name_resource_temp = 'resources/{name}'
                    file_name_resource = file_name_resource_temp.format(
                        name=d['file_name'])

                    if 'content' in d.keys():
                        with open('outputs/deploy_output/' +
                                  file_name_resource, 'w') as file:
                            file.write(d['content'])
                    elif 'file_path' in d.keys():
                        with open(d['file_path'], 'rb') as file:
                            file_data = file.read()
                        with open('outputs/deploy_output/' +
                                  file_name_resource, 'wb') as file:
                            file.write(file_data)

                    command_formated = None
                    if d.get('keyname') is None:
                        command_text = (
                            'SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"\n'
                            "kubectl delete configmap {name};\n"
                            "kubectl create configmap {name} "
                            '--from-file="$SCRIPTPATH/{file_name}" '
                            '--namespace={namespace}')
                        command_formated = command_text.format(
                            name=d['name'], file_name=file_name_resource,
                            namespace=self.namespace)
                    else:
                        command_text = (
                            'SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"\n'
                            "kubectl delete configmap {name};\n"
                            "kubectl create configmap {name} "
                            '--from-file="{keyname}=$SCRIPTPATH/{file_name}" '
                            '--namespace={namespace}')
                        command_formated = command_text.format(
                            name=d['name'], file_name=file_name_resource,
                            keyname=d['keyname'], namespace=self.namespace)

                    file_name_temp = 'outputs/deploy_output/' + \
                                     '{counter}__{name}.sh'
                    file_name = file_name_temp.format(
                        counter=str_counter, name=d['name'])

                    print('Creating configmap: ' + file_name)
                    with open(file_name, 'w') as file:
                        file.write(command_formated)
                    deploy_cmds.append({'command': 'run', 'file': file_name,
                                        'sleep': d.get('sleep')})
                    os.chmod(file_name, stat.S_IRWXU)
                    counter = counter + 1

                # Create services and load-balacers
                elif d['type'] == 'services':
                    file_name_temp = 'resources/{service_counter}__{name}.yml'
                    file_name = file_name_temp.format(
                        service_counter=str_service_counter,
                        name=d['name'])

                    print('Creating services: ' + file_name)
                    with open('outputs/services_output/' +
                              file_name, 'w') as file:
                        file.write(d['content'])

                    file_name_sh_temp = \
                        'outputs/services_output/' +\
                        '{service_counter}__{name}.sh'
                    file_name_sh = file_name_sh_temp .format(
                        service_counter=str_service_counter,
                        name=d['name'])

                    with open(file_name_sh, 'w') as file:
                        content = self.create_kube_cmd.format(
                            file=file_name, namespace=self.namespace)
                        file.write(content)

                    os.chmod(file_name_sh, stat.S_IRWXU)
                    sevice_cmds.append({
                        'command': 'run', 'file': file_name_sh,
                        'sleep': d.get('sleep')})
                    service_counter = service_counter + 1

                elif d['type'] == 'endpoint_services':
                    raise Exception('Not used anymore')
                else:
                    raise Exception('Type not implemented: %s' % (d['type'], ))

        return {
            'service_cmds': sevice_cmds,
            'microservice_cmds': deploy_cmds}

    def deploy_cluster(self):
        """Deploy cluster."""
        deploy_cmds = self.create_deploy_files()
        print('\n\n###Deploying Services:')
        self.kube_client.run_deploy_commmands(
            deploy_cmds['service_cmds'])

        print('\n\n###Deploying Microservices:')
        self.kube_client.run_deploy_commmands(
            deploy_cmds['microservice_cmds'])
