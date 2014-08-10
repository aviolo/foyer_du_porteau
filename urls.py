from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.static import serve
from django.utils.functional import curry

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


handler500 = curry(server_error, template_name='fdp_app.500.html')

urlpatterns = patterns('',
    url(r'^medias/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': settings.DEBUG}, name='medias'),
    url(r'^statics/(?P<path>.*)$', serve, {'document_root': settings.STATIC_URL, 'show_indexes': settings.DEBUG}, name='statics'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('fdp_app.urls')),
    # Examples:
    # url(r'^$', 'fdp_django.views.home', name='home'),
    # url(r'^fdp_django/', include('fdp_django.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
)
