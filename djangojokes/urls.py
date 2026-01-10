from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import private_storage.urls
from django.conf import settings
urlpatterns = [
    #Admin
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    #User Management
    path('jobs/', include('jobs.urls')),
    path('account/', include('users.urls')),
    
    # Private media
    path('media/private/', include(private_storage.urls)),

    #Local Apps
    path('jokes/', include('jokes.urls')),
    path('', include('pages.urls')),
    path('account/', include('allauth.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns