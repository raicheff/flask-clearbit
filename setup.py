#
# Flask-Clearbit
#
# Copyright (C) 2017 Boris Raicheff
# All rights reserved
#


from setuptools import setup


setup(
    name='Flask-Clearbit',
    version='0.1.0',
    description='Flask-Clearbit',
    author='Boris Raicheff',
    author_email='b@raicheff.com',
    url='https://github.com/raicheff/flask-clearbit',
    install_requires=['flask', 'clearbit', 'itsdangerous', 'six'],
    py_modules=['flask_clearbit'],
)


# EOF
