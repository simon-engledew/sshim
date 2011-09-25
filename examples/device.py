import sshim, re, shlex, threading
from datetime import datetime
import logging
logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

class Device(threading.Thread):
    def __init__(self, script):
        threading.Thread.__init__(self)
        self.history = []
        self.script = script
        self.start()

    def adduser(self, *args):
        username = args[0]
        self.script.writeline('user %s add!' % username)

    commands = {'adduser': adduser}

    def cursor(self, key):
        if key == 'A':
            self.script.writeline('up')

    def prompt(self):
        self.script.write('root@device # ')

    def run(self):
        while True:
            self.prompt()
            match = self.script.expect(re.compile('(?P<command>\S+)?\s*(?P<arguments>.*)'))
            self.history.append(match.group(0))
            groups = match.groupdict()
            if groups['command'] == 'exit':
                break
            if groups['command'] in Device.commands:
                Device.commands[groups['command']](self, *shlex.split(groups['arguments']))
            else:
                self.script.writeline('-bash: %s: command not found' % groups['command'])

server = sshim.Server(Device, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()