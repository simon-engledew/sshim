# encoding: utf8

import paramiko, threading, socket, select, os, re, traceback, errno, inspect, logging, subprocess
from StringIO import StringIO

logger = logging.getLogger(__name__)

DEFAULT_KEY = paramiko.RSAKey(file_obj=
StringIO("""-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAnahBtR7uxtHmk5UwlFfpC/zxdxjUKPD8UpNOOtIJwpei7gaZ
+Jgub5GFJtTG6CK+DIZiR4tE9JxMjTEFDCGA3U4C36shHB15Pl3bLx+UxdyFylpc
c7XYp4fpQjhFUoHOAIl5ZaA223kIxi7sFXtM1Gjy6g49u+G5teVfMbeZnks2xjjy
F84qVADFBXCsfjrY5m4R+Wnfups/jP1agOpnOvqHlX/bpvzEZRcwJ0A8CylBZzQP
D1Y4EXy1B4QLyLJKFIMRkWnr0f8rK5Q/obCLTjl+IMmZrkItbfC/hYCy6TDi+Efn
cgGw02L93Mf6QGDNc21BsRELPYMME22MmpLphQIBIwKCAQEAmScbQjtOWr1GY3r7
/dG90SGaG+w70AALDmM2DUEQy6k/MF4vLAGMMd3RzfNE4YDV4EgHszbVRWSiIsHn
pWJf7OyyVZ7s9r2LuO111gFr82iB98V+YcaX8zOSIxIXdLicOwk0GZRSjA8tGErW
tcg8AYqFkulDSMylxqRN2IZ3+NnTROxh4uUFH57roSYoCvzjM2v1Xa+S42BLpBD1
3mLAJD36JhOhMTgYUgHAROx9+YUUUzYk3jpkTGWnAYSumnJXQYphLE9zadXxh94N
HZJdvXajuP5N2M3Q2b4Gbyt2wNFlNcHGA+Zwk8wHIBnY9Sb9Gz0QALsOAwUoRY8T
rCysSwKBgQDPVjFdSgM3jScmFV9fVnx3iNIlM6Ea7+UCrOOCvcGtzDo5vuTPktw7
8abHEFHw7VrtxI3lRQ41rlmK3B//Q7b+ZJ0HdZaRdyCqW1u91tq1tQe7yiJBm0c5
hZ3F0Vr6HAXoBVOux5wUq55jvUJ8dCVYNYfctZducVmOos3toDkSzQKBgQDCqRQ/
GO5AU3nKfuJ+SZvv8/gV1ki8pGmyxkSebUqZSXFx+rQEQ1e6tZvIz/rYftRkXAyL
XfzXX8mU1wEci6O1oSLiUBgnT82PtUxlO3Peg1W/cpKAaIFvvOIvUMRGFbzWhuj7
4p4KJjZWjYkAV2YlZZ8Br23DFFjjCuawX7NhmQKBgHCN4EiV5H09/08wLHWVWYK3
/Qzhg1fEDpsNZZAd3isluTVKXvRXCddl7NJ2kuHf74hjYvjNt0G2ax9+z4qSeUhF
P00xNHraRO7D4VhtUiggcemZnZFUSzx7vAxNFCFfq29TWVBAeU0MtRGSoG9yQCiS
Fo3BqfogRo9Cb8ojxzYXAoGBAIV7QRVS7IPheBXTWXsrKRmRWaiS8AxTe63JyKcm
XwoGea0+MkwQ67M6s/dqCxgcdGITO81Hw1HbSGYPxj91shYlWb/B5K0+CUyZk3id
y8vHxcUbXSTZ8ls/sQqAhpZ1Tkn2HBpvglAaM+OUQK/G5vUSe6liWeTawJuvtCEr
rjRLAoGAUNNY4/7vyYFX6HkX4O2yL/LZiEeR6reI9lrK/rSA0OCg9wvbIpq+0xPG
jCrc8nTlA0K0LtEnE+4g0an76nSWUNiP4kALROfZpXajRRaWdwFRAO17c9T7Uxc0
Eez9wYRqHiuvU0rryYvGyokr62w1MtJO0tttnxe1Of6wzb1WeCU=
-----END RSA PRIVATE KEY-----"""))

class Server(threading.Thread):
    """
        
    """
    def __init__(self, script, address='127.0.0.1', port=22, key=None):
        threading.Thread.__init__(self)
        self.script = script
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((address, port))
        self.key = key or DEFAULT_KEY

    @property
    def address(self):
        address, port = self.socket.getsockname()
        return address
    
    @property
    def port(self):
        address, port = self.socket.getsockname()
        return port

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()

    def stop(self):
        """
            Stop the server, waiting for the runloop to exit.
        """
        logging.info('stopping')
        self.socket.close()
        if self.is_alive():
            self.join()

    def run(self):
        """
            Synchronously start the server in the current thread, blocking indefinitely.
        """
        try:
            self.socket.listen(5)
            logging.info('listening on port %d', self.port)
            while True:
                r, w, x = select.select([self.socket], [], [], 1)
                if r:
                    Client(self, self.socket.accept())
        except (select.error, socket.error) as (code, message):
            if code != errno.EBADF:
                raise

class Client(object):
    def __init__(self, server, (client, (address, port))):
        self.server = server
        self.address, self.port = address, port
        self.transport = paramiko.Transport(client)
        self.transport.add_server_key(self.server.key)
        self.transport.start_server(server=self)

    def check_channel_request(self, kind, channel_id):
        if kind in ('session',):
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        logger.warning('paramiko.Channel(%d) was denied an exec request', channel.chanid)
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
        logger.debug('paramiko.Channel(%d) was granted a shell request', channel.chanid)
        channel.setblocking(True)
        Actor(self, channel).start()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        logger.debug('paramiko.Channel(%d) was granted a pty request', channel.chanid)
        return True

class Actor(threading.Thread):
    def __init__(self, client, channel):
        threading.Thread.__init__(self)
        self.daemon = True
        self.client = client
        self.channel = channel

    @property
    def script(self):
        return self.client.server.script

    def run(self):
        try:
            fileobj = self.channel.makefile('rw')
            try:
                value = self.script(Script(self.script, fileobj, self.client.transport))
                if isinstance(value, threading.Thread):
                    value.join()
            except:
                fileobj.write('\r\n' + traceback.format_exc().replace('\n', '\r\n'))
                raise
        finally:
            self.channel.close()

class Script(object):
    """
    """
    def __init__(self, delegate, fileobj, transport):
        self.delegate = delegate
        self.transport = transport
        self.fileobj = fileobj
        self.values = {}

    @property
    def username(self):
        return self.transport.get_username()

    def write(self, line):
        """
            Send str(line) to the client.
        """
        self.fileobj.write(str(line))

    def writeline(self, line):
        """
            Send str(line) to the client and append a carriage return and newline.
        """
        self.fileobj.write(str(line) + '\r\n')

    def expect(self, line):
        """
            Expect a line of input from the user. If this has the `match` method, it will call it on the input and return
            the result, otherwise it will use the equality operator, ==. Notably, if a regular expression is passed in
            its match method will be called and the matchdata returned. This allows you to use matching groups to pull
            out interesting data and operate on it.
        """
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
                command = self.fileobj.read(1)
                if hasattr(self.delegate, 'cursor'):
                    self.delegate.cursor(command)
                logger.debug('cursor: %s', command)
            elif byte in ('\r', '\n'):
                break
            else:
                logger.debug(repr(byte))
                buffer.write(byte)
                self.fileobj.write(byte)
        self.fileobj.write('\r\n')

        if hasattr(line, 'match'):
            match = line.match(buffer.getvalue())
            if match:
                return match
        else:
            if line == buffer.getvalue():
                return line

        raise ValueError('failed to match "%s" against "%s"' % (line, buffer.getvalue()))
