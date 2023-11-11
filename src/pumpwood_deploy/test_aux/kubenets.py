"""Functions to help testing for Kubernets."""
import os


def validate_k8s_yml(file_content: str, microservice_name: str = None):
    """
    Validate K8s yml file with a dry run.

    Args:
        file_content (str): Content of the yml file.
    """
    if microservice_name is not None:
        if microservice_name not in file_content:
            msg = "{} not found on yml, many be definition is wrong".format(
                microservice_name)
            raise Exception(msg)

    with open("temp_val/temp.yml", "w") as file:
        file.write(file_content)

    cmd = (
        "kubectl apply --validate --dry-run=client "
        "--filename=temp_val/temp.yml")
    finish_signal = os.system(cmd)
    if finish_signal != 0:
        raise Exception("File is not a valid YML K8s")
