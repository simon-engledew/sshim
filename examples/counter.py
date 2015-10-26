import logging
logging.basicConfig(level='DEBUG')

import sshim, time, re
from six.moves import range

# define the callback function which will be triggered when a new SSH connection is made:
def counter(script):
    while True:
        for n in range(0, 10):
            # send the numbers 0 to 10 to the client with a little pause between each one for dramatic effect:
            script.writeline(n)
            time.sleep(0.1)

        # ask them if they are interested in seeing the show again
        script.write('Again? (y/n): ')

        # parse their input with a regular expression and pull it into a named group
        groups = script.expect(re.compile('(?P<again>[yn])')).groupdict()

        # if they didn't say yes, break out the loop and disconnect them
        if groups['again'] != 'y':
            break

# create a server and pass in the callback method
# connect to it using `ssh localhost -p 3000`
server = sshim.Server(counter, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()
