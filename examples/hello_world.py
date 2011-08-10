import sshim

def hello_world(script):
    script.write('Please enter your name: ')
    script.expect('(?P<name>.*)')
    print script['name'], 'just connected'
    script.writeline('Hello %(name)s!')

server = sshim.Server(hello_world, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()