# encoding: utf8

import ssh
import threading
import socket
import select
import traceback
import errno
import logging
import Queue as queue
import sys

from StringIO import StringIO

logger = logging.getLogger(__name__)

DEFAULT_KEY = ssh.RSAKey(file_obj=
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

class Counter(object):
    def __init__(self, mutex=None):
        self.mutex = mutex or threading.Lock()
        self.count = 0
        self.condition = threading.Condition(self.mutex)

    def __enter__(self):
        self.count += 1

    def __exit__(self, *exc_info):
        with self.condition:
            count = self.count - 1
            if count <= 0:
                if count < 0:
                    raise ValueError('Count decremented below zero')
                self.condition.notify_all()
            self.count = count

    def join(self):
        with self.condition:
            while self.count:
                self.condition.wait()

class Handler(object):
    def __init__(self, server, (client, (address, port))):
        self.server = server
        self.address, self.port = address, port
        self.transport = ssh.Transport(client)
        self.transport.add_server_key(self.server.key)
        self.transport.start_server(server=self)

    def check_channel_request(self, kind, channel_id):
        if kind in ('session',):
            return ssh.OPEN_SUCCEEDED
        return ssh.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        logger.warning('ssh.Channel(%d) was denied an exec request', channel.chanid)
        return False

    def check_auth_none(self, username):
        return ssh.AUTH_SUCCESSFUL

    def check_auth_password(self, username, password):
        return ssh.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return ssh.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return ('password', 'publickey', 'none')

    def check_channel_shell_request(self, channel):
        logger.debug('ssh.Channel(%d) was granted a shell request', channel.chanid)
        channel.setblocking(True)
        Actor(self, channel).start()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        logger.debug('ssh.Channel(%d) was granted a pty request', channel.chanid)
        return True

class Server(threading.Thread):
    """

    """
    def __init__(self, delegate, address='127.0.0.1', port=22, key=None, handler=Handler):
        threading.Thread.__init__(self, name='sshim.Server')
        self.exceptions = queue.Queue()

        self.counter = Counter()
        self.handler = handler

        self.delegate = delegate
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
        if not self.exceptions.empty():
            exc_info = self.exceptions.get()
            raise exc_info[0], exc_info[1], exc_info[2]

    def join(self):
        self.counter.join()
        threading.Thread.join(self)

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
                    self.handler(self, self.socket.accept())
        except (select.error, socket.error) as (code, message):
            if code != errno.EBADF:
                raise

class Actor(threading.Thread):
    def __init__(self, client, channel):
        threading.Thread.__init__(self, name='sshim.Actor(%s)' % channel.get_id())
        self.daemon = True
        self.client = client
        self.channel = channel

    @property
    def delegate(self):
        return self.server.delegate

    @property
    def server(self):
        return self.client.server

    def run(self):
        with self.server.counter:
            try:
                fileobj = self.channel.makefile('rw')
                try:
                    value = self.delegate(Script(self.delegate, fileobj, self.client.transport))

                    if isinstance(value, threading.Thread):
                        value.join()

                except:
                    exc_info = sys.exc_info()
                    exception_string = traceback.format_exc()
                    try:
                        fileobj.write('\r\n' + exception_string.replace('\n', '\r\n'))
                    except:
                        pass
                    raise exc_info[0], exc_info[1], exc_info[2]
            except:
                self.server.exceptions.put_nowait(sys.exc_info())
            finally:
                try:
                    self.channel.close()
                except EOFError:
                    logger.debug('Channel already closed')

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
        try:
            self.fileobj.write(str(line))
        except socket.error:
            pass
        except EOFError:
            pass

    def writeline(self, line):
        """
            Send str(line) to the client and append a carriage return and newline.
        """
        self.write(str(line) + '\r\n')

    def expect(self, line):
        """
            Expect a line of input from the user. If this has the `match` method, it will call it on the input and return
            the result, otherwise it will use the equality operator, ==. Notably, if a regular expression is passed in
            its match method will be called and the matchdata returned. This allows you to use matching groups to pull
            out interesting data and operate on it.
        """
        buffer = StringIO()

        try:
            while True:
                byte = self.fileobj.read(1)

                if not byte or byte == '\x04':
                    raise EOFError()
                elif byte == '\t':
                    pass
                elif byte == '\x7f':
                    if buffer.len > 0:
                        self.write('\b \b')
                        buffer.truncate(buffer.len - 1)
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
                    self.write(byte)
            value = buffer.getvalue().decode('utf-8')

            self.write('\r\n')

            if hasattr(line, 'match'):
                match = line.match(value)
                if match is not None:
                    return match
            else:
                if line == value:
                    return line
        except:
            logger.exception('Exception in actor')

        raise AssertionError('failed to match "%s" against "%s"' % (line.encode('utf-8'), value.encode('utf-8')))
