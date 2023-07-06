from django.shortcuts import render
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class SendNotification(APIView):
    def post(self, request, format=None):
        device_token = request.data['token']
        title = request.data['title']
        body = request.data['body']
        try:
            device = FCMDevice.objects.get(registration_id=device_token)
            device.send_message(Message(
                notification=Notification(title=title, body=body, image="url")
            ))
            return Response({'msg': 'Send push notification successfully'}, status=status.HTTP_200_OK)
        except Exception:
            return Http404