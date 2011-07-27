import paramiko, threading, socket, select, os
from StringIO import StringIO
import logging, subprocess
logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

class Host(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('127.0.0.1', port))
    
    def stop(self):
        self.socket.close()
    
    def run(self):
        logger.debug('Host.run')
        try:
            self.socket.listen(5)
            while True:
                read, write, exception = select.select((self.socket,), [], [],  1)
                for connection in read:
                    Connection(*connection.accept()).start()
        except select.error as (code, message):
            pass
        finally:
            logger.debug('~ Host.run')
            self.socket.close()

class Connection(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        logger.info('Client connected from %s:%d' % address)
        self.socket = socket
        self.daemon = True
    
    def check_channel_request(self, kind, channel_id):
        if kind in ('session',):
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        Exec(channel, command).start()
        return True

    def check_auth_none(self, username):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        PTY(channel).start()
        return True

    def stop(self):
        self.socket.close()

    def run(self):
        try:
            transport = paramiko.Transport(self.socket)
            transport.add_server_key(paramiko.RSAKey(filename=os.path.join(os.path.dirname(__file__), 'private.key')))
            transport.start_server(server=self)
            while transport.is_active():
                channel = transport.accept()
                channel.setblocking(True)
        finally:
            self.socket.close()

class ChannelListener(threading.Thread):
    def __init__(self, channel):
        logger.debug(channel)
        threading.Thread.__init__(self)
        self.daemon = True
        self.channel = channel
    
    def run(self):
        self.stop()
    
    def stop(self):
        self.channel.send_exit_status(0)
        self.channel.close()

class Exec(ChannelListener):
    def __init__(self, channel, command):
        ChannelListener.__init__(self, channel)
        self.channel.setblocking(False)
        print command

class PTY(ChannelListener):
    def __init__(self, channel):
        ChannelListener.__init__(self, channel)
        self.channel.setblocking(True)

    def stop(self):
        self.channel.close()
    
    def run(self):
        try:
            bytes = StringIO()
            prompt = ">> "

            bytes.write(prompt)
            self.channel.send(prompt)
            
            while True:
                byte = self.channel.recv(1)

                if not byte or byte == '\x04':
                    break
                elif byte in ('\n', '\r'):
                    self.channel.send('\n')
                    self.channel.send('\033[%dD' % bytes.len)

                    bytes.write(prompt)
                    self.channel.send(prompt)

                    bytes.truncate()
                else:
                    bytes.write(byte)
                    self.channel.send(byte)

        except socket.timeout:
            pass
        finally:
            self.stop()

if __name__ == '__main__':
    host = Host(3000)
    try:
        host.run()
    except KeyboardInterrupt:
        host.stop()
    