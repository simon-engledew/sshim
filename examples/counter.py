import sshim, time

def hello_world(script):
    while True:
        for n in xrange(0, 10):
            script.writeline(n)
            time.sleep(0.1)
        script.write('Again? (y/n): ')
        script.expect('(?P<again>[yn])')
        if script['again'] != 'y': break

server = sshim.Server(hello_world, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()