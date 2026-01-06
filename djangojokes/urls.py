from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    #Admin
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    #User Management
    path('jobs/', include('jobs.urls')),
    path('account/', include('users.urls')),
    #Local Apps
    path('jokes/', include('jokes.urls')),
    path('', include('pages.urls')),
    path('account/', include('allauth.urls'))
]