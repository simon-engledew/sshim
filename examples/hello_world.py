import logging
import re
import sshim

logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

# define the callback function which will be triggered when a new SSH connection is made:
def hello_world(script):
	# ask the SSH client to enter a name
    script.write('Please enter your name: ')

    # match their input against a regular expression which will store the name in a capturing group called name
    groups = script.expect(re.compile('(?P<name>.*)')).groupdict()

    # log on the server-side that the user has connected
    logger.info('%(name)s just connected'.format(**groups))

    # send a message back to the SSH client greeting it by name
    script.writeline('Hello %(name)s!' % groups)

# create a server and pass in the callback method
# connect to it using `ssh localhost -p 3000`
server = sshim.Server(hello_world, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()
