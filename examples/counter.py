import sshim, time, re
import logging
logging.basicConfig(level='DEBUG')

def counter(script):
    while True:
        for n in xrange(0, 10):
            script.writeline(n)
            time.sleep(0.1)

        script.write('Again? (y/n): ')

        groups = script.expect(re.compile('(?P<again>[yn])')).groupdict()

        if groups['again'] != 'y':
            break

server = sshim.Server(counter, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()
