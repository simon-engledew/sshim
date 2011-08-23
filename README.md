SSHim is a library for testing and debugging SSH automation clients. The aim is to provide a scriptable SSH server which can be made to behave like any SSH-enabled device.

Currently SSHim does just enough to fire up an SSH server using Paramiko and read and write values. Eventually it could be expanded to support additional channel types, scripted tunneling and more.

To install as an egg-link in development mode:

```
python setup.py develop -N
```

To run from the folder direct:

```
PYTHONPATH=. python examples/counter.py
```

Or to run the tests:

```
nosetests -x -s -w tests/
```

Example:

```python
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
```

Because SSHim uses Python to script the SSH server, complicated emulated interfaces can be created using branching, stored state and looping, e.g:

```python
import sshim, time, re

def counter(script):
    while True:
        for n in xrange(0, 10):
            script.writeline(n)
            time.sleep(0.1)
        script.write('Again? (y/n): ')
        groups = script.expect(re.compile('(?P<again>[yn])')).groupdict()
        if groups['again'] != 'y': break

server = sshim.Server(counter, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()
```