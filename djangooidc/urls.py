from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
                       url(r'^openid$', views.openid, name='openid'),
                       url(r'^rp/name/(?P<op_name>.+)$', views.rp, name='redirect_to_op_name'),
                       url(r'^rp/discovery$', views.rp, name='redirect_to_op_discovery'),
                       url(r'^authz_cb/?', views.authz_cb, name='authz_cb'),
                       url(r'^logout$', views.logout, name='logout'),
                       )