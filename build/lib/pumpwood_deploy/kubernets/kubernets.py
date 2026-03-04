"""Interface with kubernets."""
import os
import subprocess  # NOQA
import pkg_resources
from typing import List


volume_gcp = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'kubernets/resources/volume__gcp.yml').read().decode()
"""@private"""
volume_azure = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'kubernets/resources/volume__azure.yml').read().decode()
"""@private"""
volume_aws = pkg_resources.resource_stream(
    'pumpwood_deploy',
    'kubernets/resources/volume__aws.yml').read().decode()
"""@private"""


class Kubernets:
    """Class to auxiliate kubernets interface."""

    k8_namespace: str
    """Namespace that will be used to deploy Pumpwood."""
    k8_deploy_args: dict
    """Arguments that will be used on deploy of the pods, it will be passed as
       `**k8_deploy_args` to `KubernetsGCP`, `KubernetsAzure` or
       `KubernetsAWS`."""
    k8_provider: str
    """K8s provider, possible values ['gcp', 'azure', 'aws']."""
    kube_client: object
    """Object of the corresponding K8s class associated with `k8_provider`."""

    def __init__(self, k8_provider: str, k8_deploy_args: dict,
                 k8_namespace: str = "default"):
        """__init__.

        Args:
            k8_provider (str):
                Provider name.
            k8_deploy_args (dict):
                Arguments to deploy k8s cluster.
            k8_namespace (str):
                Name of the namespaces that will be used at deploy.

        Raises:
            NotImplementedError:
                Error for not implemented deploy options.
        """
        self.k8_namespace = k8_namespace
        self.k8_deploy_args = k8_deploy_args
        self.k8_provider = k8_provider

        self.kube_client = None
        if k8_provider == "gcp":
            self.kube_client = KubernetsGCP(**k8_deploy_args)
        elif k8_provider == "azure":
            self.kube_client = KubernetsAzure(**k8_deploy_args)
        elif k8_provider == "aws":
            self.kube_client = KubernetsAWS(**k8_deploy_args)
        else:
            msg = "Kubernets Provider [{}] not implemented".format(
                k8_provider)
            raise NotImplementedError(msg)

        print('## Creating k8_namespace')
        cmd = "kubectl create namespace {k8_namespace}"
        cmd_formated = cmd.format(k8_namespace=k8_namespace)
        # Commands associated with deploy are generated at the deploy package
        process = subprocess.Popen( # NOQA
            cmd_formated.split(), stdout=subprocess.PIPE)
        process.communicate()

        print('## Setting new k8_namespace [{k8_namespace}] as default'.format(
            k8_namespace=k8_namespace))
        cmd = (
            "kubectl config set-context --current "
            "--namespace={k8_namespace}")
        cmd_formated = cmd.format(k8_namespace=k8_namespace)
        # Commands associated with deploy are generated at the deploy package
        process = subprocess.Popen( # NOQA
            cmd_formated.split(), stdout=subprocess.PIPE)
        process.communicate()

    def create_volume_yml(self, disk_name: str, disk_size: str,
                          volume_claim_name: str) -> str:
        """Create volume yml using provider and k8_deploy_args.

        Args:
            disk_name (str):
                Disk name at the provider.
            disk_size (str):
                Size of the disk that will be mapped to K8s
                cluster.
            volume_claim_name (str):
                Name of the volume claim.

        Returns:
            Return the yml content of the deploy file.
        """
        return self.kube_client.create_volume_yml(
            disk_name=disk_name, disk_size=disk_size,
            volume_claim_name=volume_claim_name)

    def run_deploy_commmands(self, cmds: List[dict]):
        """Deploy commands.

        Create bash files to apply manifests to k8s cluster and run them. It is
        set a sleep time after each deployment, permiting finishing of cluster
        changes before move on.

        Args:
            cmds (List[dict]):
                List of commands to be applied at the k8s cluster.

        Raises:
            NotImplementedError:
                'Command not implemented: %s'. Indicates that command
                associated with deploy was not implemented yet. So far,
                only `run` was implemented.
        """
        for c in cmds:
            if c['command'] == 'run':
                sleep_time = c.get('sleep', 5)
                if sleep_time is None:
                    sleep_time = 5

                print('### Running file: ' + c['file'])
                print('##### Slepping for %s seconds after' % (sleep_time, ))
                with open(c['file'], 'r') as file:
                    file_cmd = file.read()

                # Colocando o shebangs no inicio do arquivo
                with open(c['file'], 'w') as file:
                    file.write(
                        "#!/bin/sh\n" + file_cmd + "\nsleep %s" % (
                            sleep_time, ))
                # Commands associated with deploy are generated at the deploy
                # package
                subprocess.call(c['file']) # NOQA
            else:
                raise NotImplementedError('Command not implemented: %s' % (
                    c['command'],))


class KubernetsGCP:
    """Class to auxiliate GCP Kubernets interface.

    This class will help creation of disks and cluster conenction, creating
    a default API for all providers.
    """

    def __init__(self, cluster_name: str, zone: str, project: str,
                 **kwargs):
        """Create a KubernetsGCP object.

        Constructor will create object and connect to k8s cluster using
        kubectl.

        Args:
            cluster_name (str):
                Kubernets cluster name that will be connected and will
                receive the K8s manifest application.
            zone (str):
                Zone location of the cluster.
            project (str):
                Google project name.
            **kwargs (dict):
                Other parameters for compatibility with other versions.

        Raises:
            Exception:
                '!! Error loging to k8s cluster, check logs !!'. Indicates
                that it was not possible to connect with k8s cluster using
                arguments passed.
        """
        self.cluster_name = cluster_name
        self.zone = zone
        self.project = project

        cmd = (
            "gcloud container clusters get-credentials {cluster_name} "
            " --zone {zone} --project {project}")
        cmd_formated = cmd.format(
            cluster_name=cluster_name, zone=zone, project=project)

        print('## Loging to kubernets cluster')
        status_code = os.system(cmd_formated) # NOQA
        if status_code != 0:
            raise Exception("!! Error loging to k8s cluster, check logs !!")

    def create_volume_yml(self, disk_name: str, disk_size: str,
                          volume_claim_name: str) -> str:
        """Create volume yml using provider and k8_deploy_args.

        Args:
            disk_name (str):
                Disk name at the provider.
            disk_size (str):
                Size of the disk that will be mapped to K8s
                cluster.
            volume_claim_name (str):
                Name of the volume claim.

        Returns:
            Return the yml manifest content of the deploy file to created
            perissistent volumes on GCP.
        """
        return volume_gcp.format(
            disk_name=disk_name, disk_size=disk_size,
            volume_claim_name=volume_claim_name)


class KubernetsAzure:
    """Class to auxiliate Azure AKS Kubernets interface.

    This class will help creation of disks and cluster conenction, creating
    a default API for all providers.
    """

    subscription: str
    """Azure subscription."""
    resource_group: str
    """Resorce group used in k8s cluster."""
    k8s_resource_group: str
    """Resorce group created by k8s cluster to deploy cluster components."""
    aks_resource: str
    """Name of the K8s resource."""

    def __init__(self, subscription: str, resource_group: str,
                 k8s_resource_group: str, aks_resource: str,
                 **kwargs):
        """Create a KubernetsAzure object.

        Constructor will create object and connect to k8s cluster using
        kubectl.

        Args:
            subscription (str):
                Azure subscription ID, something like
                XXXXXXXX-XXXX-XXXX-XXXX-53b44c8776b0.
            resource_group (str):
                Resorce group name used to deploy in k8s cluster. It is not
                the resource group created by k8s do deploy cluster
                components.
            k8s_resource_group (str):
                Resorce group created by k8s cluster to deploy cluster
                components.
            aks_resource (str):
                Name of the K8s resource.
            **kwargs (dict):
                Other parameters for compatibility with other versions.

        Raises:
            Exception:
                '!! Error loging to k8s cluster, check logs !!'. Indicates that
                it was not possible to connect with k8s cluster.
        """
        self.subscription = subscription
        self.resource_group = resource_group
        self.k8s_resource_group = k8s_resource_group
        self.aks_resource = aks_resource

        print('## Setting az client subscription')
        cmd = "az account set --subscription {subscription}"
        cmd_formated = cmd.format(subscription=subscription)
        status_code = os.system(cmd_formated) # NOQA
        if status_code != 0:
            raise Exception(
                "!! Error setting Azure subscription, check logs !!")

        process = subprocess.Popen(cmd_formated.split()) # NOQA
        process.communicate()

        print('## Loging to kubernets cluster')
        cmd = (
            "az aks get-credentials --overwrite-existing "
            "--resource-group {resource_group} "
            "--name {aks_resource} \n")
        cmd_formated = cmd.format(
            resource_group=resource_group,
            aks_resource=aks_resource)
        status_code = os.system(cmd_formated)  # NOQA
        if status_code != 0:
            raise Exception("!! Error loging to k8s cluster, check logs !!")

    def create_volume_yml(self, disk_name: str, disk_size: str,
                          volume_claim_name: str) -> str:
        """Create volume yml using provider and k8_deploy_args.

        Args:
            disk_name (str):
                Disk name at the provider.
            disk_size (str):
                Size of the disk that will be mapped to K8s
                cluster.
            volume_claim_name (str):
                Name of the volume claim.

        Returns:
            Return the yml content of the deploy file
        """
        return volume_azure.format(
            subscription_id=self.subscription,
            resource_group=self.k8s_resource_group,
            disk_name=disk_name, disk_size=disk_size,
            volume_claim_name=volume_claim_name)


class KubernetsAWS:
    """Class to auxiliate AWS EKS Kubernets interface.

    This class will help creation of disks and cluster conenction, creating
    a default API for all providers.
    """

    region: str
    """Region associated with K8s cluster."""
    cluster_name: str
    """K8s cluster name."""

    def __init__(self, region: str, cluster_name: str, **kwargs):
        """Create a KubernetsAWS object.

        Constructor will create object and connect to k8s cluster using
        kubectl.

        Args:
            region (str):
                EKS AWS Region.
            cluster_name (str):
                EKS cluster name.
            **kwargs (dict):
                Other parameters for compatibility with other versions.
        """
        self.region = region
        self.cluster_name = cluster_name

        print('## Loging to kubernets cluster')
        cmd = (
            "aws eks --region {region} "
            "update-kubeconfig --name {cluster_name}")
        cmd_formated = cmd.format(
            region=region, cluster_name=cluster_name)
        status_code = os.system(cmd_formated)  # NOQA
        if status_code != 0:
            raise Exception("!! Error loging to k8s cluster, check logs !!")

    def create_volume_yml(self, disk_name: str, disk_size: str,
                          volume_claim_name: str) -> str:
        """Create volume yml using provider and k8_deploy_args.

        Args:
            disk_name (str):
                Disk name at the provider.
            disk_size (str):
                Size of the disk that will be mapped to K8s
                cluster.
            volume_claim_name (str):
                Name of the volume claim.

        Returns:
            Return the yml content of the deploy file
        """
        return volume_aws.format(
            aws_volume_id=disk_name,
            volume_claim_name=volume_claim_name,
            disk_size=disk_size)
