import paramiko
from contextlib import contextmanager

from sshim.Server import DEFAULT_KEY

@contextmanager
def connect(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server.address, port=server.port, pkey=DEFAULT_KEY, look_for_keys=False)
    channel = ssh.invoke_shell()
    fileobj = channel.makefile('rw')
    yield fileobj
    ssh.close()