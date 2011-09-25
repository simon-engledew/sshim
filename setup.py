from setuptools import setup, find_packages

setup(
    name='sshim',
    version='0.1',

    description='Scriptable SSH server for testing SSH clients.',
    author="Simon Engledew",
    author_email="simon@engledew.com",
    url="http://www.engledew.com",

    install_requires = [
        'paramiko>=1.7.7.1',
        'pycrypto>=2.3',
    ],
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
