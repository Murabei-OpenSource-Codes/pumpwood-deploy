"""Interface with kubernets."""

import subprocess


class Kubernets:
    """Class to auxiliate kubernets interface."""

    def __init__(self, cluster_name: str, zone: str, project: str,
                 namespace: str = "default"):
        """
        __init__.

        Args:
            cluster_name (str): Kubernets cluster name.
            zone (str): Zone location of the cluster.
            project (str): Google project name:
            temp_deploy_path (str): Path to keep temp deploy files.
        """
        cmd = "gcloud container clusters get-credentials {cluster_name} " + \
            " --zone {zone} --project {project}"
        cmd_formated = cmd.format(
            cluster_name=cluster_name, zone=zone, project=project)

        print('## Loging to kubernets cluster')
        process = subprocess.Popen(
            cmd_formated.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        print('## Creating namespace')
        cmd = "kubectl create namespace {namespace}"
        cmd_formated = cmd.format(namespace=namespace)
        process = subprocess.Popen(
            cmd_formated.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        print('## Setting new namespace [{namespace}] as default'.format(
            namespace=namespace))
        cmd = "kubectl config set-context --current --namespace={namespace}"
        cmd_formated = cmd.format(namespace=namespace)
        process = subprocess.Popen(
            cmd_formated.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

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
