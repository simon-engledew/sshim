
Using SSHim
***********

SSHim is a library for testing and debugging SSH automation clients.
The aim is to provide a scriptable SSH server which can be made to
behave like any SSH-enabled device.

Currently SSHim does just enough to fire up an SSH server using
Paramiko and read and write values. Eventually it could be expanded to
support additional channel types, scripted tunneling and more.

To install from pypi:

   pip install sshim

To install as an egg-link in development mode:

   python setup.py develop -N

To run from the folder direct:

   PYTHONPATH=. python examples/counter.py

Or to run the tests:

   nosetests -x -s -w tests/

Simple Example:

   import logging
   logging.basicConfig(level='DEBUG')
   logger = logging.getLogger()

   import sshim, re

   # define the callback function which will be triggered when a new SSH connection is made:
   def hello_world(script):
   	# ask the SSH client to enter a name
       script.write('Please enter your name: ')

       # match their input against a regular expression which will store the name in a capturing group called name
       groups = script.expect(re.compile('(?P<name>.*)')).groupdict()
       
       # log on the server-side that the user has connected
       logger.info('%(name)s just connected', **groups)
       
       # send a message back to the SSH client greeting it by name
       script.writeline('Hello %(name)s!' % groups)

   # create a server and pass in the callback method
   # connect to it using `ssh localhost -p 3000`
   server = sshim.Server(hello_world, port=3000)
   try:
       server.run()
   except KeyboardInterrupt:
       server.stop()

Because SSHim uses Python to script the SSH server, complicated
emulated interfaces can be created using branching, stored state and
looping, e.g:

   import logging
   logging.basicConfig(level='DEBUG')

   import sshim, time, re

   # define the callback function which will be triggered when a new SSH connection is made:
   def counter(script):
       while True:
           for n in xrange(0, 10):
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

class class sshim.Server(script, address='127.0.0.1', port=22, key=None)

   run()

      Synchronously start the server in the current thread, blocking
      indefinitely.

   stop()

      Stop the server, waiting for the runloop to exit.

class class sshim.Script(delegate, fileobj, transport)

   expect(line)

      Expect a line of input from the user. If this has the *match*
      method, it will call it on the input and return the result,
      otherwise it will use the equality operator, ==. Notably, if a
      regular expression is passed in its match method will be called
      and the matchdata returned. This allows you to use matching
      groups to pull out interesting data and operate on it.

   write(line)

      Send str(line) to the client.

   writeline(line)

      Send str(line) to the client and append a carriage return and
      newline.


Indices and tables
******************

* *Index*

* *Module Index*

* *Search Page*
