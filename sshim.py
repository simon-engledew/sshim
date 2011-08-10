import paramiko, threading, socket, select, os, re
from StringIO import StringIO
import logging, subprocess
logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

class SSHim(threading.Thread):
    def __init__(self, script, address='127.0.0.1', port=22):
        threading.Thread.__init__(self)
        self.script = script
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((address, port))

        private_key_path = os.path.join(os.path.dirname(__file__), 'private.key')
        if not os.path.exists(private_key_path):
            raise IOError("File not found: {0} - expected to find a private key.".format(private_key_path))
        self.key = paramiko.RSAKey(filename=private_key_path)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()

    def stop(self):
        self.socket.close()

    def check_channel_request(self, kind, channel_id):
        if kind in ('session',):
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        return False

    def check_auth_none(self, username):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return ('password', 'publickey', 'none')

    def check_channel_shell_request(self, channel):
        channel.setblocking(True)
        Actor(self.script, channel).start()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def run(self):
        try:
            self.socket.listen(5)
            while True:
                socket, address = self.socket.accept()
                transport = paramiko.Transport(socket)
                transport.add_server_key(self.key)
                transport.start_server(server=self)
        except select.error as (code, message):
            pass
        finally:
            self.stop()

class Actor(threading.Thread):
    def __init__(self, script, channel):
        threading.Thread.__init__(self)
        self.daemon = True
        self.script = script
        self.channel = channel

    def run(self):
        try:
            self.script(Script(self.channel.makefile('rw')))
        finally:
            self.channel.close()

class Script(object):
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.values = {}

    def __rshift__(self, line):
        self.fileobj.write(line % self.values)

    def __lshift__(self, line):
        line = re.compile(line)
        buffer = StringIO()
        while True:
            byte = self.fileobj.read(1)

            if not byte:
                break
            elif byte == '\t':
                pass
            elif byte == '\x7f':
                if buffer.len > 0:
                    self.fileobj.write('\b \b')
                    buffer.truncate(buffer.len - 1)
            elif byte == '\x04':
                raise EOFError()
            elif byte == '\x1b' and self.fileobj.read(1) == '[':
                print 'cursor:', self.fileobj.read(1)
            elif byte in ('\n', '\r'):
                break
            else:
                logger.debug(repr(byte))
                buffer.write(byte)
                self.fileobj.write(byte)
        self.fileobj.write('\r\n')
        match = line.match(buffer.getvalue())
        if match:
            self.values.update(match.groupdict())
        else:
            raise ValueError('failed to match "%s" against "%s"' % (line, buffer.getvalue()))

if __name__ == '__main__':
    def hello_world(script):
        script >> 'Please enter your name: '
        script << '(?P<name>.*)'
        script >> 'Hello %(name)s!\r\n'

    server = SSHim(hello_world, port=3000)
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()

