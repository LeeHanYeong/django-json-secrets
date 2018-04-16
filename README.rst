===================
django-json-secrets
===================

JSON secrets to Django settings module


Setup
=====

* install it via ``pip install django-json-secrets``

Usage
=====

* Setup 'SECRET_DIR' to settings module
  ::

      SECRETS_DIR = os.path.join(ROOT_DIR, '.secrets')

* Import library function
  ::

      from djs import import_secrets

* Execute function
  ::

      import_secrets()

* If there is a Python module needed to eval() the value of the secrets, define it in SECRETS_MODULES
  ::

      import requests

      SECRETS_MODULES = {
          'raven': 'raven',
          'requests': requests,
      }

Contributing
============

As an open source project, we welcome contributions.

The code lives on `github <https://github.com/LeeHanYeong/Django-Default-ImageField>`_.
