from django.urls import path
from home_automation.push_notifications import views

urlpatterns = [
    path('send_notification',views.SendNotification.as_view(),name='send_notification')
]