"""Kubernetes cluster interface for Pumpwood deploy."""
import os
import subprocess  # NOQA
from pathlib import Path
from loguru import logger
from importlib import resources
from pumpwood_deploy.type import (
    PumpwoodDeployCMD, PumpwoodDeployCMDRun, PumpwoodDeployK8sParameter,
    PumpwoodDeployK8sParameterGCP, PumpwoodDeployK8sParameterAzure,
    PumpwoodDeployK8sParameterAWS)


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
    k8_deploy_args: PumpwoodDeployK8sParameter
    """Arguments passed as to the provider class."""
    kube_client: object
    """Provider client instance selected from ``k8_provider``."""

    def __init__(self, k8_deploy_args: PumpwoodDeployK8sParameter,
                 k8_namespace: str = "default"):
        """Initialize the Kubernetes facade and cluster context.

        Args:
            k8_provider (str):
                Cloud provider identifier; one of ``gcp``, ``azure``,
                or ``aws``.
            k8_deploy_args (PumpwoodDeployK8sParameter):
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

        self.kube_client = None
        if isinstance(k8_deploy_args, PumpwoodDeployK8sParameterGCP):
            self.kube_client = KubernetsGCP(k8_deploy_args=k8_deploy_args)
        elif isinstance(k8_deploy_args, PumpwoodDeployK8sParameterAzure):
            self.kube_client = KubernetsAzure(k8_deploy_args=k8_deploy_args)
        elif isinstance(k8_deploy_args, PumpwoodDeployK8sParameterAWS):
            self.kube_client = KubernetsAWS(k8_deploy_args=k8_deploy_args)
        else:
            msg = "Kubernetes provider not implemented: {provider}".format(
                provider=type(k8_deploy_args).__name__)
            raise NotImplementedError(msg)

        logger.info('## Creating k8_namespace')
        cmd = "kubectl create namespace {k8_namespace}"
        cmd_formated = cmd.format(k8_namespace=k8_namespace)
        # Commands associated with deploy are generated at the deploy package
        process = subprocess.Popen( # NOQA
            cmd_formated.split(), stdout=subprocess.PIPE)
        process.communicate()

        logger.info(
            '## Setting new k8_namespace [{k8_namespace}] as default',
            k8_namespace=k8_namespace)
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

    def run_deploy_commmands(self, cmds: list[PumpwoodDeployCMD]):
        """Run generated audit shell scripts in sequence.

        Each script is written during file generation with a trailing
        ``sleep`` so manual replay matches automated execution.

        Args:
            cmds (list[PumpwoodDeployCMD]):
                Deploy command objects. Only ``PumpwoodDeployCMDRun`` is
                supported.

        Returns:
            None:
                Always returns None.

        Raises:
            NotImplementedError:
                If a command type other than ``PumpwoodDeployCMDRun`` is
                requested.
            ValueError:
                If an audit script path is outside ``outputs/``.
            subprocess.CalledProcessError:
                If a deploy script exits with a non-zero status.
        """
        outputs_root = Path('outputs').resolve()
        for c in cmds:
            if isinstance(c, PumpwoodDeployCMDRun):
                script_path = Path(c.file).resolve()
                if outputs_root not in script_path.parents:
                    msg = (
                        "Audit script outside outputs/: {path}").format(
                            path=script_path)
                    raise ValueError(msg)

                logger.info(
                    '### Running audit script: {file}',
                    file=str(script_path))
                subprocess.run(
                    ['/bin/sh', str(script_path)],
                    check=True)
            else:
                msg = 'Command not implemented: {cmd}'.format(
                    cmd=type(c).__name__)
                raise NotImplementedError(msg)


class KubernetsGCP:
    """Google Cloud Kubernetes helper for cluster access and volumes.

    Provides a shared API for disk creation and cluster connection across
    cloud providers.
    """

    def __init__(self, k8_deploy_args: PumpwoodDeployK8sParameterGCP):
        """Connect to a GKE cluster using gcloud credentials.

        Args:
            k8_deploy_args (PumpwoodDeployK8sParameterGCP):
                GCP cluster connection parameters.

        Raises:
            RuntimeError:
                If cluster credential retrieval fails.
        """
        self.cluster_name = k8_deploy_args.cluster_name
        self.zone = k8_deploy_args.zone
        self.project = k8_deploy_args.project

        cmd = (
            "gcloud container clusters get-credentials {cluster_name} "
            " --zone {zone} --project {project}")
        cmd_formated = cmd.format(
            cluster_name=self.cluster_name, zone=self.zone,
            project=self.project)

        logger.info('## Loging to kubernets cluster')
        status_code = os.system(cmd_formated)  # noqa: S605
        if status_code != 0:
            msg = "Error loging to k8s cluster, check logs"
            raise RuntimeError(msg)

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

    def __init__(self, k8_deploy_args: PumpwoodDeployK8sParameterAzure):
        """Connect to an Azure Kubernetes Service cluster.

        Args:
            k8_deploy_args (PumpwoodDeployK8sParameterAzure):
                Azure cluster connection parameters.

        Raises:
            RuntimeError:
                If subscription selection or credential retrieval fails.
        """
        self.subscription = k8_deploy_args.subscription
        self.resource_group = k8_deploy_args.resource_group
        self.k8s_resource_group = k8_deploy_args.k8s_resource_group
        self.aks_resource = k8_deploy_args.aks_resource

        logger.info('## Setting az client subscription')
        cmd = "az account set --subscription {subscription}"
        cmd_formated = cmd.format(subscription=self.subscription)
        status_code = os.system(cmd_formated)  # noqa: S605
        if status_code != 0:
            msg = "Error setting Azure subscription, check logs"
            raise RuntimeError(msg)

        logger.info('## Loging to kubernets cluster')
        cmd = (
            "az aks get-credentials --overwrite-existing "
            "--resource-group {resource_group} "
            "--name {aks_resource} \n")
        cmd_formated = cmd.format(
            resource_group=self.resource_group,
            aks_resource=self.aks_resource)
        status_code = os.system(cmd_formated)  # noqa: S605
        if status_code != 0:
            msg = "Error loging to k8s cluster, check logs"
            raise RuntimeError(msg)

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

    def __init__(self, k8_deploy_args: PumpwoodDeployK8sParameterAWS):
        """Connect to an AWS Elastic Kubernetes Service cluster.

        Args:
            k8_deploy_args (PumpwoodDeployK8sParameterAWS):
                AWS cluster connection parameters.

        Raises:
            RuntimeError:
                If kubeconfig update fails.
        """
        self.region = k8_deploy_args.region
        self.cluster_name = k8_deploy_args.cluster_name

        logger.info('## Loging to kubernets cluster')
        cmd = (
            "aws eks --region {region} "
            "update-kubeconfig --name {cluster_name}")
        cmd_formated = cmd.format(
            region=k8_deploy_args.region,
            cluster_name=k8_deploy_args.cluster_name)
        status_code = os.system(cmd_formated)  # noqa: S605
        if status_code != 0:
            msg = "Error loging to k8s cluster, check logs"
            raise RuntimeError(msg)

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
