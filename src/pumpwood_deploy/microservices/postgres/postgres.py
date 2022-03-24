"""Postgres deploy fuctions."""
import os
import subprocess


def create_ssl_key_ssl_crt():
    """Create SSL key and Certificate for Postgres connections."""
    dir_temp_path = 'temp/'
    if not os.path.exists(dir_temp_path):
        os.makedirs(dir_temp_path)

    key_path = dir_temp_path + 'server.key'
    cert_path = dir_temp_path + 'server.crt'

    bash_cmd_text = """openssl req -new -x509 -days 365 -nodes -text """ +\
                    """-out {out} -keyout {keyout} -subj """ +\
                    """/CN=pumpwood.murabei.com"""
    bash_cmd_1 = bash_cmd_text.format(
        keyout=key_path, out=cert_path)

    process = subprocess.Popen(bash_cmd_1.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    with open(key_path, 'r') as file:
        ssl_key = file.read()

    with open(cert_path, 'r') as file:
        ssl_crt = file.read()

    os.remove(key_path)
    os.remove(cert_path)
    return {'ssl_key': ssl_key, 'ssl_crt': ssl_crt}
