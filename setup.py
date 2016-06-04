"""Movie Bot setup"""

from setuptools import setup, find_packages

setup(
    name='moviebot',
    version='1.0',
    description=__doc__,
    packages=find_packages(),

    install_requires=('aiohttp', 'cchardet'),
    extras_requires={
        'gui': ('PyQt5'),
        'test' : ('pytest', 'pytest-flake8', 'pytest-coverage'),
        'doc' : ('Sphinx', 'sphinx_rtd_theme')
    }
)