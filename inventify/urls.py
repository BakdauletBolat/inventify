from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from inventify.yasg import urlpatterns as yasg_urlpatterns

urlpatterns = yasg_urlpatterns + [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('users/', include('users.urls')),
        path('', include('apps.product.urls')),
        path('car/', include('apps.car.urls')),
        path('category/', include('apps.category.urls')),
        path('stock/', include('apps.stock.urls')),
        path('orders/', include('apps.order.urls'))
    ])),
]
urlpatterns += yasg_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
