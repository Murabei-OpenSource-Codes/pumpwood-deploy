"""Create AWS Aplication LoadBalancer Ingress."""
import os
from jinja2 import Template
from pumpwood_deploy.ingress.aws.resources.yml_resources import (
    aws_alb_ingress_host, aws_alb_ingress_path, aws_nlb_healthcheck,
    aws_nlb_healthcheck_ingress)


class IngressALB:
    """Create an AWS Aplication LoadBalancer Ingress."""

    def __init__(self, alb_name: str, group_name: str,
                 health_check_url: str, certificate_arn: str,
                 service_name: str = "apigateway-nginx",
                 service_port: int = 80,
                 host: str = None, path: str = "/"):
        """
        __init__.

        Constructor of IngressALB class.


        Args:
            alb_name [str]: Name of the Aplication LoadBalancer that will be
                created on AWS.
            group_name [str]: Name of the group used on AWS Aplication
                LoadBalancer.
            health_check_url [str]: Health check URL.
            certificate_arn [str]: Certificate ARN.
            service_name [str]: K8s service name.
            service_port [int] K8s service port.
        Kargs:
            host = None [str]: Host to redirect calls to service backend, this
                can be used to redirect sub-domains to especifct namespaces
                or services. Ex.: dev.mysite.com, client1.mysite.com.
            path = "/" [str]: Path to be used to redirect calls to service.
            service_name [str] = "apigateway-nginx": Service to redirect calls,
                apigateway-nginx is the default name of the CORSTerminaton
                service.
            service_port [int] = 80: Post used by {service_name}. 80 is the
                default port for CORSTerminaton.
        """
        self._alb_name = alb_name
        self._group_name = group_name
        self._health_check_url = health_check_url
        self._certificate_arn = certificate_arn
        self._service_name = service_name
        self._service_port = service_port
        self._host = host
        self._path = path
        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self, kube_client):
        """
        Create_deployment_file.

        Args:
          kube_client: Client to communicate with Kubernets cluster.
        """
        template = Template(aws_nlb_healthcheck_ingress)
        aws_nlb_healthcheck_ingress_frm = template.render(
            alb_name=self._alb_name,
            group_name=self._group_name,
            certificate_arn=self._certificate_arn)

        aws_alb_ingress_frm = None
        if self._host is None:
            template = Template(aws_alb_ingress_path)
            aws_alb_ingress_frm = template.render(
                alb_name=self._alb_name,
                group_name=self._group_name,
                health_check_url=self._health_check_url,
                certificate_arn=self._certificate_arn,
                path=self._path,
                service_name=self._service_name,
                service_port=self._service_port)

        else:
            template = Template(aws_alb_ingress_host)
            aws_alb_ingress_frm = template.render(
                alb_name=self._alb_name,
                group_name=self._group_name,
                health_check_url=self._health_check_url,
                certificate_arn=self._certificate_arn,
                host=self._host,
                path=self._path,
                service_name=self._service_name,
                service_port=self._service_port)

        return [
            {'type': 'deploy', 'name': 'aws_nlb_healthcheck__deploy',
             'content': aws_nlb_healthcheck, 'sleep': 0},
            {'type': 'deploy', 'name': 'aws_nlb_healthcheck_ingress__deploy',
             'content': aws_nlb_healthcheck_ingress_frm, 'sleep': 0},
            {'type': 'deploy', 'name': 'aws_alb_ingress_frm__deploy',
             'content': aws_alb_ingress_frm, 'sleep': 0},
        ]
