To install egg in development mode:

```
python setup.py develop -N
```

Example:

```python
import sshim

def hello_world(script):
    script >> 'Please enter your name: '
    script << '(?P<name>.*)'
    print script['name'], 'just connected'
    script >> 'Hello %(name)s!\r\n'

server = sshim.Server(hello_world, port=3000)
try:
    server.run()
except KeyboardInterrupt:
    server.stop()
```
