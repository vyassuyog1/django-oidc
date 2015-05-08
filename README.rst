Django OpenID Connect (OIDC) authentication provider
====================================================

.. warning:: fork in progress - goal is to make it easily reusable. Pip packages are not available yet.

Django module that includes pyoidc relying party code into a Django application.


Documentation
-------------

The full documentation is at https://django-oidc.readthedocs.org.

Quickstart
----------

Install djangooidc::

    # Latest released package:
    pip install django-oidc
    
    # Latest code - unstable!
    pip install git+https://github.com/marcanpilami/django-oidc.git
    

Then to use it in a project, add this to your settings.py:

* add 'djangooidc.backends.OpenIdUserBackend' to your AUTHENTICATION_BACKENDS
* add 'djangooidc' to your INSTALLED_APPS
* set LOGIN_URL = 'openid'
* TODO: specific OIDC parameters


Features
--------

* Simple ready to use Django authentication provider
