"""Orchestrate Pumpwood microservice deployment on Kubernetes."""
from typing import Literal
import os
import stat
import shutil
from loguru import logger
from typing import List
from importlib import resources
from jinja2 import Template
from pumpwood_deploy.kubernets.kubernets import Kubernets
from pumpwood_deploy.type import (
    PumpwoodDeployK8sParameter,
    PumpwoodDeploySecret, PumpwoodDeployDeployment,
    PumpwoodDeployConfigMap, PumpwoodDeployVolume, PumpwoodDeployCMDRun,
    PumpwoodDeploy, PumpwoodDeploySecretFile, PumpwoodDeployConfigMapFile,
    PumpwoodDeployService)


create_kube_cmd = resources.files('pumpwood_deploy')\
    .joinpath('kubernets/bash_templates/kubectl_apply.sh')\
    .read_text(encoding='utf-8')
"""@private"""
secret_file_template = Template(
    resources.files('pumpwood_deploy')
    .joinpath('kubernets/bash_templates/secret_file.sh')
    .read_text(encoding='utf-8'))
"""@private"""
configmap_template = Template(
    resources.files('pumpwood_deploy')
    .joinpath('kubernets/bash_templates/configmap.sh')
    .read_text(encoding='utf-8'))
"""@private"""
configmap_keyname_template = Template(
    resources.files('pumpwood_deploy')
    .joinpath('kubernets/bash_templates/configmap_keyname.sh')
    .read_text(encoding='utf-8'))
"""@private"""


class DeployPumpWood():
    """Orchestrate Pumpwood microservice deployment on Kubernetes."""

    kube_client: Kubernets
    """Kubernetes client for disk creation and provider operations."""
    namespace: str
    """Namespace used to deploy Pumpwood resources."""
    microsservices_to_deploy: List
    """Microservice objects registered for deployment."""
    base_path: str
    """Base path for generated manifest files and bash scripts."""

    def __init__(self, k8_provider: Literal['gcp', 'azure', 'aws'],
                 k8_namespace: str, k8_deploy_args: PumpwoodDeployK8sParameter
                 ):
        """Initialize the Pumpwood deployment manager.

        Args:
            k8_provider (Literal['gcp', 'azure', 'aws']):
                Kubernetes cluster cloud provider.
            k8_namespace (str):
                Target namespace for deployment resources.
            k8_deploy_args (PumpwoodDeployK8sParameter):
                Provider-specific cluster connection parameters.
                Use ``PumpwoodDeployK8sParameterAWS`` for AWS,
                ``PumpwoodDeployK8sParameterGCP`` for GCP, or
                ``PumpwoodDeployK8sParameterAzure`` for Azure.
        """
        self.deploy = []

        # Create an instance of the K8s object that will make the
        # communication with provider
        self.kube_client = Kubernets(
            k8_namespace=k8_namespace, k8_provider=k8_provider,
            k8_deploy_args=k8_deploy_args)
        self.namespace = k8_namespace
        self.microsservices_to_deploy = []
        self.base_path = os.getcwd()

    def add_microservice(self, microservice):
        """Add a microservice to the deployment stack.

        Args:
            microservice (BasePumpwoodDeployMicroservice):
                Microservice object whose manifests will be generated.
        """
        self.microsservices_to_deploy.append(microservice)

    def create_deploy_files(self):
        """Create all deployment manifests and scripts.

        Iterate over `microsservices_to_deploy` creating deploy files at
        `./outputs/` folder.

        Returns:
            dict:
                A dictionary containing two lists of PumpwoodDeployCMDRun
                objects: 'service_cmds' and 'microservice_cmds'.
        """
        sevice_cmds = []
        deploy_cmds = []

        counter = 0
        service_counter = 0

        # Clear directory before creating deploy files
        if os.path.exists('outputs/deploy_output'):
            shutil.rmtree('outputs/deploy_output')
        os.makedirs('outputs/deploy_output')
        os.makedirs('outputs/deploy_output/resources/')

        if os.path.exists('outputs/services_output'):
            shutil.rmtree('outputs/services_output')
        os.makedirs('outputs/services_output')
        os.makedirs('outputs/services_output/resources/')

        # Use the template files to create bash scripts to deploy the
        # resources at k8s cluster
        logger.info('Creating microservices files:')
        m = self.microsservices_to_deploy[0]
        for m in self.microsservices_to_deploy:
            class_name = type(m).__name__
            logger.info('# Processing: {class_name}', class_name=class_name)
            temp_deployments = m.create_deployment_file()
            for d in temp_deployments:
                logger.info('### Creating deploy file: {d}', d=str(d.name))
                # Create a counter to order the files in the deploy
                str_counter = "%03d" % (counter, )
                str_service_counter = "%03d" % (service_counter, )

                # Process de deployment according to the deployment
                # class
                simple_types = (
                    PumpwoodDeploySecret, PumpwoodDeployDeployment,
                    PumpwoodDeployConfigMap)
                if isinstance(d, simple_types):
                    simple_deploy = self.process_simple_deploy(
                        d=d, str_counter=str_counter)
                    deploy_cmds.append(simple_deploy)
                    counter = counter + 1
                    continue

                # Process secret files
                if isinstance(d, PumpwoodDeploySecretFile):
                    deploy_cmd = self.process_secrets_file(
                        d=d, str_counter=str_counter)
                    deploy_cmds.append(deploy_cmd)
                    counter = counter + 1
                    continue

                # Process config maps files
                if isinstance(d, PumpwoodDeployConfigMapFile):
                    deploy_cmd = self.process_configmap_file(
                        d=d, str_counter=str_counter)
                    deploy_cmds.append(deploy_cmd)
                    counter = counter + 1
                    continue

                # Process volume
                if isinstance(d, PumpwoodDeployVolume):
                    deploy_cmd = self.process_volume(
                        d=d, str_counter=str_counter)
                    deploy_cmds.append(deploy_cmd)
                    counter = counter + 1
                    continue

                # Process services
                if isinstance(d, PumpwoodDeployService):
                    deploy_cmd = self.process_service(
                        d=d, str_service_counter=str_service_counter)
                    sevice_cmds.append(deploy_cmd)
                    service_counter = service_counter + 1
                    continue

                msg = (
                    "Deployment type not implemented, check the Pumpwood "
                    "deploy class {}").format(str(m))
                raise NotImplementedError(msg)

        return {
            'service_cmds': sevice_cmds,
            'microservice_cmds': deploy_cmds}

    def process_simple_deploy(self, d: PumpwoodDeploy,
                              str_counter: str) -> PumpwoodDeployCMDRun:
        """Process simple deployments.

        Handles secrets, deployments, and config maps written as YAML
        files plus matching ``kubectl apply`` shell scripts.

        Args:
            d (PumpwoodDeploy):
                Deployment object to process.
            str_counter (str):
                Formatted counter string for ordering files.

        Returns:
            PumpwoodDeployCMDRun:
                Command runner for the generated deploy script.
        """
        file_name_temp = 'resources/{counter}__{name}.yml'
        file_name = file_name_temp.format(
            counter=str_counter, name=d.name)

        with open('outputs/deploy_output/' +
                    file_name, 'w') as file:
            file.write(d.content)
        file_name_sh_temp = (
            'outputs/deploy_output/{counter}__{name}.sh')
        file_name_sh = file_name_sh_temp.format(
            counter=str_counter, name=d.name)

        # Create the bash file for the deployment
        deploy_namespace = d.namespace or self.namespace
        with open(file_name_sh, 'w') as file:
            content = create_kube_cmd.format(
                file=file_name, namespace=deploy_namespace)
            file.write(content)
        os.chmod(file_name_sh, stat.S_IRWXU)

        # Return an instance of the CMD run
        return PumpwoodDeployCMDRun(
            file=file_name_sh, sleep=d.sleep)

    def process_secrets_file(self, d: PumpwoodDeploySecretFile,
                             str_counter: str) -> PumpwoodDeployCMDRun:
        """Process secret files deployment.

        Args:
            d (PumpwoodDeploySecretFile):
                The secret file deployment object to process.
            str_counter (str):
                Formatted counter string for ordering files.

        Returns:
            PumpwoodDeployCMDRun:
                Command runner for the generated secret script.
        """
        # Legacy path set as string
        if isinstance(d.path, str):
            d.path = [d.path]

        deploy_namespace = d.namespace or self.namespace
        command_formated = secret_file_template.render(
            name=d.name, paths=d.path,
            namespace=deploy_namespace)
        file_name_temp = (
            'outputs/deploy_output/{counter}__{name}.sh')
        file_name = file_name_temp.format(
            counter=str_counter, name=d.name)

        with open(file_name, 'w') as file:
            file.write(command_formated)
        os.chmod(file_name, stat.S_IRWXU)
        return PumpwoodDeployCMDRun(
            file=file_name, sleep=d.sleep)

    def process_configmap_file(self, d: PumpwoodDeployConfigMapFile,
                               str_counter: str) -> PumpwoodDeployCMDRun:
        """Process configmap file deployment.

        Args:
            d (PumpwoodDeployConfigMapFile):
                The config map file object.
            str_counter (str):
                Formatted counter string for ordering files.

        Returns:
            PumpwoodDeployCMDRun:
                Command runner for the generated config map script.
        """
        file_name_resource_temp = 'resources/{name}'
        file_name_resource = file_name_resource_temp.format(
            name=d.file_name)

        if d.content is not None:
            with open('outputs/deploy_output/' +
                        file_name_resource, 'w') as file:
                file.write(d.content)
        else:
            with open(d.file_path, 'rb') as file:
                file_data = file.read()
            with open('outputs/deploy_output/' +
                        file_name_resource, 'wb') as file:
                file.write(file_data)

        command_formated = None
        deploy_namespace = d.namespace or self.namespace
        if d.keyname is None:
            command_formated = configmap_template.format(
                name=d.name, file_name=file_name_resource,
                namespace=deploy_namespace)
        else:
            command_formated = configmap_keyname_template.format(
                name=d.name, file_name=file_name_resource,
                keyname=d.keyname, namespace=deploy_namespace)

        file_name_temp = (
            'outputs/deploy_output/{counter}__{name}.sh')
        file_name = file_name_temp.format(
            counter=str_counter, name=d.name)

        with open(file_name, 'w') as file:
            file.write(command_formated)
        os.chmod(file_name, stat.S_IRWXU)
        return PumpwoodDeployCMDRun(
            file=file_name, sleep=d.sleep)

    def process_volume(self, d: PumpwoodDeployService,
                       str_counter: str) -> PumpwoodDeployCMDRun:
        """Process volume deployment.

        Args:
            d (PumpwoodDeployVolume):
                Volume deployment object.
            str_counter (str):
                Formatted counter string for ordering deploy files.

        Returns:
            PumpwoodDeployCMDRun:
                Command runner for the generated volume script.
        """
        volume_postgres_text_f = self.kube_client.create_volume_yml(
            disk_name=d.disk_name, disk_size=d.disk_size,
            volume_claim_name=d.volume_claim_name)

        file_name_temp = 'resources/{counter}__{name}.yml'
        file_name = file_name_temp.format(
            counter=str_counter, name=d.name)

        with open('outputs/deploy_output/' +
                    file_name, 'w') as file:
            file.write(volume_postgres_text_f)
        file_name_sh_temp = (
            'outputs/deploy_output/{counter}__{name}.sh')
        file_name_sh = file_name_sh_temp.format(
            counter=str_counter, name=d.name)

        # Create the bash file for the deployment
        deploy_namespace = d.namespace or self.namespace
        with open(file_name_sh, 'w') as file:
            content = create_kube_cmd.format(
                file=file_name, namespace=deploy_namespace)
            file.write(content)
        os.chmod(file_name_sh, stat.S_IRWXU)

        # Return an instance of the CMD run
        return PumpwoodDeployCMDRun(
            file=file_name_sh, sleep=d.sleep)

    def process_service(self, d: PumpwoodDeployService,
                        str_service_counter: str) -> PumpwoodDeployCMDRun:
        """Process service deployment.

        Args:
            d (PumpwoodDeployService):
                The service deployment object.
            str_service_counter (str):
                Formatted counter string for ordering service files.

        Returns:
            PumpwoodDeployCMDRun:
                Command runner for the generated service script.
        """
        file_name_temp = 'resources/{service_counter}__{name}.yml'
        file_name = file_name_temp.format(
            service_counter=str_service_counter,
            name=d.name)

        with open('outputs/services_output/' +
                    file_name, 'w') as file:
            file.write(d.content)
        file_name_sh_temp = \
            'outputs/services_output/' +\
            '{service_counter}__{name}.sh'
        file_name_sh = file_name_sh_temp .format(
            service_counter=str_service_counter,
            name=d.name)

        deploy_namespace = d.namespace or self.namespace
        with open(file_name_sh, 'w') as file:
            content = create_kube_cmd.format(
                file=file_name, namespace=deploy_namespace)
            file.write(content)

        os.chmod(file_name_sh, stat.S_IRWXU)
        return PumpwoodDeployCMDRun(
            file=file_name_sh, sleep=d.sleep)

    def deploy_microservices(self):
        """Generate deployment files and apply them to the cluster.

        Creates manifests under ``outputs/``, applies service manifests
        first, then microservice manifests in registration order.
        """
        deploy_cmds = self.create_deploy_files()
        logger.info('Deploying Services:')
        self.kube_client.run_deploy_commmands(
            deploy_cmds['service_cmds'])

        logger.info('Deploying Microservices:')
        self.kube_client.run_deploy_commmands(
            deploy_cmds['microservice_cmds'])
