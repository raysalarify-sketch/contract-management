from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/properties/', include('properties.urls')),
    path('api/v1/contracts/', include('contracts.urls')),
    path('api/v1/insurance/', include('insurance.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
    path('api/v1/schedules/', include('schedules.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
