"""Interface with kubernets."""
import subprocess
from .resources.yml__resources import volume_gcp, volume_azure


class Kubernets:
    """Class to auxiliate kubernets interface."""

    def __init__(self, k8_provider: str, k8_deploy_args: dict,
                 k8_namespace: str = "default"):
        """
        __init__.

        Args:
            cluster_name (str): Kubernets cluster name.
            k8_provider (str): Provider name.
            k8_deploy_args (dict): Arguments to deploy k8s cluster.
        """
        self.k8_namespace = k8_namespace
        self.k8_deploy_args = k8_deploy_args
        self.k8_provider = k8_provider

        self.kube_client = None
        if k8_provider == "gcp":
            self.kube_client = KubernetsGCP(**k8_deploy_args)
        elif k8_provider == "azure":
            self.kube_client = KubernetsAzure(**k8_deploy_args)
        else:
            raise Exception("Kubernets Provider not Found")

        print('## Creating k8_namespace')
        cmd = "kubectl create namespace {k8_namespace}"
        cmd_formated = cmd.format(k8_namespace=k8_namespace)
        process = subprocess.Popen(
            cmd_formated.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        print('## Setting new k8_namespace [{k8_namespace}] as default'.format(
            k8_namespace=k8_namespace))
        cmd = (
            "kubectl config set-context --current "
            "--namespace={k8_namespace}")
        cmd_formated = cmd.format(k8_namespace=k8_namespace)
        process = subprocess.Popen(
            cmd_formated.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

    def create_volume_yml(self, disk_name: str, disk_size: str,
                          volume_claim_name: str) -> str:
        """
        Create volume yml using provider and k8_deploy_args.

        Args:
            disk_name [str]: Disk name at the provider.
            disk_size [str]: Size of the disk that will be mapped to K8s
                cluster.
            volume_claim_name [str]: Name of the volume claim.
        Return [str]:
            Return the yml content of the deploy file
        """
        return self.kube_client.create_volume_yml(
            disk_name=disk_name, disk_size=disk_size,
            volume_claim_name=volume_claim_name)

    def run_deploy_commmands(self, cmds):
        """Deploy comands."""
        for c in cmds:
            if c['command'] == 'create':
                raise Exception('Not implemented')
            elif c['command'] == 'run':
                sleep_time = c.get('sleep', 10)
                if sleep_time is None:
                    sleep_time = 10
                print('###Running file: ' + c['file'])
                print('#####Slepping for %s seconds after' % (sleep_time, ))
                with open(c['file'], 'r') as file:
                    file_cmd = file.read()
                # Colocando o shebangs no inicio do arquivo
                with open(c['file'], 'w') as file:
                    file.write(
                        "#!/bin/sh\n" + file_cmd + "\nsleep %s" % (
                            sleep_time, ))
                subprocess.call(c['file'])
            else:
                raise Exception('Command not implemented: %s' % (
                    c['command'],))


class KubernetsGCP:
    """Class to auxiliate GCP Kubernets interface."""

    def __init__(self, cluster_name: str, zone: str, project: str):
        """
        __init__.

        Args:
            cluster_name (str): Kubernets cluster name.
            zone (str): Zone location of the cluster.
            project (str): Google project name:
            temp_deploy_path (str): Path to keep temp deploy files.
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
        process = subprocess.Popen(
            cmd_formated.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

    def create_volume_yml(self, disk_name: str, disk_size: str,
                          volume_claim_name: str) -> str:
        """
        Create volume yml using provider and k8_deploy_args.

        Args:
            disk_name [str]: Disk name at the provider.
            disk_size [str]: Size of the disk that will be mapped to K8s
                cluster.
            volume_claim_name [str]: Name of the volume claim.
        Return [str]:
            Return the yml content of the deploy file
        """
        return volume_gcp.format(
            disk_name=disk_name,
            disk_size=disk_size,
            volume_claim_name=volume_claim_name)


class KubernetsAzure:
    """Class to auxiliate Azure AKS Kubernets interface."""

    def __init__(self, subscription: str, resource_group: str,
                 k8s_resource_group: str, aks_resource: str):
        """
        __init__.

        Args:
            subscription (str): Azure subscription.
            resource_group (str): Resorce group used in k8s cluster.
            k8s_resource_group (str): Resorce group created by k8s cluster
                to deploy cluster components
            aks_resource (str): Name of the K8s resource.
        """
        self.subscription = subscription
        self.resource_group = resource_group
        self.k8s_resource_group = k8s_resource_group
        self.aks_resource = aks_resource

        print('## Setting az client subscription')
        cmd = "az account set --subscription {subscription}"
        cmd_formated = cmd.format(subscription=subscription)
        process = subprocess.Popen(cmd_formated.split())
        output, error = process.communicate()

        print('## Loging to kubernets cluster')
        cmd = (
            "az aks get-credentials --overwrite-existing "
            "--resource-group {resource_group} "
            "--name {aks_resource} \n")
        cmd_formated = cmd.format(
            resource_group=resource_group,
            aks_resource=aks_resource)
        process = subprocess.Popen(cmd_formated.split())
        output, error = process.communicate()

    def create_volume_yml(self, disk_name: str, disk_size: str,
                          volume_claim_name: str) -> str:
        """
        Create volume yml using provider and k8_deploy_args.

        Args:
            disk_name [str]: Disk name at the provider.
            disk_size [str]: Size of the disk that will be mapped to K8s
                cluster.
            volume_claim_name [str]: Name of the volume claim.
        Return [str]:
            Return the yml content of the deploy file
        """
        return volume_azure.format(
            subscription_id=self.subscription,
            resource_group=self.k8s_resource_group,
            disk_name=disk_name,
            disk_size=disk_size,
            volume_claim_name=volume_claim_name)
