from django.conf.urls import patterns, include, url
from django.contrib import admin
import examplesite.views as exviews

urlpatterns = patterns('',
    # Examples:
    url(r'^$', exviews.index, name='index'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
)
