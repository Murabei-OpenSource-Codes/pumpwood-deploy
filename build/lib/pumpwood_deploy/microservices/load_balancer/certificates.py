"""Module to generate NGINX certificates for SSL encription."""

import os
import shutil
import random
import string
import subprocess
import pathlib


def create_nginx_ssl_certificates(cert_pass_phrase=None):
    """Create nginx ssl certificates."""
    file_path = os.path.dirname(__file__)

    if cert_pass_phrase is None:
        cert_pass_phrase = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for i in range(20)])

    script_file = os.path.join(file_path, 'resources/setup_certs.sh')
    ssl_config_file = os.path.join(file_path, 'resources/ssl_config.txt')

    tmp_location = 'outputs/nginx_certificates/'
    if os.path.exists(tmp_location):
        shutil.rmtree(tmp_location)
    os.makedirs(tmp_location)

    dirpath = os.getcwd()
    file_proxycert = dirpath + "/" + tmp_location + 'nginx_proxycert'
    file_proxykey = dirpath + "/" + tmp_location + 'nginx_proxykey'
    file_dhparam = dirpath + "/" + tmp_location + 'nginx_dhparam'

    print('== Creating nginx gateway certificates ==')
    cmd = ' '.join(
        [script_file, tmp_location, cert_pass_phrase, ssl_config_file])
    print(cmd)
    subprocess.call(cmd, shell=True)

    with open(file_proxycert, 'r') as file:
        proxycert = file.read()

    with open(file_proxykey, 'r') as file:
        proxykey = file.read()

    with open(file_dhparam, 'r') as file:
        dhparam = file.read()

    return {'proxycert': proxycert, 'proxykey': proxykey, 'dhparam': dhparam}
