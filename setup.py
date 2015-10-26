from setuptools import setup, find_packages

setup(
    name='sshim',
    version='1.1',

    description='Scriptable SSH server for testing SSH clients.',
    author="Simon Engledew",
    author_email="simon@engledew.com",
    url="http://www.engledew.com",

    install_requires = [
        'paramiko',
        'six'
    ],
    extras_require = {
      'tests': [
        'nose'
      ]
    },
    zip_safe=True,
    include_package_data=False,
    packages=find_packages(),
    license='MIT',
    keywords = [
        'ssh',
        'paramiko',
        'testing'
    ],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
