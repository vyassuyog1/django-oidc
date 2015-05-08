from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r'^openid$', views.openid, name='openid'),
                       url(r'^openid/(?P<op_name>.+)$', views.openid, name='openid_with_op_name'),
                       url(r'^callback/?', views.authz_cb, name='openid_cb'),
                       url(r'^logout$', views.logout, name='logout'),
                       )