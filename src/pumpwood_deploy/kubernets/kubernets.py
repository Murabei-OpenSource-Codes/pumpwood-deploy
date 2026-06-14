"""Kubernetes cluster interface for Pumpwood deploy."""
import os
import subprocess  # NOQA
from importlib import resources
from typing import List


volume_gcp = resources.files('pumpwood_deploy')\
    .joinpath('kubernets/resources/volume__gcp.yml')\
    .read_text(encoding='utf-8')
"""@private"""
volume_azure = resources.files('pumpwood_deploy')\
    .joinpath('kubernets/resources/volume__azure.yml')\
    .read_text(encoding='utf-8')
"""@private"""
volume_aws = resources.files('pumpwood_deploy')\
    .joinpath('kubernets/resources/volume__aws.yml')\
    .read_text(encoding='utf-8')
"""@private"""


class Kubernets:
    """Facade for provider-specific Kubernetes operations."""

    k8_namespace: str
    """Namespace used to deploy Pumpwood resources."""
    k8_deploy_args: dict
    """Arguments passed as ``**k8_deploy_args`` to the provider client."""
    k8_provider: str
    """Kubernetes provider; one of ``gcp``, ``azure``, or ``aws``."""
    kube_client: object
    """Provider client instance selected from ``k8_provider``."""

    def __init__(self, k8_provider: str, k8_deploy_args: dict,
                 k8_namespace: str = "default"):
        """Initialize the Kubernetes facade and cluster context.

        Args:
            k8_provider (str):
                Cloud provider identifier; one of ``gcp``, ``azure``,
                or ``aws``.
            k8_deploy_args (dict):
                Provider-specific cluster connection parameters passed
                to the selected provider client.
            k8_namespace (str):
                Namespace created and set as the active kubectl context.
                Defaults to ``default``.

        Raises:
            NotImplementedError:
                If ``k8_provider`` is not supported.
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
        """Build a persistent volume manifest for the active provider.

        Args:
            disk_name (str):
                Provider disk identifier.
            disk_size (str):
                Requested disk size mapped into the cluster.
            volume_claim_name (str):
                Kubernetes persistent volume claim name.

        Returns:
            str:
                Rendered persistent volume manifest for the provider.
        """
        return self.kube_client.create_volume_yml(
            disk_name=disk_name, disk_size=disk_size,
            volume_claim_name=volume_claim_name)

    def run_deploy_commmands(self, cmds: List[dict]):
        """Run generated deploy shell scripts in sequence.

        Each command may include a sleep interval so cluster resources
        can finish provisioning before the next apply.

        Args:
            cmds (List[dict]):
                Deploy command descriptors with ``command``, ``file``,
                and optional ``sleep`` keys.

        Raises:
            NotImplementedError:
                If a command type other than ``run`` is requested.
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
    """Google Cloud Kubernetes helper for cluster access and volumes.

    Provides a shared API for disk creation and cluster connection across
    cloud providers.
    """

    def __init__(self, cluster_name: str, zone: str, project: str,
                 **kwargs):
        """Connect to a GKE cluster using gcloud credentials.

        Args:
            cluster_name (str):
                GKE cluster name that receives manifest applications.
            zone (str):
                GCP zone where the cluster is deployed.
            project (str):
                Google Cloud project identifier.
            **kwargs (dict):
                Extra parameters kept for backward compatibility.

        Raises:
            Exception:
                If cluster credential retrieval fails.
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
        """Build a GCP persistent volume manifest.

        Args:
            disk_name (str):
                GCP disk identifier.
            disk_size (str):
                Requested disk size mapped into the cluster.
            volume_claim_name (str):
                Kubernetes persistent volume claim name.

        Returns:
            str:
                Rendered GCP persistent volume manifest content.
        """
        return volume_gcp.format(
            disk_name=disk_name, disk_size=disk_size,
            volume_claim_name=volume_claim_name)


class KubernetsAzure:
    """Azure AKS Kubernetes cluster helper.

    Creates persistent volume manifests and connects to AKS using
    ``az aks get-credentials``.
    """

    subscription: str
    """Azure subscription identifier."""
    resource_group: str
    """Resource group that owns the AKS deployment."""
    k8s_resource_group: str
    """Resource group created by AKS for cluster components."""
    aks_resource: str
    """AKS cluster resource name."""

    def __init__(self, subscription: str, resource_group: str,
                 k8s_resource_group: str, aks_resource: str,
                 **kwargs):
        """Connect to an Azure Kubernetes Service cluster.

        Args:
            subscription (str):
                Azure subscription ID.
            resource_group (str):
                Resource group used to deploy the AKS cluster.
            k8s_resource_group (str):
                Resource group created by AKS for cluster components.
            aks_resource (str):
                AKS cluster resource name.
            **kwargs (dict):
                Extra parameters kept for backward compatibility.

        Raises:
            Exception:
                If subscription selection or credential retrieval fails.
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
        """Build an Azure persistent volume manifest.

        Args:
            disk_name (str):
                Azure disk identifier.
            disk_size (str):
                Requested disk size mapped into the cluster.
            volume_claim_name (str):
                Kubernetes persistent volume claim name.

        Returns:
            str:
                Rendered Azure persistent volume manifest content.
        """
        return volume_azure.format(
            subscription_id=self.subscription,
            resource_group=self.k8s_resource_group,
            disk_name=disk_name, disk_size=disk_size,
            volume_claim_name=volume_claim_name)


class KubernetsAWS:
    """AWS EKS Kubernetes cluster helper.

    Creates persistent volume manifests and connects to EKS using
    ``aws eks update-kubeconfig``.
    """

    region: str
    """AWS region associated with the EKS cluster."""
    cluster_name: str
    """EKS cluster name."""

    def __init__(self, region: str, cluster_name: str, **kwargs):
        """Connect to an AWS Elastic Kubernetes Service cluster.

        Args:
            region (str):
                AWS region where the cluster is deployed.
            cluster_name (str):
                EKS cluster name.
            **kwargs (dict):
                Extra parameters kept for backward compatibility.

        Raises:
            Exception:
                If kubeconfig update fails.
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
        """Build an AWS persistent volume manifest.

        Args:
            disk_name (str):
                AWS volume identifier.
            disk_size (str):
                Requested disk size mapped into the cluster.
            volume_claim_name (str):
                Kubernetes persistent volume claim name.

        Returns:
            str:
                Rendered AWS persistent volume manifest content.
        """
        return volume_aws.format(
            aws_volume_id=disk_name,
            volume_claim_name=volume_claim_name,
            disk_size=disk_size)
