import sshim, re

def hello_world(script):
    script.write('Please enter your name: ')
    groups = script.expect(re.compile('(?P<name>.*)')).groupdict()
    print '%(name)s just connected' % groups
    script.writeline('Hello %(name)s!' % groups)

server = sshim.Server(hello_world, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()