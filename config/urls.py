from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Hotel Ríos del Sur · Administración'
admin.site.site_title = 'Hotel Ríos del Sur'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('django.contrib.auth.urls')),  # login / logout
    path('', include('hotel.urls')),
]
