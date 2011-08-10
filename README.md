SSHim is a library for testing and debugging SSH automation clients. The aim is to provide a scriptable SSH server which can be made to behave like any SSH-enabled device.

Currently SSHim does just enough to fire up an SSH server using Paramiko and read and write values. Eventually it could be expanded to support additional channel types, scripted tunneling and more.

To install egg in development mode:

```
python setup.py develop -N
```

Example:

```python
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
```

Because SSHim uses Python to script the SSH server complicated emulated interfaces can be created to use branching, stored state and looping, e.g:

```python
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
```