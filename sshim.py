# -*- coding: utf-8 -*-

import paramiko, threading, socket, select, os, re
from StringIO import StringIO
import logging, subprocess
logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

DEFAULT_KEY = paramiko.RSAKey(file_obj=StringIO("""-----BEGIN RSA PRIVATE KEY-----
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
    def __init__(self, script, address='127.0.0.1', port=22, key=DEFAULT_KEY):
        threading.Thread.__init__(self)
        self.script = script
        self.daemon = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((address, port))
        self.key = key

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

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

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
