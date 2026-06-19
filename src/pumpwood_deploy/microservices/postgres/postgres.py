"""Postgres helper functions for Pumpwood deploy."""
import os
import subprocess # NOQA


def create_ssl_key_ssl_crt():
    """Create a self-signed SSL key and certificate for Postgres.

    Generates temporary files under ``temp/``, reads their contents,
    and removes the local files before returning.

    Returns:
        dict:
            Mapping with ``ssl_key`` and ``ssl_crt`` PEM contents.

    Raises:
        OSError:
            If temporary files cannot be created, read, or removed.
        subprocess.SubprocessError:
            If OpenSSL certificate generation fails.
    """
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

    process = subprocess.run(
        bash_cmd_1.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False)
    if process.returncode != 0:
        msg = "OpenSSL certificate generation failed"
        raise subprocess.SubprocessError(msg)

    with open(key_path, 'r') as file:
        ssl_key = file.read()

    with open(cert_path, 'r') as file:
        ssl_crt = file.read()

    os.remove(key_path)
    os.remove(cert_path)
    return {'ssl_key': ssl_key, 'ssl_crt': ssl_crt}
