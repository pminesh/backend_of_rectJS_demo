"""HomeAutomation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from fcm_django.api.rest_framework import FCMDeviceViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger schema
schema_view = get_schema_view(
   openapi.Info(
      title="DEMO API",
      default_version='v2.0',
      description="DEMO API for Website, Backend & Apps",
      terms_of_service="testing.com",
      contact=openapi.Contact(email="demo@gmail.com"),
      license=openapi.License(name="DEMO"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'devices', FCMDeviceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include ([
        path('scene/',include('home_automation.scene.api_urls')),
        path('trigger/',include('home_automation.trigger.api_urls')),
        path('user/',include('home_automation.user.api_urls')),
        path('push_notification/',include('home_automation.push_notifications.api_urls')),
        path('razorpay/',include('home_automation.payment.api_urls')),
    ])),
    path('', include(router.urls)),

    # DRF DRF_YASG
    path('redoc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/api/api.json', schema_view.without_ui(cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/doc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
