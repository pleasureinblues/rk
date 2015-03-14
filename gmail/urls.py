from django.conf.urls import patterns, url
from gmail import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^$', views.index, name='index'),
        url(r'^(?P<fv>[\d]+)/(?P<sv>[\d]+)/$', views.sumup, name='sumup'),
        url(r'^(?P<your_name>[\w\-\s]+)/$', views.personalized_name, name='personalized_name'),
)