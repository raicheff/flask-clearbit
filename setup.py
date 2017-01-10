from setuptools import setup


setup(
    name='flask-clearbit',
    version='0.1.1',
    description='Flask-Clearbit',
    author='Boris Raicheff',
    author_email='b@raicheff.com',
    url='https://github.com/raicheff/flask-clearbit',
    install_requires=['flask', 'clearbit', 'itsdangerous', 'six'],
    py_modules=['flask_clearbit'],
)
