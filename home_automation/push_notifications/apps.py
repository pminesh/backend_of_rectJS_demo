from django.apps import AppConfig


class PushNotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = __name__.rpartition('.')[0]