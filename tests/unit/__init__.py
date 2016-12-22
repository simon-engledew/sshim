import paramiko
from contextlib import contextmanager, closing

from sshim.Server import DEFAULT_KEY

@contextmanager
def connect(server):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server.address, port=server.port, pkey=DEFAULT_KEY, look_for_keys=False)
        with closing(ssh.invoke_shell()) as channel:
            with closing(channel.makefile('rw')) as fileobj:
                yield fileobj
