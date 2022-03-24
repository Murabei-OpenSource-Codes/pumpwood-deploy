"""load_balancer.py."""

import os
import base64

from slugify import slugify
from jinja2 import Template


class LoadBalancerMicroservice:
    """
    LoadBalancerMicroservice.

    .
    """

    def __init__(self, haproxy_stats_user, haproxy_stats_password,
                 haproxy_acls, haproxy_services, kube_dns_ip,
                 gateway_public_ip, gateway_ssl_cert_path,
                 gateway_ssl_key_path, gateway_ssl_dhparam_path,
                 version_nginx_gateway, firewall_ips):
        """
        __init__.

        .
        """
        with open(gateway_ssl_cert_path, 'r') as file:
            ssl_cert = file.read()
            self._nginx_ssl_cert = base64.b64encode(
                    ssl_cert.encode()).decode()

        with open(gateway_ssl_key_path, 'r') as file:
            ssl_key = file.read()
            self._nginx_ssl_key = base64.b64encode(
                ssl_key.encode()).decode()

        with open(gateway_ssl_dhparam_path, 'r') as file:
            ssl_dhparam = file.read()
            self._nginx_ssl_dhparam = base64.b64encode(
                ssl_dhparam.encode()).decode()

        self.version_nginx_gateway = version_nginx_gateway
        self.haproxy_stats_user = haproxy_stats_user
        self.haproxy_stats_password = haproxy_stats_password
        self._haproxy_stats_user = base64.b64encode(
            haproxy_stats_user.encode()).decode()
        self._haproxy_stats_password = base64.b64encode(
            haproxy_stats_password.encode()).decode()
        self.haproxy_acls = haproxy_acls
        self.haproxy_services = haproxy_services
        self.kube_dns_ip = kube_dns_ip
        self.gateway_public_ip = gateway_public_ip
        self.firewall_ips = firewall_ips
        self.base_path = os.path.dirname(__file__)

    def create_deployment_file(self):
        """create_deployment_file."""
        #################
        # Haproxy Config#
        with open(os.path.join(self.base_path,
                  'resources_yml/haproxy.cfg.jinja2'), 'r') as file:
            haproxy_config_template = file.read()
        haproxy_config_template = Template(haproxy_config_template)

        with_health_check = []
        admin_acls = []
        admin_backends = []
        for x in self.haproxy_services:
            if x['health-check']:
                if x['model'] is None:
                    acl_name = slugify(x['service'], separator="_") + \
                        '_health_check'
                    with_health_check.append({
                            'acl_name': acl_name,
                            'service': '/health-check/' + x['service'] + '/',
                            'backend': x['backend']})
                else:
                    acl_name = slugify(x['service'], separator="_") + \
                        '_health_check'
                    with_health_check.append({
                            'acl_name': acl_name,
                            'service': '/health-check/estimation-model/' +
                                       x['model'] + '/',
                            'backend': x['backend']})
            if x['admin']:
                # Gui admin service
                acl_name_gui = slugify(x['service'], separator="_") + \
                    '__admin_gui'
                backend_name_gui = x['backend'] + '__admin_gui'
                admin_acls.append({
                    'acl_name': acl_name_gui,
                    'url_beg': '/admin/' + x['service'] + '/gui/',
                    'backend': backend_name_gui})

                service_admin_gui = x['service'] + '-admin-gui'
                admin_backends.append({
                    'service': service_admin_gui,
                    'backend': backend_name_gui
                })

                # Static files for admin site
                acl_name_static = slugify(x['service'], separator="_") + \
                    '__admin_static'
                backend_name_static = x['backend'] + '__admin_static'
                admin_acls.append({
                    'acl_name': acl_name_static,
                    'url_beg': '/admin/' + x['service'] + '/static/',
                    'backend': backend_name_static})

                service_admin_static = x['service'] + '-admin-static'
                admin_backends.append({
                    'service': service_admin_static,
                    'backend': backend_name_static
                })

        haproxy_config_text = haproxy_config_template.render(
            user=self.haproxy_stats_user,
            password=self.haproxy_stats_password,
            acls=self.haproxy_acls,
            srvs_with_health_check=with_health_check,
            admin_acls=admin_acls,
            admin_backends=admin_backends,
            services=self.haproxy_services,
            kube_dns_ip=self.kube_dns_ip)

        ##################
        # Haproxy Secrets#
        with open(os.path.join(self.base_path,
                  'resources_yml/haproxy__secrets.yml'), 'r') as file:
            haproxy_secrets__text = file.read()
        haproxy_secrets__text_formated = haproxy_secrets__text.format(
            user=self._haproxy_stats_user,
            password=self._haproxy_stats_password)

        ##################
        # Haproxy Service#
        with open(os.path.join(self.base_path,
                  'resources_yml/haproxy_service.yml'), 'r') as file:
            haproxy_service__text = file.read()

        #################
        # Haproxy Deploy#
        with open(os.path.join(self.base_path,
                  'resources_yml/haproxy_deploy.yml'), 'r') as file:
            haproxy_deploy_text = file.read()

        ################
        # NGINX Service#
        with open(os.path.join(self.base_path,
                  'resources_yml/nginx-ssl__service.jinja2'), 'r') as file:
            nginx_service_template = Template(file.read())
        nginx_service_text = nginx_service_template.render(
            public_ip=self.gateway_public_ip,
            firewall_ips=self.firewall_ips)

        ###############
        # NGINX Deploy#
        with open(os.path.join(self.base_path,
                  'resources_yml/nginx-ssl__deploy.yml'), 'r') as file:
            nginx_deploy_text = file.read()
        nginx_deploy_text_format = nginx_deploy_text.format(
            server_name=self.gateway_public_ip,
            version=self.version_nginx_gateway)

        with open(os.path.join(self.base_path,
                  'resources_yml/nginx-ssl__secrets.yml'), 'r') as file:
            nginx_secrets_text = file.read()

        nginx_secrets_text_formated = nginx_secrets_text.format(
            nginx_ssl_cert=self._nginx_ssl_cert,
            nginx_ssl_key=self._nginx_ssl_key,
            nginx_ssl_dhparam=self._nginx_ssl_dhparam)

        to_return = [
            # HAProxy
            {'type': 'services', 'name': 'haproxy__services',
             'content': haproxy_service__text, 'sleep': 0},
            {'type': 'configmap', 'name': 'haproxy-load-balancer-config',
             'content': haproxy_config_text, 'file_name': 'haproxy.cfg',
             'sleep': 5},
            {'type': 'secrets', 'name': 'haproxy__secrets',
             'content': haproxy_secrets__text_formated, 'sleep': 5},
            {'type': 'deploy', 'name': 'haproxy__deploy',
             'content': haproxy_deploy_text, 'sleep': 0},

            # NGINX Gateway
            {'type': 'services', 'name': 'nginx__services_loadbalancer',
             'content': nginx_service_text, 'sleep': 5},
            {'type': 'deploy', 'name': 'nginx__deploy',
             'content': nginx_deploy_text_format, 'sleep': 0},
            {'type': 'secrets', 'name': 'nginx__secrets',
             'content': nginx_secrets_text_formated, 'sleep': 5}
        ]

        return to_return
