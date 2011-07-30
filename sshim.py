import paramiko, threading, socket, select, os, re
from StringIO import StringIO
import logging, subprocess
logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

class SSHim(threading.Thread):
    def __init__(self, script, port):
        threading.Thread.__init__(self)
        self.script = script
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('127.0.0.1', port))
        self.key = paramiko.RSAKey(filename=os.path.join(os.path.dirname(__file__), 'private.key'))
    
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
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        self.script(channel).start()
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
        self.values = {}
    
    def run(self):
        fileobj = self.channel.makefile('rw')
        try:
            for statement in self.script.statements:
                statement(self, fileobj)
        finally:
            print self.values
            self.channel.close()

class Call(object):
    def __init__(self, value):
        self.value = value
    
    def __call__(self, actor, fileobj):
        fileobj.write(self.value % actor.values)

class Response(object):
    def __init__(self, value):
        self.value = value
    
    def __call__(self, actor, fileobj):
        buffer = StringIO()
        while True:
            byte = fileobj.read(1)
            
            if not byte:
                break
            elif byte == '\t':
                pass
            elif byte == '\x7f':
                if buffer.len > 0:
                    fileobj.write('\b \b')
                    buffer.truncate(buffer.len - 1)
            elif byte == '\x04':
                raise EOFError()
            elif byte == '\x1b' and fileobj.read(1) == '[':
                print 'cursor:', fileobj.read(1)
            elif byte in ('\n', '\r'):
                break
            else:
                print repr(byte)
                buffer.write(byte)
                fileobj.write(byte)
        fileobj.write('\r\n')
        match = self.value.match(buffer.getvalue())
        if match:
            actor.values.update(match.groupdict())

class Script(object):
    def __init__(self):
        self.statements = []
    
    def __call__(self, fileobj):
        return Actor(self, fileobj)
    
    def __rshift__(self, other):
        self.statements.append(Call(other))
    
    def __lshift__(self, other):
        self.statements.append(Response(other))

if __name__ == '__main__':
    script = Script()
    script >> 'Please enter your name: '
    script << re.compile('(?P<name>.*)')
    script >> 'Thanks %(name)s!\r\n'
    
    server = SSHim(script, 3000)
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
    