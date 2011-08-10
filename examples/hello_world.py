import sshim

def hello_world(script):
    script >> 'Please enter your name: '
    script << '(?P<name>.*)'
    script >> 'Hello %(name)s!\r\n'

server = sshim.SSHim(hello_world, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()


