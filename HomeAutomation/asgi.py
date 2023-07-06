"""
ASGI config for BMS_host project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""
import os
import django
from django.core.asgi import get_asgi_application
from django.conf.urls import url
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from home_automation.dashboard.dashboard_consumer import UserDashConsumer
from home_automation.user.user_consumer import UserConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomeAutomation.settings')

# application = get_asgi_application()
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url(r'^user_dashboard/(?P<user_id>\w+)/(?P<user_type>\w+)/$', UserDashConsumer.as_asgi()),
            url(r'^user/', UserConsumer.as_asgi()),
        ])
    ),
})
