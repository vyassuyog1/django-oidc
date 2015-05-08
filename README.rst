Django OpenID Connect (OIDC) authentication provider
====================================================

**WARNING**: work in progress.

This module makes it easy to integrate OpenID Connect as an authentication source in a Django project.

Behind the scene, it uses Roland Hedberg's pyoidc library.

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

* add `'djangooidc.middleware.OpenIdMiddleware'` to MIDDLEWARE_CLASSES
* add `'djangooidc.backends.OpenIdUserBackend'` to AUTHENTICATION_BACKENDS
  (note: the default `'django.contrib.auth.backends.ModelBackend'` must be present **before** the oidc backend)
* set LOGIN_URL = 'openid'
* add the specific OIDC parameters (change the absolute URLs to yours)::

    ##################################
    # OIDC

    # If we should check certificates
    VERIFY_SSL = True

    # The view for OIDC login uses a default template - it can be overridden here
    # OIDC_LOGIN_TEMPLATE = "fed_login.html"

    # You may want to disable client registration. In that case, only the OP inside OIDC_CLIENTS will be available.
    # OIDC_ALLOW_DYNAMIC_OP = False

    # Information used when registering the client, this may be the same for all OPs
    # Ignored if auto registration is not used.
    OIDC_ME = {
        "application_type": "web",
        "contacts": ["ops@example.com"],
        "redirect_uris": ["http://localhost:8000/openid/callback", ],
        "post_logout_redirect_uris": ["http://localhost:8000/", ]
    }

    # Default is using the 'code' workflow, which requires direct connectivity from website to the OP.
    OIDC_BEHAVIOUR = {
        "response_type": "code",
        "scope": ["openid", "profile", "email", "address", "phone"],
    }

    # The keys in this dictionary are the OPs (OpenID Providers) short user friendly name not the issuer (iss) name.
    OIDC_CLIENTS = {
        # The ones that support webfinger, OP discovery and client registration
        # This is the default, any client that is not listed here is expected to
        # support dynamic discovery and registration.
        "": {
            "client_info": OIDC_ME,
            "behaviour": OIDC_BEHAVIOUR
        },
    }

In addition, you may want to use a specific OpenID Connect provider that is not auto-discoverable. This is done
by adding items to the OIDC_CLIENTS dictionary. For example, an Azure AD OP would be::

    "Azure Active Directory": {
        "srv_discovery_url": "https://sts.windows.net/aaaaaaaa-aaaa-1111-aaaa-xxxxxxxxxxxxx/",
        "behaviour": OIDC_BEHAVIOUR,
        "client_registration": {
            "client_id": "your_client_id",
            "client_secret": "your_client_secret",
            "redirect_uris": ["http://localhost:8000/openid/callback/"],
            "post_logout_redirect_uris": ["http://localhost:8000/"],
        }
    }

Then add this to urls.py::

    url(r'openid/', include('djangooidc.urls')),


You may now test the authentication by going to (on the development server) http://localhost:8000/openid/login


Features
--------

* Simple ready to use Django authentication provider
