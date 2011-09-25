# encoding: utf8

"""
SSHim is a library for testing and debugging SSH automation clients. The aim is to provide a scriptable SSH server which can be made to behave like any SSH-enabled device.

Currently SSHim does just enough to fire up an SSH server using Paramiko and read and write values. Eventually it could be expanded to support additional channel types, scripted tunneling and more.

To install as an egg-link in development mode::

    python setup.py develop -N

To run from the folder direct::

    PYTHONPATH=. python examples/counter.py

Or to run the tests::

    nosetests -x -s -w tests/

Example:

.. literalinclude:: examples/hello_world.py

Because SSHim uses Python to script the SSH server, complicated emulated interfaces can be created using branching, stored state and looping, e.g:

.. literalinclude:: examples/counter.py
"""

from Server import Server
