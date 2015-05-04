from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

from os import path

BASEDIR = path.dirname(path.abspath(__file__))

urlpatterns = patterns('',
                       # URLS for OpenId authentication
                       url(r'openid/', include('oidc_django.urls')),

                       # Test URLs
                       url(r'^$', 'testapp.views.home', name='home'),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),

                       )
